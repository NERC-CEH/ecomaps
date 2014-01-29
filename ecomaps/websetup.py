import pylons
from ecomaps.config.environment import load_environment
from ecomaps.model.meta import Base, Session

__author__ = 'Phil Jenkins (Tessella)'


def setup_app(command, conf, vars):
    """Place any commands to setup ecomaps here - currently creating db tables"""

    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    Base.metadata.create_all(bind=Session.bind)