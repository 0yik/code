# -*- coding: utf-8 -*-

from odoo import models, fields, api

class delivery_address(models.Model):
    _name = 'purchase.request.delivery.address'

    name = fields.Char('Name')
    project_id = fields.Many2one('account.analytic.account')

    @api.model
    def create(self,vals):
        res = super(delivery_address, self).create(vals)
        if self._context.get('project_id'):
            res.project_id = self._context.get('project_id')
        return res
