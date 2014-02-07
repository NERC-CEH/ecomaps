import logging
from pylons.controllers.util import redirect
import formencode

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.analysis import AnalysisService
from ecomaps.services.user import UserService
from ecomaps.services.dataset import DatasetService
from pylons import tmpl_context as c, url
from ecomaps.model.configure_analysis_form import ConfigureAnalysisForm

#from pylons import request, response, session, tmpl_context as c, url
#from pylons.controllers.util import abort, redirect

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class AnalysisController(BaseController):
    """Provides operations for analysis page actions"""

    _user_service = None
    _analysis_service = None
    _dataset_service = None

    def __init__(self, user_service=UserService(), analysis_service=AnalysisService(), dataset_service=DatasetService()):
        """Constructor for the user controller, takes in any services required
            Params:
                user_service: User service to use within the controller
        """
        super(BaseController, self).__init__()

        self._user_service = user_service
        self._analysis_service = analysis_service
        self._dataset_service = dataset_service

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

            if not request.POST:

                c.point_datasets = self._dataset_service.get_datasets_for_user(user_id,'Point')
                c.coverage_datasets = self._dataset_service.get_datasets_for_user(user_id, 'Coverage')

                return render('configure_analysis.html')

            schema = ConfigureAnalysisForm()
            form_errors = {}

            if request.POST:

                try:
                    form_result = schema.to_python(request.params)
                except formencode.Invalid, error:
                    response.content_type = 'text/plain'
                    return 'Invalid: '+unicode(error)
                else:
                    self._analysis_service.create(form_result.get('analysis_name'),
                                form_result.get('point_dataset_id'),
                                form_result.get('coverage_dataset_ids'),
                                user_id,
                                form_result.get('parameter1'))
                    return render('analysis_progress.html')

    def view(self, id):
        """Action for looking in detail at a single analysis
            id - ID of the analysis to look at
        """

        user = request.environ.get('REMOTE_USER')

        user_obj = self._user_service.get_user_by_username(user)

        analysis = self._analysis_service.get_analysis_by_id(id, user_obj.id)

        if analysis:
            c.analysis = analysis
            return render('analysis_view.html')
        else:
            c.object_type = 'analysis'
            return render('not_found.html')

    def test(self):

        return render('analysis_progress.html')