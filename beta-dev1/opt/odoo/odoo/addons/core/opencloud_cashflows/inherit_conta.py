# -*- coding: utf-8 -*-
import random
import odoo

from odoo import SUPERUSER_ID, tools
#from odoo.osv import osv, orm, fields
from odoo import api, fields, models, tools
#from odoo.addons.web.http import request
from odoo import fields as field, models, _, api

class conta_inherit(models.Model):#orm.Model):
    _inherit = 'account.account'

    cashflow_type_id = fields.Many2one('cashflow.type', string='Tipo de Cashflow', index=True)

conta_inherit()
