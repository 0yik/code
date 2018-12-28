# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AnchorMaster(models.Model):
    _inherit = 'anchor.master'

    user_id = fields.Many2one('res.users', 'User')

AnchorMaster()