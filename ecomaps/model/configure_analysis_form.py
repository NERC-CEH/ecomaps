import formencode

__author__ = 'Chirag Mistry (Tessella)'


class ConfigureAnalysisForm(formencode.Schema):
    """Used to validate data from the Configure Analysis page"""

    allow_extra_fields = True
    filter_extra_fields = True

    point_dataset = formencode.validators.String(not_empty=True)
    coverage_sets = formencode.validators.String(not_empty=True)
    parameter1 = formencode.validatlors.String(not_empty=True)