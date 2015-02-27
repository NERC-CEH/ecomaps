import datetime
import os
import pylons.test
import urllib2
from itertools import groupby
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

def registerThreddsDatasets(url, types, session):
    """Scan over the given url for thredds datasets. Add to the session"""
    xml = parse(urllib2.urlopen(url))
  
    for dataset in xml.getElementsByTagName('dataset'):
        if dataset.hasAttribute('urlPath'):
            # Here we should lookup the sevicename which (contained in this element)
            # and find out the services base. 
            ds = Dataset()
            ds.dataset_type = types['GRID'] # Set to GRID type by default

            # See if a dataType has been defined for this dataset. If so, look 
            # it up
            dataTypes = dataset.getElementsByTagName('dataType')
            if dataTypes.length == 1:
                ds.dataset_type = types[dataTypes[0].firstChild.nodeValue]

            path = dataset.attributes['urlPath'].value
            ds.name = dataset.attributes['name'].value
            ds.wms_url = urljoin(url, '/thredds/wms/' + path + '?service=WMS&version=1.3.0&request=GetCapabilities')
            ds.netcdf_url = urljoin(url, '/thredds/dodsC/' + path)

            session.add(ds) # Register the dataset to the session

    # Group sibling catalogRefs together. If any of these have an aggregation we will scan them
    # otherwise just scan all of the catalogueRegs
    catalogRefs = xml.getElementsByTagName("catalogRef")
    for key, group in groupby(catalogRefs, lambda e: e.parentNode):
      groupList = list(group)
      aggregations = filter(lambda x: x.attributes['xlink:title'].value.lower().endswith('aggregation'), groupList)
    
      scan = aggregations if len(aggregations) > 0 else groupList # Were there any aggregations?
      
      for catRef in scan:
        path = urljoin(url, catRef.attributes['xlink:href'].value)
        registerThreddsDatasets(path, types, session)

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

        # Model that provides the interface to the R code
        model = Model()
        model.name = "LCM Thredds Model"
        model.id = 1
        model.description = "LCM Thredds model written in R"
        model.code_path = "code_root"

        session.add(model)

        pointDst = DatasetType()
        pointDst.type = 'Point'

        coverDst = DatasetType()
        coverDst.type = 'Coverage'

        resultDst = DatasetType()
        resultDst.type = 'Result'

        session.add(pointDst)
        session.add(coverDst)
        session.add(resultDst)

        # Define a datasetType lookup. This will conver the possible thredds 
        # datasets into their EcoMaps equivalents.
        datasetTypes = {
            "GRID": coverDst,
            "POINT": pointDst
        }

        # Populate from thredds
        registerThreddsDatasets('http://thredds.ceh.ac.uk/thredds/ecomaps.xml', datasetTypes, session)
