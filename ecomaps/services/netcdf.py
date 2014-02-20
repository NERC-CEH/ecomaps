from pydap.client import open_url

__author__ = 'Phil Jenkins (Tessella)'


class EcoMapsNetCdfFile(object):

    attributes = {}

    columns = []

    def __init__(self, url):
        """ Constructor, reads in a file from the url provided
        @param url: OpenNDAP url for the NetCDF file
        """

        # Let's open the file using OpenNDAP
        f = open_url(url)

        # Pull out the attributes, and column names
        self.attributes = f.attributes['NC_GLOBAL']
        self.columns = f.keys()

class NetCdfService(object):
    """ Provides operations to read elements of NetCDF files stored in our assoicated THREDDS server
    """

    def get_attributes(self, netcdf_url, column_filter=None):
        """Gets a dictionary of attributes stored on the file, optionally filtered
            by a list of column names
            @param netcdf_url: OpenNDAP url for the NetCDF file
            @param column_filter: Optional list of attribute names to return

            @returns Dictionary of attribute name/value pairs
        """

        ds = EcoMapsNetCdfFile(netcdf_url)

        if column_filter:
            return dict([(key, ds.attributes[key]) for key in column_filter if key in ds.attributes])
        else:
            return ds.attributes

    def get_variable_column_names(self, netcdf_url):
        """ Gets a list of column names that are part of a particular dataset, but
            not the standard column names (x, y, transverse_mercator)
        """

        ds = EcoMapsNetCdfFile(netcdf_url)

        columns_to_ignore = ['x', 'y', 'transverse_mercator', 'time']

        return [col for col in ds.columns if col not in columns_to_ignore]