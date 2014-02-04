import pylons.test
from ecomaps.config.environment import load_environment
from ecomaps.model import session_scope, DatasetType, Dataset
from ecomaps.model.meta import Base, Session

__author__ = 'Phil Jenkins (Tessella)'


def setup_app(command, conf, vars):
    """Place any commands to setup ecomaps here - currently creating db tables"""

    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    Base.metadata.drop_all(bind=Session.bind)
    Base.metadata.create_all(bind=Session.bind)

    with session_scope(Session) as session:

        pointDst = DatasetType()
        pointDst.type = 'Point'

        coverDst = DatasetType()
        coverDst.type = 'Coverage'

        resultDst = DatasetType()
        resultDst.type = 'Result'

        session.add(pointDst)
        session.add(coverDst)
        session.add(resultDst)

        # Sample land coverage map
        ds = Dataset()
        ds.dataset_type = coverDst
        ds.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/wms/LCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds.name = 'Land Cover Map 2007'

        session.add(ds)