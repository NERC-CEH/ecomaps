import datetime
import pylons.test
from ecomaps.config.environment import load_environment
from ecomaps.model import session_scope, DatasetType, Dataset, Analysis, User
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

        user = User()
        user.name = 'Phil Jenkins'
        user.username = 'jenp'
        user.email = 'phil.jenkins@tessella.com'

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
        ds.netcdf_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc'

        session.add(ds)
        
        ds2 = Dataset()
        ds2.dataset_type = pointDst
        ds2.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/wms/CHESSModel001Run001OutputAggregation/DetailWholeDataset.ncml?service=WMS&version=1.3.0&request=GetCapabilities'
        ds2.name = 'Example CHESS dataset'

        session.add(ds2)
        
        a1 = Analysis()
        a1.name = "JENP's Analysis 1"
        a1.viewable_by_user = user
        a1.run_date = datetime.datetime.now()
        a1.coverage_datasets = [ds]
        a1.goodness_of_fit = 75
        a1.run_by_user = user
        a1.point_dataset = ds2

        session.add(a1)

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
