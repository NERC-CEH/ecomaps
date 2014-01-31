from ecomaps.model import Dataset
from ecomaps.services.general import DatabaseService

__author__ = 'Phil Jenkins (Tessella)'

class DatasetService(DatabaseService):
    """Encapsulates operations on Map datasets"""

    def get_datasets_for_user(self, user_id):
        """Returns a list of datasets that the supplied user has access to
            Params:
                user_id:
                    ID of the user to get a list of datasets for
        """

        with self.readonly_scope() as session:

            # Find all datasets that are viewable by this user (private)
            # or are public (null viewable_by)
            # Note SQLAlchemy wants '== None' not 'is None'
            return session.query(Dataset).filter(Dataset.viewable_by_user_id == user_id or
                                                 Dataset.viewable_by_user_id == None).all()
