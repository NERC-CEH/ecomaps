import formencode

__author__ = 'Chirag Mistry (Tessella)'


class ConfigureAnalysisForm(formencode.Schema):
    """Used to validate data from the Configure Analysis page"""

    allow_extra_fields = True
    filter_extra_fields = False

    coverage_dataset_ids = formencode.validators.Set()
    parameter1 = formencode.validators.String(not_empty=True)