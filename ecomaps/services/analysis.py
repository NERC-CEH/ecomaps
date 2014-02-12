import datetime
from random import randint
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import Alias, or_
from ecomaps import websetup
from ecomaps.model import Dataset, Analysis
from ecomaps.services.general import DatabaseService
from ecomaps.model import AnalysisCoverageDataset

__author__ = 'Phil Jenkins (Tessella)'


class AnalysisService(DatabaseService):
    """Provides operations on Analysis objects"""

    def get_analyses_for_user(self, user_id):
        """Gets a list of analyses for the given user
            Params:
                user_id: Get analyses for the user with this ID
        """

        with self.readonly_scope() as session:

            return session.query(Analysis) \
                        .options(subqueryload(Analysis.point_dataset)) \
                        .options(subqueryload(Analysis.coverage_datasets)) \
                        .options(subqueryload(Analysis.run_by_user)) \
                        .filter(or_(Analysis.viewable_by == user_id, Analysis.run_by == user_id)) \
                        .all()

    def get_public_analyses(self):
        """Gets all analyses that are classed as 'public' i.e. they
                aren't restricted to a particular user account"""

        with self.readonly_scope() as session:

            return session.query(Analysis) \
                        .options(subqueryload(Analysis.point_dataset)) \
                        .options(subqueryload(Analysis.coverage_datasets)) \
                        .options(subqueryload(Analysis.run_by_user)) \
                        .filter(Analysis.viewable_by == None) \
                        .all()

    def publish_analysis(self, analysis_id):
        """Publishes the analysis with the supplied ID
            Params:
                analysis_id: ID of the analysis to publish
        """

        with self.transaction_scope() as session:

            analysis = session.query(Analysis).filter(Analysis.id == analysis_id).one()

            # Now update the "viewable by" field - setting to None
            # infers that the analysis is published
            analysis.viewable_by = None
            analysis.result_dataset.viewable_by_user_id = None

    def get_analysis_by_id(self, analysis_id, user_id):
        """Returns a single analysis with the given ID
            Params:
                analysis_id - ID of the analysis to look for
        """

        with self.readonly_scope() as session:

            try:

                return session.query(Analysis).filter(Analysis.id == analysis_id,
                                              or_(or_(Analysis.viewable_by == user_id,
                                                      Analysis.viewable_by == None),
                                                  Analysis.run_by == user_id)).one()

            except NoResultFound:
                return None


    def create(self, name, point_dataset_id, coverage_dataset_ids, user_id, parameters):
        """Creates a new analysis object
            Params:
                name - Friendly name for the analysis
                point_dataset_id - Id of dataset containing point data
                coverage_dataset_ids - List of coverage dataset ids
                user_id - Who is creating this analysis?
                parameters - Extra parameters to pass to the model code
        """

        with self.transaction_scope() as session:

            analysis = Analysis()
            analysis.name = name
            analysis.run_by = user_id
            analysis.viewable_by = user_id
            analysis.point_data_dataset_id = int(point_dataset_id)

            # Putting this in for testing purposes only!
            analysis.run_date = datetime.datetime.now()
            analysis.result_image = websetup._get_result_image()
            analysis.goodness_of_fit = randint(50, 100)

            result_dataset = Dataset()
            result_dataset.dataset_type_id = 3
            result_dataset.name = "Results for %s" % analysis.name
            result_dataset.viewable_by_user_id = user_id

            analysis.result_dataset = result_dataset

            # End of temporary test code

            coverage_datasets = AnalysisCoverageDataset()

            for id in coverage_dataset_ids:
                id_as_int = int(id)
                coverage_datasets.dataset_id = id_as_int
                analysis.coverage_datasets.append(coverage_datasets)

            session.add(analysis)
            session.flush([analysis])
            session.refresh(analysis)


            return analysis.id