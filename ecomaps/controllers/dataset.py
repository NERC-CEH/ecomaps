import logging
import urllib2
from pylons.decorators import jsonify
from ecomaps.lib.base import BaseController, request, render, c
from ecomaps.services.dataset import DatasetService
from ecomaps.services.netcdf import NetCdfService
from ecomaps.services.user import UserService

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class DatasetController(BaseController):

    _dataset_service = None
    _netcdf_service = None


    def __init__(self, dataset_service=DatasetService(), netcdf_service=NetCdfService(),
                 user_service=UserService()):
        """ Constructs a new dataset controller
        @param dataset_service: The dataset service to use with this controller
        @param netcdf_service: The NetCDF service to use with this controller
        @param user_service: The user service we're going to use
        """

        super(DatasetController, self).__init__()

        self._user_service = user_service
        self._dataset_service = dataset_service
        self._netcdf_service = netcdf_service

    @jsonify
    def columns(self, id):
        """ Returns a list of the variable columns for the given dataset id
        @param id: The ID of the dataset to get columns for
        """
        ds = self._dataset_service.get_dataset_by_id(id)

        if ds:
            return self._netcdf_service.get_variable_column_names(ds.netcdf_url)
        else:
            return None

    @jsonify
    def list(self):

        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])

        return self._dataset_service.get_datasets_for_user(user.id)


    def wms(self, id):
        """ Indirection layer between ecomaps and the underlying dataset mapping
        server (currently THREDDS)
            @param id - ID of the dataset containing the real URL to the data
        """

        log.debug("Request for %s" % request.query_string)
        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])
        ds = self._dataset_service.get_dataset_by_id(id, user_id=user.id)

        redirect_url = "%s?%s" % (ds.wms_url.split('?')[0], request.query_string)

        log.debug("Redirecting to %s" % redirect_url)
        return urllib2.urlopen(redirect_url).read()

    def preview(self, id):
        """ Renders a preview view of the first 10 rows of a dataset (currently point data only!)
        """

        # Need to make sure the user has access to the dataset in question
        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])
        ds = self._dataset_service.get_dataset_by_id(id, user_id = user.id)

        c.dataset_name = ds.name

        # This should contain the first 10 rows
        preview_data = self._netcdf_service.get_point_data_preview(ds.netcdf_url, 10)

        c.columns = preview_data.keys()

        # Number of rows - 1 for the row range--------------------------------------v
        c.row_set = [[preview_data[col][row] for col in c.columns] for row in range(9)]

        return render('dataset_preview.html')

    def view_datasets(self):
        """Allow admin-user to see all available datasets. If user is non-admin, redirect to page not found.
        """
        identity = request.environ.get('REMOTE_USER')

        user = self._user_service.get_user_by_username(identity)

        if user.access_level == "Admin":

            c.datasets = self._dataset_service.get_all_datasets()
            return render('all_analyses.html')

        else:

            return render('not_found.html')