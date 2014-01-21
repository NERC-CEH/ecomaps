"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *
import webhelpers.html.tags as html_tags
from pylons import config


def jsonParseIfNotEmpty(var):
    if var is not None and var != "":
        return 'JSON.parse("%s")' % var
    else:
        return 'null'
    
def getOpenLayersImportPath():
    return config.get('openlayers_js_path', config['serverurl'] + '/js/OpenLayers.js')

