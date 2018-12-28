# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CustomTargetGroup(models.Model):
    _inherit = 'target.group'

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()
        
    start_date = fields.Date("Start Date",
                             help="Start Date")
    end_date = fields.Date("End date", help="End Date")
    team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, default=_get_default_team)
