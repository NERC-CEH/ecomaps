import base64
from contextlib import contextmanager
import logging
import tempfile
import shutil
import datetime
from threading import Thread
import os
import uuid
import stat
from ecomaps.analysis.code_root.ecomaps_analysis import EcomapsAnalysis
from ecomaps.model import Dataset, session_scope, Analysis

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class EcomapsAnalysisWorkingDirectory(object):
    """Encapsulates the aspects of a directory containing the ecomaps analysis"""

    _working_dir = None

    def __init__(self, working_dir):
        """Constructor for our temporary directory
            Params:
                working_dir: The directory we're going to use as our base
        """
        self._working_dir = working_dir

    @property
    def csv_folder(self):
        """The folder to store CSV data in"""
        return os.path.join(self._working_dir, "CSV")

    @property
    def r_script_folder(self):
        """The folder where the r script lives"""

        return os.path.join(self._working_dir, "R")

    @property
    def netcdf_folder(self):
        """The folder to store netCDF files in"""

        return os.path.join(self._working_dir, "netCDF")

    @property
    def image_folder(self):
        """Folder containing images"""

        return os.path.join(self._working_dir, "images")

    @property
    def root_folder(self):

        return self._working_dir


@contextmanager
def working_directory(root_dir):
    """Provides a temporary copy of a given root directory, deletes when done
        Params:
            root_dir: Root of directory to copy
    """

    try:
        temp_dir = tempfile.mkdtemp()

        working_dir = EcomapsAnalysisWorkingDirectory(os.path.join(temp_dir, 'working'))
        shutil.copytree(root_dir, working_dir.root_folder)

        # copytree() doesn't set the permissions properly on the copied files
        # so we'll have to do it manually instead
        for root, dirs, files in os.walk(working_dir.root_folder, topdown=False):
            for dir in dirs:
                os.chmod(os.path.join(root, dir), 0755)
            for file in files:
                os.chmod(os.path.join(root,file), 0755)

        yield working_dir

    finally:

        # Clean up after ourselves
        shutil.rmtree(temp_dir)

class AnalysisRunner(object):
    """Utility to run an analysis within the context of a temporary directory"""

    _source_dir = None
    _thredds_wms_format = None
    _netcdf_file_store = None
    _open_ndap_format = None
    _analysis_obj = None

    def __init__(self, source_dir):
        """ Constructs our runner
            Params:
                source_dir: Directory containing the code we want to run
        """

        # Set up the temporary directory based on the directory
        # containing the analysis code
        self._source_dir = source_dir

        # Read the config
        from ConfigParser import SafeConfigParser

        config = SafeConfigParser()
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))

        self._thredds_wms_format = config.get('thredds', 'thredds_wms_format')
        self._netcdf_file_store = config.get('thredds', 'netcdf_file_location')
        self._open_ndap_format = config.get('thredds', 'open_ndap_format')

    def run_async(self, analysis_obj):
        """Runs the analysis asynchonously
            Params:
                analysis_obj: The ecomaps analysis object
        """

        analysis_thread = Thread(target=self.run, kwargs={'analysis_obj':analysis_obj})
        analysis_thread.start()


    def run(self, analysis_obj):
        """Runs the analysis, updating the model object passed in with a result file URL and a
            PNG image (base64 encoded)
         Params:
            analysis: Ecomaps analysis model to update
        """

        self._analysis_obj = analysis_obj

        with working_directory(os.path.join(os.path.dirname(__file__), self._source_dir)) as dir:

            log.debug("Analysis for %s has started" % self._analysis_obj.name)

            #RUN
            analysis = EcomapsAnalysis(dir)

            file_name = "%s_%s.nc" % (self._analysis_obj.name.replace(' ', '-'), str(datetime.datetime.now().isoformat()).replace(':', '-'))

            coverage_dict = {}

            for ds in analysis_obj.coverage_datasets:
                coverage_dict[ds.dataset] = [c.column for c in ds.columns]

            # Now we have enough information to kick the analysis off
            output_file_loc, image_file_loc = analysis.run(analysis_obj.point_dataset.netcdf_url,
                                                           coverage_dict, self._update_progress)

            # Write the result image to
            with open(image_file_loc, "rb") as img:

                encoded_image = base64.b64encode(img.read())
                self._analysis_obj.result_image = encoded_image

            # Copy the result file to the ecomaps THREDDS server
            # Set the file name to the name of the analysis + a bit of uniqueness
            shutil.copyfile(output_file_loc, os.path.join(self._netcdf_file_store, file_name))

            # Generate a WMS URL for the output file...
            wms_url = self._thredds_wms_format % file_name

            # Create a result dataset
            result_ds = Dataset()
            result_ds.name = 'Results for %s' % self._analysis_obj.name
            result_ds.wms_url = wms_url

            # TODO: Can we do something nicer than the ID?
            result_ds.dataset_type_id = 3
            result_ds.netcdf_url = self._open_ndap_format % file_name

            # Tidy up the analysis object
            self._save_analysis(result_ds)
            self._update_progress('Complete', True)


    def _update_progress(self, message, complete=False):
        """Simply updates the analysis progress message
            Params:
                analysis_obj: Analysis object to update
                message: Message to use
                complete: Set to True if complete
        """

        log.debug(message)

        with session_scope() as session:

            a = session.query(Analysis).get(self._analysis_obj.id)

            a.progress_message = message
            a.complete = complete
            session.add(a)

    def _save_analysis(self, result_ds):
        """ Saves the analysis to the database
            Params:
                analysis_obj: The analysis object containing the updated fields
                result_ds: Dataset containing the results to associate with this analysis
        """
        with session_scope() as session:

            a = session.query(Analysis).get(self._analysis_obj.id)
            a.result_dataset = result_ds
            a.run_date = datetime.datetime.now()
            a.result_image = self._analysis_obj.result_image
            session.add(result_ds)
            session.add(a)