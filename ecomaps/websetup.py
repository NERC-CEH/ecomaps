import datetime
import os
import pylons.test
from ecomaps.config.environment import load_environment
from ecomaps.model import session_scope, DatasetType, Dataset, Analysis, User, AnalysisCoverageDataset, \
    AnalysisCoverageDatasetColumn
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
        user.username = 'philip.jenkins@tessella.com'
        user.email = 'philip.jenkins@tessella.com'
        user.access_level = "Admin"

        user2 = User()
        user2.name = 'Someone else'
        user2.username = 'someone.else@tessella.com'
        user2.email = 'someone.else@tessella.com'

        session.add(user)
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

        # Sample land coverage map

        # CEH
        ds = Dataset()
        ds.dataset_type = coverDst
        ds.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/wms/LCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds.name = 'Land Cover Map 2007'
        ds.netcdf_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/LCM2007_25mAggregation/DetailWholeDataset.ncml'
        ds.low_res_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/fileServer/LCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc'

        # LOCAL
        # ds = Dataset()
        # ds.dataset_type = coverDst
        # ds.wms_url = 'http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        # ds.name = 'Land Cover Map 2007'
        # ds.netcdf_url = 'http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc'
        # ds.low_res_url = 'http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc'

        session.add(ds)

        # CEH
        ds2 = Dataset()
        ds2.dataset_type = pointDst
        ds2.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds2.netcdf_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc'
        ds2.name = 'Example Point dataset'

        # LOCAL
        # ds2 = Dataset()
        # ds2.dataset_type = pointDst
        # ds2.wms_url = 'http://localhost:8080/thredds/dodsC/testAll/ECOMAPSInputLOI01.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        # ds2.netcdf_url = 'http://localhost:8080/thredds/dodsC/testAll/ECOMAPSInputLOI01.nc'
        # ds2.name = 'Example Point dataset'

        session.add(ds2)

        return

        ds3 = Dataset()
        ds3.dataset_type = resultDst
        ds3.name = 'Results Dataset 1'
        ds3.netcdf_url = 'http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc'
        
        a1 = Analysis()
        a1.name = "JENP's Analysis 1"
        a1.viewable_by_user = user
        a1.run_by = user
        a1.run_date = datetime.datetime.now()
        a1.result_image = _get_result_image()
        a1.result_dataset = ds3
        a1.progress_message = "Testing the progress message"
        a1.complete = True


        # Adding a coverage dataset

        # 1. Create the link object
        cds = AnalysisCoverageDataset()

        # 2. Either assign the dataset directly
        cds.dataset = ds

        col = AnalysisCoverageDatasetColumn()
        col.column = 'LandCover'
        cds.columns.append(col)

        # 3. Or just use the dataset ID
        # cds.dataset_id = 1

        # 4. Add to the analyses' collection
        a1.coverage_datasets.append(cds)
        a1.goodness_of_fit = 75
        a1.run_by_user = user
        a1.point_dataset = ds2

        session.add(a1)

        cds_a2 = AnalysisCoverageDataset()

        # 2. Either assign the dataset directly
        cds_a2.dataset = ds

        a2 = Analysis()
        a2.name = "Example public analysis"
        a2.run_date = datetime.datetime.now()
        a2.run_by_user = user
        a2.result_image = _get_result_image()
        a2.coverage_datasets.append(cds_a2)
        a2.goodness_of_fit = 60
        a2.point_dataset = ds2
        a2.result_dataset = ds3

        session.add(a2)

        cds_a3 = AnalysisCoverageDataset()

        # 2. Either assign the dataset directly
        cds_a3.dataset = ds

        a3 = Analysis()
        a3.name = "Example public analysis 2"
        a3.run_date = datetime.datetime.now()
        a3.run_by_user = user2
        a3.result_image = _get_result_image()
        a3.coverage_datasets.append(cds_a3)
        a3.goodness_of_fit = 60
        a3.point_dataset = ds2
        a3.result_dataset = ds3

        session.add(a3)

        cds_a4 = AnalysisCoverageDataset()

        # 2. Either assign the dataset directly
        cds_a4.dataset = ds

        a4 = Analysis()
        a4.name = "Example private analysis - someone else"
        a4.run_date = datetime.datetime.now()
        a4.run_by_user = user2
        a4.viewable_by_user = user2
        a4.result_image = _get_result_image()
        a4.coverage_datasets.append(cds_a4)
        a4.goodness_of_fit = 60
        a4.point_dataset = ds2
        a4.result_dataset = ds3

        session.add(a4)

        # Additional databases for the purpose of testing the analysis configuration page
        #ds4 = Dataset()
        #ds4.dataset_type = coverDst
        #ds4.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/cover1'
        #ds4.name = 'Chess Example'
        #ds4.netcdf_url = 'http://localhost:8080/thredds/dodsC/testAll/CHESS_MODEL001_RUN001_OUT_precip_1971-01.nc'

        #session.add(ds4)

        #ds5 = Dataset()
        #ds5.dataset_type = coverDst
        #ds5.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/cover2'
        #ds5.name = 'Land Cover Map 2'
        #ds5.netcdf_url = 'http://localhost:8080/thredds/dodsC/testAll/LCM2007_GB_1K_DOM_TAR.nc'

        #session.add(ds5)

        ds6 = Dataset()
        ds6.dataset_type = pointDst
        ds6.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc?service=WMS&version=1.3.0&request=GetCapabilities'
        ds6.netcdf_url = 'http://thredds-prod.nerc-lancaster.ac.uk/thredds/dodsC/ECOMAPSDetail/ECOMAPSInputLOI01.nc'
        ds6.name = 'Example Point dataset 2'

        session.add(ds6)

        ds7 = Dataset()
        ds7.dataset_type = pointDst
        ds7.wms_url = 'http://thredds-prod.nerc-lancaster.ac.uk/point2'
        ds7.name = 'Land Point Map 2'

        session.add(ds7)

        #cds2 = AnalysisCoverageDataset()
        #cds2.dataset = ds4

        #cds3 = AnalysisCoverageDataset()
        #cds3.dataset = ds5

        #a5 = Analysis()
        #a5.name = "Private Analysis - multiple coverage datasets"
        #a5.run_date = datetime.datetime.now()
        #a5.run_by_user = user
        #a5.viewable_by_user = user
        #a5.result_image = _get_result_image()
        #a5.coverage_datasets.append(cds2)
        #a5.coverage_datasets.append(cds3)
        #a5.goodness_of_fit = 81
        #a5.point_dataset = ds7
        #a5.result_dataset = ds3
        #a5.complete = True
        #a5.year = '1997'
        #a5.random_group = 'SERIES_NUM'
        #a5.model_variable = 'loi'
        #a5.data_type = 'CONT'

        #session.add(a5)

        cds2 = AnalysisCoverageDataset()
        cds2.dataset = ds4

        cds3 = AnalysisCoverageDataset()
        cds3.dataset = ds5

        a5 = Analysis()
        a5.name = "Private Analysis - multiple coverage datasets"
        a5.run_date = datetime.datetime.now()
        a5.run_by_user = user
        a5.viewable_by_user = user
        a5.result_image = _get_result_image()
        a5.coverage_datasets.append(cds2)
        a5.coverage_datasets.append(cds3)
        a5.goodness_of_fit = 81
        a5.point_dataset = ds7
        a5.result_dataset = ds3
        a5.complete = True
        a5.unit_of_time = 'year'
        a5.random_group = 'SERIES_NUM'
        a5.model_variable = 'loi'
        a5.data_type = 'CONT'

        session.add(a5)

