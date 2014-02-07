import base64
from contextlib import contextmanager
import tempfile
import shutil
import datetime
from threading import Thread
import os
import uuid
from ecomaps.analysis.code_root.ecomaps_analysis import EcomapsAnalysis
from ecomaps.model import Dataset

__author__ = 'Phil Jenkins (Tessella)'

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
    _manager = None

    def __init__(self, source_dir, manager=None):

        # Set up the temporary directory
        # Move this out to a config.

        self._source_dir = source_dir
        self._manager = manager

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

        analysis_thread = Thread(target=self.run, args=analysis_obj)
        analysis_thread.start()


    def run(self, analysis_obj):
        """Runs the analysis, updating the model object passed in with a result file URL and a
            PNG image (base64 encoded)
         Params:
            analysis: Ecomaps analysis model to update
        """

        with working_directory(os.path.join(os.path.dirname(__file__), self._source_dir)) as dir:

            #RUN
            analysis = EcomapsAnalysis(dir)

            file_name = "%s_%s.nc" % (analysis_obj.name, uuid.uuid4())

            # Swap the urls out for the coverage and point datasets in the analysis object
            output_file_loc, image_file_loc = analysis.run('http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc',
                         'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/LCM2007_25mAggregation/DetailWholeDataset.ncml')

            # Write the result image to
            with open(image_file_loc, "rb") as img:

                encoded_image = base64.b64encode(img.read())
                analysis_obj.result_image = encoded_image

            # Copy the result file to the ecomaps THREDDS server
            # Set the file name to the name of the analysis + a bit of uniqueness
            shutil.copyfile(output_file_loc, os.path.join(self._netcdf_file_store, file_name))

            # Generate a WMS URL for the output file...
            wms_url = self._thredds_wms_format % file_name

            # Create a result dataset
            result_ds = Dataset()
            result_ds.name = 'Results for %s' % analysis_obj.name
            result_ds.wms_url = wms_url
            result_ds.netcdf_url = self._open_ndap_format % file_name

            # Set analysis_obj result dataset
            analysis_obj.result_dataset = result_ds

            # Done, so set the run date too
            analysis_obj.run_date = datetime.datetime.now()

            self.manager and self.manager.complete()





