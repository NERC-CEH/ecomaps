from pylons.decorators import jsonify
from ecomaps.lib.base import BaseController
from ecomaps.services.dataset import DatasetService
from ecomaps.services.netcdf import NetCdfService

__author__ = 'Phil Jenkins (Tessella)'



class DatasetController(BaseController):

    _dataset_service = None
    _netcdf_service = None


    def __init__(self, dataset_service=DatasetService(), netcdf_service=NetCdfService()):
        """ Constructs a new dataset controller
        @param dataset_service: The dataset service to use with this controller
        @param netcdf_service: The NetCDF service to use with this controller
        """

        super(BaseController, self).__init__()

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