# -*- coding: utf-8 -*-

from odoo import models, fields, api

class quality_control_approval(models.Model):
    _inherit = 'qc.inspection'

    @api.model
    def action_pass(self):
        self.write({
            'state' : 'success'
        })