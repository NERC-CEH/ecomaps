import threading
import unittest
import shutil
from mock import MagicMock
from ecomaps.analysis.run import AnalysisRunner
from ecomaps.model import Analysis

__author__ = 'Phil Jenkins (Tessella)'

class TestEcomapsAnalysis(unittest.TestCase):

    def test_analysis_run(self):

        test_analysis = Analysis()
        test_analysis.name = "Testing times"
        runner = AnalysisRunner('code_root')

        runner.run(test_analysis)

        self.assertNotEqual(test_analysis.result_image, None, "Expected an image to be populated")
        self.assertNotEqual(test_analysis.result_dataset, None, "Expected a result dataset to be populated")

        self.assertNotEqual(test_analysis.result_dataset.wms_url, None, "Expected the result dataset to have a WMS URL")
        self.assertNotEqual(test_analysis.result_dataset.netcdf_url, None, "Expected the result dataset to have an OPENNDAP URL")