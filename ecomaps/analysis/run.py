import base64
from contextlib import contextmanager
import tempfile
import shutil
import os
from ecomaps.analysis.code_root.ecomaps_analysis import EcomapsAnalysis

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



class AnalysisRunner(object):
    """Utility to run an analysis within the context of a temporary directory"""

    _source_dir = None

    def __init__(self, source_dir):

        # Set up the temporary directory
        # Move this out to a config.

        self._source_dir = source_dir

    def run(self):

        with working_directory(os.path.join(os.path.dirname(__file__), self._source_dir)) as dir:

            #RUN
            analysis = EcomapsAnalysis(dir)
            output_file_loc, image_file_loc = analysis.run('http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc',
                         'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/LCM2007_25mAggregation/DetailWholeDataset.ncml')

            with open(image_file_loc, "rb") as img:

                encoded_image = base64.b64encode(img.read())

            # Copy the result file to the ecomaps THREDDS server
            # This'll need moving to the config!
            dest_dir = '/usr/share/tomcat6/content/thredds/public/testdata'

            shutil.copyfile(output_file_loc, os.path.join(dest_dir, 'output_test.nc'))

            p=0


if __name__ == "__main__":

    runner = AnalysisRunner('code_root')
    runner.run()




