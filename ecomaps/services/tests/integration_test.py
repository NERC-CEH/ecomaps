import unittest
from ecomaps.model import initialise_session, Base, Session, User, Dataset, Analysis, DatasetType
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

    def _populate_session(self):

        with self._service.transaction_scope() as session:

            pointDst = DatasetType()
            pointDst.type = 'Point'

            coverDst = DatasetType()
            coverDst.type = 'Coverage'

            resultDst = DatasetType()
            resultDst.type = 'Result'

            session.add(pointDst)
            session.add(coverDst)
            session.add(resultDst)

            dataset_a = Dataset()
            dataset_a.dataset_type = pointDst
            dataset_a.viewable_by_user_id = self._user_id
            dataset_a.name = "Dataset1"

            session.add(dataset_a)

            dataset_b = Dataset()
            dataset_b.dataset_type = pointDst
            dataset_b.name = "Dataset2"

            session.add(dataset_b)

            dataset_c = Dataset()
            dataset_c.dataset_type = pointDst
            dataset_c.viewable_by_user_id = self._another_user_id
            dataset_c.name = "Dataset3"

            session.add(dataset_c)

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

        self._populate_session()

    def test_get_datasets_for_user(self):

        datasets = self._service.get_datasets_for_user(self._user_id, 1)
        self.assertEqual(len(datasets), 2, "Expected 2 viewable datasets back")

    def test_get_analyses_for_user(self):

        analysis_service = AnalysisService()
        analysis_list = analysis_service.get_analyses_for_user(self._user_id)

        self.assertNotEqual(analysis_list, None, "Expected a result to be populated")
        self.assertEqual(len(analysis_list), 2, "Expected 2 analyses back")

    def test_get_public_analyses(self):

        analysis_service = AnalysisService()
        analysis_list = analysis_service.get_public_analyses()

        self.assertNotEqual(analysis_list, None, "Expected a result to be populated")
        self.assertEqual(len(analysis_list), 1, "Expected 1 analysis back")

    def test_publish_analysis(self):

        analysis_service = AnalysisService()

        with analysis_service.readonly_scope() as session:

            analysis = session.query(Analysis).filter(Analysis.viewable_by == self._user_id).first()

        analysis_service.publish_analysis(analysis.id)

        with analysis_service.readonly_scope() as another_session:

            updated_analysis = another_session.query(Analysis).filter(Analysis.id == analysis.id).one()
            self.assertEqual(updated_analysis.viewable_by, None, "Expected viewable by field to be cleared out")