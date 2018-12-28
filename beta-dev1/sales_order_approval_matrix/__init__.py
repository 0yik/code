# -*- coding: utf-8 -*-
# Part of eComBucket. See LICENSE file for full copyright and licensing details
import models
def odoo_version_check(cr):
    from openerp.exceptions import Warning
    from openerp.service import common
    exp_version = common.exp_version()
    if exp_version.get('server_serie')!='10.0':
    	error_message="""
    	At Present this extension
    	developed for Odoo version 10.0,
    	Kindly not try to install in {version}""".format(
    		version = exp_version.get('server_serie'))
    	raise Warning(error_message)
    return True
