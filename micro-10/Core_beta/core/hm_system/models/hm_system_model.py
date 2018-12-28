# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

class WebsitePlannerPdf(models.Model):
    _name = 'web.planner.pdf'
    _description = 'Planner PDF'

    name = fields.Char(string='Name', required=True)
    menu_get_id = fields.Many2one('ir.ui.menu',string='Menu',domain=[('parent_id', '=', False)])
    tooltip_planner = fields.Html(string='Planner Tooltips', translate=True)
    attch_doc = fields.Binary(string='Updload Document')

