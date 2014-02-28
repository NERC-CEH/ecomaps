from geopandas import GeoDataFrame, GeoSeries
from pydap.client import open_url
from shapely.geometry import Point

__author__ = 'Phil Jenkins (Tessella)'


class EcoMapsNetCdfFile(object):

    attributes = {}
    columns = []
    url = None

    def __init__(self, url):
        """ Constructor, reads in a file from the url provided
        @param url: OpenNDAP url for the NetCDF file
        """

        self.url = url

        # Let's open the file using OpenNDAP
        f = open_url(url)

        # Pull out the attributes, and column names
        self.attributes = f.attributes['NC_GLOBAL']
        self.columns = f.keys()
        del f

    def get_preview_data(self, no_of_rows):
        """ Gets a data structure containing the first ten rows of a given point dataset

            @param no_of_rows: Restrict to a particular number of rows
        """

        points = open_url(self.url)
        column_dictionary = {}
        for column in points.keys():

            if points[column].shape:

                ##column_dictionary[column.upper()] = points[column][:]
                # Data may have been created on a machine with a different byte order to the one on which you are running
                # Python.  To deal with this issue should convert to the native system byte order BEFORE passing it to a
                # Series/DataFrame/Panel constructor.
                # see:  http://pandas.pydata.org/pandas-docs/dev/gotchas.html#byte-ordering-issues
                column_dictionary[column] = points[column][:no_of_rows].byteswap().newbyteorder()

        return column_dictionary

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


    def get_point_data_preview(self, netcdf_url, no_of_rows=10):
        """ Gets a 2D preview of the point dataset at the given NetCDF url
            @param netcdf_url: URL to the point dataset
        """

        ds = EcoMapsNetCdfFile(netcdf_url)

        return ds.get_preview_data(no_of_rows)
