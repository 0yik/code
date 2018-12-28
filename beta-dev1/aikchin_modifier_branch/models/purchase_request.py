# -*- coding: utf-8 -*-

from odoo import models, fields, api

class aikchin_modifier_branch(models.Model):
    _inherit = 'purchase.request'

    branch_id = fields.Many2one('res.branch', string="Branch")
