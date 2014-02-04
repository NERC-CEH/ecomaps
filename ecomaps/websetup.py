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

        # Additional databases for the purpose of testing the analysis configuration page
        ds1 = Dataset()
        ds1.dataset_type = coverDst
        ds1.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/cover1'
        ds1.name = 'Land Cover Map 1'

        session.add(ds1)

        ds2 = Dataset()
        ds2.dataset_type = coverDst
        ds2.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/cover2'
        ds2.name = 'Land Cover Map 2'

        session.add(ds2)

        ds3 = Dataset()
        ds3.dataset_type = pointDst
        ds3.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/point1'
        ds3.name = 'Land Point Map 1'

        session.add(ds3)

        ds4 = Dataset()
        ds4.dataset_type = pointDst
        ds4.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/point2'
        ds4.name = 'Land Point Map 2'

        session.add(ds4)
