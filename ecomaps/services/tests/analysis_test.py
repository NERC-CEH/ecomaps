from mock import MagicMock, ANY
from ecomaps.model import Analysis
from ecomaps.services.tests.base import BaseTest
from ecomaps.services.analysis import AnalysisService

__author__ = 'Chirag Mistry (Tessella)'

class AnalysisServiceTest(BaseTest):

    def test_create_analysis(self):
        # Important - don't instantiate the mock class,
        # as the session creation function in the service
        # will do that for us

        sample_analysis = Analysis()
        sample_analysis.name = 'Test User'
        sample_analysis.user_id  = 1
        sample_analysis.point_data_dataset_id = 2
        sample_analysis.coverage_dataset_ids = [1,3]
        sample_analysis.parameters = []

        self._mock_session.add = MagicMock()
        self._mock_session.commit = MagicMock()

        analysis_service = AnalysisService(self._mock_session)
        analysis_service.create(sample_analysis.name,
                                sample_analysis.point_data_dataset_id,
                                sample_analysis.coverage_dataset_ids,
                                sample_analysis.user_id,
                                sample_analysis.parameters)

        self._mock_session.add.assert_called_once_with(ANY)
        self._mock_session.commit.assert_called_once_with()