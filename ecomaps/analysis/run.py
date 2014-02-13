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

        for root, dirs, files in os.walk(working_dir.root_folder, topdown=False):
            for dir in dirs:
                os.chmod(os.path.join(root, dir), 0755)
            for file in files:
                os.chmod(os.path.join(root,file), 0755)

        yield working_dir

    finally:
        shutil.rmtree(temp_dir)

def report_progress(message):

    print message

class AnalysisRunner(object):
    """Utility to run an analysis within the context of a temporary directory"""

    _source_dir = None
    _thredds_wms_format = None
    _netcdf_file_store = None
    _open_ndap_format = None
    _analysis_obj = None

    def __init__(self, source_dir, manager=None):

        # Set up the temporary directory
        # Move this out to a config.

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

            file_name = "%s_%s.nc" % (self._analysis_obj.name, uuid.uuid4())

            # Swap the urls out for the coverage and point datasets in the analysis object
            output_file_loc, image_file_loc = analysis.run('http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc',
                         'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/LCM2007_25mAggregation/DetailWholeDataset.ncml', self._update_progress)

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
            result_ds.netcdf_url = self._open_ndap_format % file_name

            self._save_analysis(self._analysis_obj, result_ds)

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

    def _save_analysis(self, analysis_obj, result_ds):

        with session_scope() as session:

            a = session.query(Analysis).get(self._analysis_obj.id)
            a.result_dataset = result_ds
            a.run_date = datetime.datetime.now()
            session.add(a)


