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


