import logging
import os
import threading
import unittest
import shutil
from mock import MagicMock
import sys
from ecomaps.analysis.code_root.ecomaps_analysis import EcomapsAnalysis
from ecomaps.analysis.run import AnalysisRunner, working_directory
from ecomaps.model import Analysis, Dataset

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class TestEcomapsAnalysis(unittest.TestCase):

    def test_analysis_run(self):
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG)
        log.setLevel(logging.DEBUG)
        try:

            #log.basicConfig(stream=sys.stderr)

            log.addHandler(handler)
            with working_directory(os.path.join(os.path.dirname(__file__), '../code_root')) as dir:

                coverage_ds = Dataset()
                coverage_ds.netcdf_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/LCM2007_25mAggregation/DetailWholeDataset.ncml'
                coverage_ds.low_res_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/fileServer/LCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc'

                def progress(msg):

                    log.debug(msg)

                coverage_dict = {
                    coverage_ds: ['LandCover']
                }

                analysis = EcomapsAnalysis(dir, 'Test User', 'test@test.com')
                analysis.run(point_url='http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc',
                             coverage_dict=coverage_dict,
                             progress_fn=progress)
        finally:
            log.removeHandler(handler)
        # Remove me to test analysis code
        return
