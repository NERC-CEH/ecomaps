import logging
from pylons.controllers.util import redirect
import formencode
from pylons.decorators import jsonify
from ecomaps.analysis.run import AnalysisRunner

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.analysis import AnalysisService
from ecomaps.services.netcdf import NetCdfService
from ecomaps.services.user import UserService
from ecomaps.services.dataset import DatasetService
from pylons import tmpl_context as c, url
from ecomaps.model.configure_analysis_form import ConfigureAnalysisForm
from formencode import htmlfill
import tempfile
from paste.fileapp import FileApp
import os

#from pylons import request, response, session, tmpl_context as c, url
#from pylons.controllers.util import abort, redirect

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class AnalysisController(BaseController):
    """Provides operations for analysis page actions"""

    _user_service = None
    _analysis_service = None
    _dataset_service = None
    _netcdf_service = None

    def __init__(self, user_service=UserService(), analysis_service=AnalysisService(),
                 dataset_service=DatasetService(), netcdf_service=NetCdfService()):
        """Constructor for the analysis controller, takes in any services required
            Params:
                user_service: User service to use within the controller
        """
        super(AnalysisController, self).__init__(user_service)

        self._analysis_service = analysis_service
        self._dataset_service = dataset_service
        self._netcdf_service = netcdf_service

    def index(self):
        """Default action for the analysis controller"""

        # Who am I?
        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])

        # Grab the analyses...
        c.private_analyses = self._analysis_service.get_analyses_for_user(user.id)

        c.public_analyses = self._analysis_service.get_public_analyses()

        return render('analysis_list.html')

    def create(self):
        """ Creates the configure analysis page"""

        identity = request.environ.get('REMOTE_USER')

        if identity is not None:

            user = self._user_service.get_user_by_username(identity)
            user_id = user.id

            c.point_datasets = self._dataset_service.get_datasets_for_user(user_id,'Point')

            coverage_datasets = self._dataset_service.get_datasets_for_user(user_id, 'Coverage')

            for ds in coverage_datasets:

                ds.column_names = self._netcdf_service.get_variable_column_names(ds.netcdf_url)

            c.coverage_datasets = coverage_datasets

            year = None
            random_group = None
            model_variable = None
            data_type = None

            if not request.POST:

                return render('configure_analysis.html',
                              extra_vars={'year': year,
                                          'random_group': random_group,
                                          'model_variable': model_variable,
                                          'data_type': data_type})

            schema = ConfigureAnalysisForm()
            c.form_errors = {}

            if request.POST:

                try:
                    c.form_result = schema.to_python(request.params)

                except formencode.Invalid, error:
                    c.form_result = error.value
                    c.form_errors = error.error_dict or {}

                #    If coverage_dataset_ids is not populated on the form
                #    the validation doesn't throw an error, but instead returns an empty
                #    array. Hence we have to do the error-handling ourselves
                if not c.form_result.get('coverage_dataset_ids'):
                    c.form_errors = dict(c.form_errors.items() + {
                        'coverage_dataset_ids': 'Please select at least one coverage dataset'
                    }.items())

                if c.form_errors:
                    html = render('configure_analysis.html')

                    return htmlfill.render(html,
                                           defaults=c.form_result,
                                           errors=c.form_errors,
                                           auto_error_formatter=custom_formatter)
                else:
                    analysis_id = self._analysis_service.create(c.form_result.get('analysis_name'),
                                c.form_result.get('point_dataset_id'),
                                c.form_result.get('coverage_dataset_ids'),
                                user_id,
                                c.form_result.get('year'),
                                c.form_result.get('random_group'),
                                c.form_result.get('model_variable'),
                                c.form_result.get('data_type'))

                    c.analysis_id = analysis_id

                    analysis_to_run = self._analysis_service.get_analysis_by_id(analysis_id, user_id)

                    # The path to the code may need to be made dynamic
                    # if we start running multiple analyses
                    runner = AnalysisRunner('code_root')
                    runner.run_async(analysis_to_run)

                    return render('analysis_progress.html')

    def view(self, id):
        """Action for looking in detail at a single analysis
            id - ID of the analysis to look at
        """
        user = request.environ.get('REMOTE_USER')

        user_obj = self._user_service.get_user_by_username(user)

        added_successfully = ''

        if request.POST:
            try:
                c.form_result = request.params
            except:
                added_successfully = False
            else:
                id = int(c.form_result.get('analysis_id'))
                self._analysis_service.publish_analysis(id)
                added_successfully = True

        analysis = self._analysis_service.get_analysis_by_id(id, user_obj.id)

        if analysis:

            # Get the result attributes from the NetCDF file associated with the result dataset
            analysis.attributes = self._netcdf_service.get_attributes(analysis.result_dataset.netcdf_url)

            c.analysis = analysis
            return render('analysis_view.html', extra_vars={'added_successfully': added_successfully})
        else:
            c.object_type = 'analysis'
            return render('not_found.html')

    def rerun(self, id):
        """Action for re-running a particular analysis with same parameters as before
            id - ID of the analysis to look at
        """
        user = request.environ.get('REMOTE_USER')
        user_object = self._user_service.get_user_by_username(user)
        user_id = user_object.id
        c.point_datasets = self._dataset_service.get_datasets_for_user(user_id,'Point')
        coverage_datasets = self._dataset_service.get_datasets_for_user(user_id, 'Coverage')

        # Be sure to populate the column names for each coverage dataset, this
        # will populate the list correctly
        for ds in coverage_datasets:
            ds.column_names = self._netcdf_service.get_variable_column_names(ds.netcdf_url)

        c.coverage_datasets = coverage_datasets

        current_analysis = self._analysis_service.get_analysis_by_id(id, user_id)
        point_dataset_id = current_analysis.point_data_dataset_id

        # For each coverage dataset that was linked to the original analysis, there
        # will be a number of column names chosen...
        cds = current_analysis.coverage_datasets
        coverage_dataset_ids = []

        # So create the right type of "ID" based on the convention we're using
        # which is <id>_<column-name>
        for dataset in cds:
            coverage_dataset_ids.extend(["%s_%s" % (dataset.dataset_id, col.column) for col in dataset.columns])

        year = current_analysis.year
        random_group = current_analysis.random_group
        model_variable = current_analysis.model_variable
        data_type = current_analysis.data_type

        return render('configure_analysis.html',
                              extra_vars={'current_point_dataset_id': point_dataset_id,
                                          'current_coverage_dataset_ids': coverage_dataset_ids,
                                          'year': year,
                                          'random_group': random_group,
                                          'model_variable': model_variable,
                                          'data_type': data_type})

    @jsonify
    def progress(self, id):
        """Gets a progress message from the analysis with the supplied ID
            Params:
                id: ID of analysis to get progress message for
        """

        user = request.environ.get('REMOTE_USER')
        user_obj = self._user_service.get_user_by_username(user)
        analysis = self._analysis_service.get_analysis_by_id(id, user_obj.id)

        return {
            'complete': analysis.complete,
            'message': analysis.progress_message
        }

    def test(self, id):

        c.analysis_id = id
        return render('analysis_progress.html')

    def download(self,id):
        '''Action that allows the user to download a results dataset
        '''

        user = request.environ.get('REMOTE_USER')
        user_object = self._user_service.get_user_by_username(user)
        user_id = user_object.id

        current_analysis = self._analysis_service.get_analysis_by_id(id, user_id)
        result_dataset_id = current_analysis.result_dataset_id
        result_dataset = self._dataset_service.get_dataset_by_id(result_dataset_id)
        url = result_dataset.netcdf_url

        data_file = self._analysis_service.get_netcdf_file(url)
        with tempfile.NamedTemporaryFile(suffix=".ncdf") as temp_file:
            temp_file.write(data_file.read())

            file_size = os.path.getsize(temp_file.name)

            headers = [('Content-Disposition', 'attachment; '
                       'filename=\"' + temp_file.name + '\"'),
                        ('Content-Type', 'text/plain'),
                        ('Content-Length', str(file_size))]

            fapp = FileApp(temp_file.name, headers=headers)

            return fapp(request.environ, self.start_response)

def custom_formatter(error):
    """Custom error formatter"""
    return '<span class="help-inline">%s</span>' % (
        htmlfill.html_quote(error)
    )
