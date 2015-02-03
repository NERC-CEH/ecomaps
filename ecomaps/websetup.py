import datetime
import os
import pylons.test
import urllib2
from xml.dom.minidom import parse
from urlparse import urljoin
from ecomaps.config.environment import load_environment
from ecomaps.model import session_scope, DatasetType, Dataset, Analysis, User, AnalysisCoverageDataset, \
    AnalysisCoverageDatasetColumn, Model
from ecomaps.model.meta import Base, Session

__author__ = 'Phil Jenkins (Tessella)'


def _get_result_image():

    example_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'example_image.txt')

    with open(example_path, 'r') as image_file:

        return image_file.read()

def registerThreddsDatasets(url, session):
    """Scan over the given url for thredds datasets. Add to the session"""
    xml = parse(urllib2.urlopen(url))
  
    for dataset in xml.getElementsByTagName('dataset'):
        if dataset.hasAttribute('urlPath'):
            # Here we should lookup the sevicename which (contained in this element)
            # and find out the services base. 
            ds = Dataset()
            #ds.dataset_type = NOT_SURE_HOW_TO_SET_THIS
            path = dataset.attributes['urlPath'].value
            ds.name = dataset.attributes['name'].value
            ds.wms_url = urljoin(url, '/thredds/wms/' + path + '?service=WMS&version=1.3.0&request=GetCapabilities')
            ds.netcdf_url = urljoin(url, '/thredds/dodsC/' + path)

            session.add(ds) # Register the dataset to the session

    # Look for any catalogRef elements on the page, scan these
    for catRef in xml.getElementsByTagName("catalogRef"):
        path = urljoin(url, catRef.attributes['xlink:href'].value)
        registerThreddsDatasets(path, session)

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

        pointDst = DatasetType()
        pointDst.type = 'Point'

        coverDst = DatasetType()
        coverDst.type = 'Coverage'

        resultDst = DatasetType()
        resultDst.type = 'Result'

        session.add(pointDst)
        session.add(coverDst)
        session.add(resultDst)

        # Populate from thredds
        registerThreddsDatasets('http://thredds.ceh.ac.uk/thredds/ecomaps.xml', session)
