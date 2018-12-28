# -*- coding: utf-8 -*-

from odoo import models, fields, api

class crm_case_categ(models.Model):
    _inherit = 'helpdesk.ticket.type'

    type = fields.Char('Type')

