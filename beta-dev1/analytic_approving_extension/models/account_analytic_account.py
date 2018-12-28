# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_request(models.Model):
    _inherit = 'account.analytic.account'

    is_project = fields.Boolean('Is a Project')