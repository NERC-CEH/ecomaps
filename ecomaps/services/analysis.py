from sqlalchemy.orm import subqueryload
from sqlalchemy.sql import Alias, or_
from ecomaps.model import Dataset, Analysis
from ecomaps.services.general import DatabaseService

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
                        .filter(or_(Analysis.viewable_by == user_id, Analysis.run_by == user_id)) \
                        .all()

    def get_public_analyses(self):
        """Gets all analyses that are classed as 'public' i.e. they
                aren't restricted to a particular user account"""

        with self.readonly_scope() as session:

            return session.query(Analysis) \
                        .options(subqueryload(Analysis.point_dataset)) \
                        .options(subqueryload(Analysis.coverage_datasets)) \
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