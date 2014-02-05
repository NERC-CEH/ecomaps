import unittest
import os
from ecomaps.analysis.run import AnalysisRunner

__author__ = 'Phil Jenkins (Tessella)'

class TestEcomapsAnalysis(unittest.TestCase):

    def test_analysis_run(self):

        runner = AnalysisRunner(os.path.join(os.path.dirname(__file__), 'code_root/'))

        runner.run()