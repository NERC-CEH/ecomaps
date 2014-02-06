import unittest
from ecomaps.analysis.run import AnalysisRunner
from ecomaps.model import Analysis

__author__ = 'Phil Jenkins (Tessella)'

class TestEcomapsAnalysis(unittest.TestCase):

    def test_analysis_run(self):

        pass
        test_analysis = Analysis()

        runner = AnalysisRunner('code_root')
        runner.run(test_analysis)

        self.assertNotEqual(test_analysis.result_image, None, "Expected an image to be populated")