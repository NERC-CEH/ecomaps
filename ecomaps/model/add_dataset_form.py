import formencode

__author__ = 'Chirag Mistry (Tessella)'


class AddDatasetForm(formencode.Schema):
    """Used to validate data from the Add New Dataset page"""

    allow_extra_fields = False
    filter_extra_fields = False

    name = formencode.validators.String(not_empty=True)
    type = formencode.validators.String(not_empty=True)
    wms_url = formencode.validators.String(if_missing=None)
    netcdf_url = formencode.validators.String(not_empty=True)
    low_res_url = formencode.validators.String(if_missing=None)
    data_range_from = formencode.validators.Int(if_missing=None)
    data_range_to = formencode.validators.Int(if_missing=None)
    is_categorical = formencode.validators.Bool()