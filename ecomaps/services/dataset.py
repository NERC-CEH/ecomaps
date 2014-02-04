from sqlalchemy import or_
from ecomaps.model import Dataset, DatasetType
from ecomaps.services.general import DatabaseService

__author__ = 'Phil Jenkins (Tessella)'

class DatasetService(DatabaseService):
    """Encapsulates operations on Map datasets"""

    def get_datasets_for_user(self, user_id, dataset_type=None, dataset_type_id=None):
        """Returns a list of datasets that the supplied user has access to,
            and is of a particular type. This can be specified as either an ID
            or a name, depending on which is more convenient

            Params:
                user_id: ID of the user to get a list of datasets for
                dataset_type: String name of the dataset type
                dataset_type_id: ID of the dataset type
        """

        with self.readonly_scope() as session:

            # Find all datasets that are viewable by this user (private)
            # or are public (null viewable_by)
            # Note SQLAlchemy wants '== None' not 'is None'

            if dataset_type_id is None:
                return session.query(Dataset).join(DatasetType).filter(DatasetType.type == dataset_type, or_(Dataset.viewable_by_user_id == user_id,
                                                 Dataset.viewable_by_user_id == None)).all()
            else:
                return session.query(Dataset).filter(Dataset.dataset_type_id == dataset_type_id, or_(Dataset.viewable_by_user_id == user_id,
                                                 Dataset.viewable_by_user_id == None)).all()



    def get_dataset_types(self):
        """Returns all of the dataset types in the system"""

        with self.readonly_scope() as session:

            return session.query(DatasetType).all()

    def get_dataset_by_id(self, dataset_id):
        """ Returns a single dataset with the given ID
            Params:
                dataset_id: ID of the dataset to look for
        """

        with self.readonly_scope() as session:
                return session.query(Dataset).filter(Dataset.id == dataset_id).one()