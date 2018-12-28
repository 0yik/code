# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class pdp_internal_investment_standard(models.Model):
#     _name = 'pdp_internal_investment_standard.pdp_internal_investment_standard'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100