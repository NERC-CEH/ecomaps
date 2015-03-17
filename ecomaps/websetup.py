import datetime
import os
import pylons.test
from ecomaps.config.environment import load_environment
from ecomaps.model import session_scope, DatasetType, Dataset, Analysis, User, AnalysisCoverageDataset, \
    AnalysisCoverageDatasetColumn, Model
from ecomaps.model.meta import Base, Session

__author__ = 'Phil Jenkins (Tessella)'


def _get_result_image():

    example_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'example_image.txt')

    with open(example_path, 'r') as image_file:

        return image_file.read()


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
        user.first_name = 'Phil'
        user.last_name = 'Jenkins'
        user.username = 'philip.jenkins@tessella.com'
        user.email = 'philip.jenkins@tessella.com'
        user.access_level = "Admin"

        session.add(user)

        user2 = User()
        user2.name = 'Mike Wilson'
        user2.first_name = 'Mike'
        user2.last_name = 'Wilson'
        user2.username = 'mw'
        user2.email = 'mw@ceh.ac.uk'
        user2.access_level = "Admin"

        session.add(user2)

        user3 = User()
        user3.name = 'Simon Wright'
        user3.first_name = 'Simon'
        user3.last_name = 'Wright'
        user3.username = 'smw'
        user3.email = 'smw@ceh.ac.uk'
        user3.access_level = "Admin"

        session.add(user3)

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
        # CEH
        ds = Dataset()
        ds.dataset_type = coverDst
        ds.wms_url = 'http://thredds.ceh.ac.uk/thredds/wms/EcoMapsLCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds.name = 'Land Cover Map 2007'
        ds.netcdf_url = 'http://thredds.ceh.ac.uk/thredds/dodsC/EcoMapsLCM2007_25mAggregation/DetailWholeDataset.ncml'
        ds.low_res_url = 'http://thredds.ceh.ac.uk/thredds/fileServer/EcoMapsLCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc'
        session.add(ds)

        # Model that provides the interface to the R code
        model = Model()
        model.name = "LCM Thredds Model"
        model.id = 1
        model.description = "LCM Thredds model written in R"
        model.code_path = "code_root"
        session.add(model)

        # Sample CS points
        # CEH
        ds3 = Dataset()
        ds3.dataset_type = pointDst
        ds3.wms_url = 'http://thredds.ceh.ac.uk/thredds/wms/EcoMapsPoints/Detail/ECOMAPSInputLOI01.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds3.netcdf_url = 'http://thredds.ceh.ac.uk/thredds/dodsC/EcoMapsPoints/Detail/ECOMAPSInputLOI01.nc'
        ds3.name = 'Example Point dataset'
        session.add(ds3)

        # Sample CS 2007 points
        # CEH
        ds4 = Dataset()
        ds4.dataset_type = pointDst
        ds4.wms_url = 'http://thredds.ceh.ac.uk/thredds/wms/EcoMapsPoints/Detail/ECOMAPSInput2007LOI01.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds4.netcdf_url = 'http://thredds.ceh.ac.uk/thredds/dodsC/EcoMapsPoints/Detail/ECOMAPSInput2007LOI01.nc'
        ds4.name = 'Example Point dataset for 2007'
        session.add(ds4)



