# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.onchange('branch_id')
    def onchange_branch_id(self):
        if self.branch_id:
            project = self.env['account.analytic.account'].search([('name', '=', self.branch_id.name)], limit =1)
            if project:
                self.project_id = project.id
            else:
                self.project_id = None