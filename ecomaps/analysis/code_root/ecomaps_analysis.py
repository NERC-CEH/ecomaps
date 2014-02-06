import logging
import os
from pandas import DataFrame
from pydap.client import open_url
import time
import pyper
import sys

__author__ = 'Phil Jenkins (Tessella)'

#log = logging.getLogger(__name__)

#  How to check if a list, tuple or dictionary is empty in Python
#  From: http://www.pythoncentral.io/how-to-check-if-a-list-tuple-or-dictionary-is-empty-in-python/
def is_empty(any_structure):
    if any_structure:
        #print 'Structure is not empty.'
        return False
    else:
        #print 'Structure is empty.'
        return True

class EcomapsAnalysis(object):
    """Runs the ecomaps R code"""

    _working_dir = None

    def __init__(self, working_dir):
        """Constructor:
            Params:
                working_dir: The directory we're running the code from
        """

        self._working_dir = working_dir

    def _open_sample_opendap(self, url):
        print '\n\nurl:\t{0}'.format(url)
        messages = False
        #  Create points OPeNDAP object
        points = open_url(url)
        if messages:
            print '\n\n', type(points)
            print points.keys()
        #  Create dictionary containing data columns from OPeNDAP
        column_list = []
        column_dictionary = {}
        for column in points.keys():
            if messages:
                print '\tcolumn:\t{0}'.format(column)
                print '\t\tpoints[column].shape:\t{0}'.format(points[column].shape)
            if not is_empty(points[column].shape):
                if messages:
                    print '\t\tAdding column to column_list...'
                ##column_list.append(column.upper())
                column_list.append(column)
                if messages:
                    print '\t\tAdding column to column_dictionary...'
                ##column_dictionary[column.upper()] = points[column][:]
                # Data may have been created on a machine with a different byte order to the one on which you are running
                # Python.  To deal with this issue should convert to the native system byte order BEFORE passing it to a
                # Series/DataFrame/Panel constructor.
                # see:  http://pandas.pydata.org/pandas-docs/dev/gotchas.html#byte-ordering-issues
                column_dictionary[column] = points[column][:].byteswap().newbyteorder()
        #  Create pandas data frame from dictionary
        df = DataFrame(column_dictionary)
        print df
        print type(df)
        #  Re-order column order of data frame using column list generated when points OPeNDAP accessed
        df = df[column_list]
        if messages:
            print '\n'
            print df
            print
            print df.info()
            print
            print df.describe()
            print
            ##print df.to_string()
            ##print df.iloc[:10].to_string()
            ##print df.iloc[-10:].to_string()
            print df.head(10)
            print
            print df.tail(10)
        return df

    def _get_coordinate_lists(self, url):
        print '\n\naggregationurl:\t{0}'.format(url)
        messages = False
        # Create aggregation OPeNDAP object
        aggregation = open_url(url)
        if messages:
            print '\n\n', type(aggregation)
            print aggregation.keys()
        # Set north and east dimensions
        north = aggregation['y']
        if messages:
            print '\n\n', type(north)
            print north.dimensions
            print north.shape
            print north[:]
        east = aggregation['x']
        if messages:
            print type(east)
            print east.dimensions
            print east.shape
            print east[:]
        # Convert north and east dimensions to lists
        north_list = list(north[:])
        if messages:
            print '\n\n', type(north_list)
            print len(north_list)
        east_list = list(east[:])
        if messages:
            print type(east_list)
            print len(east_list)
        # Delete north and east dimension objects
        del north, east
        # Delete aggregation object
        del aggregation
        return north_list, east_list

    def _get_landcover_array(self, url):
        print '\n\naggregationurl:\t{0}'.format(url)
        messages = False
        # Create aggregation OPeNDAP object
        aggregation = open_url(url)
        if messages:
            print type(aggregation)
            print aggregation.keys()
        #  Get Land Cover data as numpy array
        data = aggregation['LandCover']
        if messages:
            print type(data)
            print data.dimensions
            print data.shape
        #  Delete aggregation object
        del aggregation
        return data

    def _sample_intersect(self, north_list, east_list, dataframe, array):
        messages = False
        if messages:
            print north_list
            print east_list
            print dataframe
            print array
        # Add new column to data frame to store land cover
        dataframe['LandCover'] = -9999
        if messages:
            print '\n\n', dataframe.head(10)
            print
            print dataframe.tail(10)
        print '\n\nLooping...'
        loopcount = 0
        #pb = ProgressBar(len(dataframe), '*')
        for count, row in dataframe.iterrows():
        ##for count, row in thing.head(10).iterrows():
            loopcount += 1
            ##if count == 0:
            ##    sys.stdout.write('Looping')
            ##    sys.stdout.flush()
            ##if count % 100 == 0:
            ##    sys.stdout.write('.')
            ##    sys.stdout.flush()
            ##if count % 200 == 0:
            if count % int(dataframe.shape[0] / 20) == 0:
                #pb.progress(loopcount)
                pass
            if messages:
                print '\t{0:-4d}\tREP_ID:\t{1:10s}\tyear:\t{2:4d}'.format(count, row['REP_ID'], row['year'])
            northing = dataframe.northing[count]
            easting = dataframe.easting[count]
            if messages:
                rep_id = dataframe.REP_ID[count]
                print '\t\trep_id:\t{0}'.format(rep_id)
                rep_plot = dataframe.REP_PLOT[count]
                print '\t\trep_plot:\t{0}'.format(rep_plot)
                year = dataframe.year[count]
                print '\t\tyear:\t{0}'.format(year)
                print '\t\tx:\t{0}'.format(northing)
                print '\t\ty:\t{0}'.format(easting)
            #   Select closest grid point centre northing
            closest_north = min(north_list, key=lambda x:abs(x - northing))
            ypixel = north_list.index(closest_north)
            if messages:
                print '\t\tclosest_north:\t{0}'.format(closest_north)
                print '\t\typixel:\t\t\t{0}'.format(ypixel)
                print '\t\tnorth_list[ypixel]:\t{0}'.format(north_list[ypixel])
            #  Select close grid point centre easting
            closest_east = min(east_list, key=lambda x:abs(x - easting))
            xpixel = east_list.index(closest_east)
            if messages:
                print '\t\tclosest_east:\t{0}'.format(closest_east)
                print '\t\txpixel:\t\t\t{0}'.format(xpixel)
                print '\t\teast_list[xpixel]:\t{0}'.format(east_list[xpixel])
            #  Get Land Cover class for selected pixel
            if messages:
                print '\t\tdata.LandCover[ypixel, xpixel]:\t{0}'.format(array.LandCover[ypixel, xpixel])
            dataframe.loc[count, 'LandCover'] = int(array.LandCover[ypixel, xpixel])
        #pb.progress(len(points_df))
        print 'Looped.'
        print '\tloopcount:\t{0}'.format(loopcount)
        return dataframe

    def _data_frame_to_csv(self, dataframe, csv):
        # Output data frame as csv file
        print '\n\noutcsv:\t{0}'.format(csv)
        if os.path.exists(csv):
            os.remove(csv)
        dataframe.to_csv(csv, index=True, sep=',', na_rep='NA', header=True, mode='w', index_label='Count')

    def _run_r_script(self, script):
        messages = True
        if messages:
            print '\n\nR script:\t\t{0}'.format(script)
            print '\tFile last modified:\t{0}'.format(time.asctime(time.localtime(os.stat(script).st_mtime)))
        command = 'source(\'' + script + '\')'
        if messages:
            print 'command:\t{0}'.format(command)
        output = pyper.runR(command)
        if messages:
            print 'output:\t\t', output.replace('\n', '\n\t\t\t')

    def run(self, point_url, aggregation_url):
        """Runs the analysis
            Params;
                point_url: Location of the point netCDF file
                aggregation_url: Location of the coverage netCDF file
        """

        start = time.time()
        #log.debug("Ecomaps analysis started at %s" % time)

        # points_df = self._open_sample_opendap(point_url)
        #
        # northing_list, easting_list = self._get_coordinate_lists(aggregation_url)
        # array = self._get_landcover_array(aggregation_url)


        # array_intersect = self._sample_intersect(northing_list, easting_list, points_df, array)
        #
        csv_folder = self._working_dir.csv_folder
        csv_file_name = 'InputRDataFile.csv'
        csv_full_path = os.path.normpath(
            os.path.join(csv_folder, csv_file_name)
        )
        #
        # self._data_frame_to_csv(array_intersect, csv_full_path)

        r_code_folder = self._working_dir.r_script_folder
        r_script = 'LCM_thredds_model_ForSimon03.r'
        r_script_full_path = os.path.normpath(
            os.path.join(r_code_folder, r_script)
        )

        r = pyper.R()

        r["csv_file"] = csv_full_path
        r["image_file"] = os.path.join(self._working_dir.image_folder, 'map_output.png')
        r["temp_netcdf_file"] = os.path.join(self._working_dir.netcdf_folder, 'temp.nc')
        r["output_netcdf_file"] = os.path.join(self._working_dir.netcdf_folder, 'output.nc')

        r.run(CMDS="source('%s')" % r_script_full_path)

        # Now to return the results - we're interested in where the netcdf results file
        # and the png image have been written to

        return r["output_netcdf_file"], r["image_file"]

