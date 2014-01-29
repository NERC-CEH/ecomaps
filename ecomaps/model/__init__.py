from sqlalchemy import engine_from_config
from ecomaps.model.meta import Session
from contextlib import contextmanager

__author__ = 'Phil Jenkins (Tessella)'

def initialise_session(config):
    """Sets up our database engine and session
    Params
        In: config - The config object containing 'sqlalchemy.blah' items"""

    # Attach our engine to the session
    engine = engine_from_config(config, 'sqlalchemy.')
    Session.configure(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope that we can wrap around calls to the database"""

    session = Session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


