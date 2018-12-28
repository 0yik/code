# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    is_hoax = fields.Boolean('Hoax')

    @api.model
    def update_hoax(self,partner):
        self.browse(partner).is_hoax = True
        return {'code':200}