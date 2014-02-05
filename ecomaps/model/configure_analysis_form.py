import formencode

__author__ = 'Chirag Mistry (Tessella)'


class ConfigureAnalysisForm(formencode.Schema):
    """Used to validate data from the Configure Analysis page"""

    allow_extra_fields = True
    filter_extra_fields = True

    coverage_sets_ids = formencode.validators.String(not_empty=True)
    parameter1 = formencode.validators.String(not_empty=True)