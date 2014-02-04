from sqlalchemy import engine_from_config, Column, Integer, String, ForeignKey, Table, DateTime, create_engine
from sqlalchemy.orm import relationship
from ecomaps.model.meta import Session, Base
from contextlib import contextmanager

__author__ = 'Phil Jenkins (Tessella)'

def initialise_session(config, manual_connection_string=None):
    """Sets up our database engine and session
    Params
        In: config - The config object containing 'sqlalchemy.blah' items"""

    # Attach our engine to the session, either from the config file or
    # using a supplied string
    if manual_connection_string:
        engine = create_engine(manual_connection_string)
    else:
        engine = engine_from_config(config, 'sqlalchemy.')

    Session.configure(bind=engine)

@contextmanager
def session_scope(session_class):
    """Provide a transactional scope that we can wrap around calls to the database"""

    session = session_class()

    try:
        # Give this session back to the 'with' block
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


## Model definitions below ##

class User(Base):
    """A user of the Ecomaps system"""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(255))
    name = Column(String(50))

    def __repr__(self):
        """String representation of the user"""

        return "<User(username=%s, name=%s)>" % (self.username, self.name)

class DatasetType(Base):
    """Used to distinguish between the different types of map dataset we're dealing with"""

    __tablename__ = 'dataset_types'

    id = Column(Integer, primary_key=True)
    type = Column(String(30))

    def __repr__(self):
        """String representation of the dataset type"""

        return "<DatasetType(type=%s)>" % self.type

## Many-to-many relationship between an analysis and coverage datasets
analysis_coverage_datasets = Table(
    'analysis_coverage_datasets',
    Base.metadata,
    Column('dataset_id', Integer, ForeignKey('datasets.id')),
    Column('analysis_id', Integer, ForeignKey('analyses.id')))

class Dataset(Base):
    """Metadata around a map dataset"""

    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    wms_url = Column(String(255))
    netcdf_url = Column(String(255))
    dataset_type_id = Column(Integer, ForeignKey('dataset_types.id'))
    viewable_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    dataset_type = relationship("DatasetType", backref="datasets")

    def __repr__(self):
        """String representation of the Dataset class"""

        return "<Dataset(name=%s, wms_url=%s, netcdf_url=%s, dataset_type_id=%s)>" \
            % (
                self.name,
                self.wms_url,
                self.netcdf_url,
                self.dataset_type_id
            )

class Model(Base):
    """Represents the calculation model used by an Ecomaps analysis"""

    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(String(500))
    code_path = Column(String(500))

    def __repr__(self):
        """String representation of the model"""

        return "<Model(name=%s, description=%s)>" % (self.name, self.description)

class Analysis(Base):
    """A running of the model, stores setup and result information in the same entity"""

    __tablename__ = 'analyses'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    point_data_dataset_id = Column(Integer, ForeignKey('datasets.id'))
    run_date = Column(DateTime)
    run_by = Column(Integer, ForeignKey('users.id'))
    result_dataset_id = Column(Integer, ForeignKey('datasets.id'))
    viewable_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    model_id = Column(Integer, ForeignKey('models.id'))
    goodness_of_fit = Column(Integer)

    # FK Relationships
    run_by_user = relationship("User", foreign_keys=[run_by])
    point_dataset = relationship("Dataset", foreign_keys=[point_data_dataset_id])
    result_dataset = relationship("Dataset", foreign_keys=[result_dataset_id])
    viewable_by_user = relationship("User", foreign_keys=[viewable_by])
    model = relationship("Model")

    # M2M for coverage datasets
    coverage_datasets = relationship("Dataset",
                                     secondary='analysis_coverage_datasets')

    def __repr__(self):
        """String representation of the analysis"""

        return "<Analysis(name=%s, run_date=%s, run_by=%s)>" % (self.name, self.run_date, self.run_by)

