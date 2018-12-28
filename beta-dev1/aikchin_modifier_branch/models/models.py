# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class aikchin_modifier_branch(models.Model):
#     _name = 'aikchin_modifier_branch.aikchin_modifier_branch'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
