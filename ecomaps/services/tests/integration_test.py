import unittest
from ecomaps.model import initialise_session, Base, Session, User, Dataset, Analysis
from ecomaps.services.analysis import AnalysisService
from ecomaps.services.dataset import DatasetService

__author__ = 'Phil Jenkins (Tessella)'


class IntegrationTests(unittest.TestCase):

    _connectionstring = 'mysql+mysqlconnector://ecomaps-admin:ecomaps@localhost/ecomaps_test'
    _user_id = None
    _another_user_id = None
    _service = None

    def __init__(self, *args, **kwargs):

        super(IntegrationTests,self).__init__(*args, **kwargs)
        initialise_session(None, manual_connection_string=self._connectionstring)

    def tearDown(self):
        """Gets rid of the tables in the connected database"""

        # Blow the model away
        Base.metadata.drop_all(bind=Session.bind)

    def setUp(self):
        """Verifies that each of the model classes derived from declarative_base can be created"""

        Base.metadata.create_all(bind=Session.bind)

        # Should be bound to the session we've set up in __init__
        self._service = DatasetService()

        user = User()
        user.name = "testing"

        another_user = User()
        another_user.name = "Someone else"

        session = Session()
        session.add(user)
        session.add(another_user)
        session.flush()

        self._user_id = user.id
        self._another_user_id = another_user.id

        session.commit()
        session.close()

    def test_get_datasets_for_user(self):

        with self._service.transaction_scope() as session:
            dataset_a = Dataset()
            dataset_a.viewable_by_user_id = self._user_id
            dataset_a.name = "Dataset1"

            session.add(dataset_a)

            dataset_b = Dataset()
            dataset_b.name = "Dataset2"

            session.add(dataset_b)

            dataset_c = Dataset()
            dataset_c.viewable_by_user_id = self._another_user_id
            dataset_c.name = "Dataset3"

            session.add(dataset_c)

        datasets = self._service.get_datasets_for_user(self._user_id)

        self.assertEqual(len(datasets), 2, "Expected 2 viewable datasets back")

    def test_get_analyses_for_user(self):

        with self._service.transaction_scope() as session:
            dataset_a = Dataset()
            dataset_a.viewable_by_user_id = self._user_id
            dataset_a.name = "Dataset1"

            session.add(dataset_a)

            dataset_b = Dataset()
            dataset_b.name = "Dataset2"

            session.add(dataset_b)

            analysis_a = Analysis()
            analysis_a.point_dataset = dataset_a
            analysis_a.coverage_datasets = [dataset_b]
            analysis_a.viewable_by = self._user_id

            analysis_b = Analysis()
            analysis_b.point_dataset = dataset_a
            analysis_b.coverage_datasets = [dataset_b]
            analysis_b.run_by = self._user_id

            analysis_c = Analysis()
            analysis_c.point_dataset = dataset_a
            analysis_c.coverage_datasets = [dataset_b]
            analysis_c.viewable_by = self._another_user_id

            session.add(analysis_a)
            session.add(analysis_b)
            session.add(analysis_c)

        analysisService = AnalysisService()
        analysis_list = analysisService.get_analyses_for_user(self._user_id)

        self.assertNotEqual(analysis_list, None, "Expected a result to be populated")
        self.assertEqual(len(analysis_list), 2, "Expected 2 analyses back")
