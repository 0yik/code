# coding=utf-8
from odoo import api, fields, models, _

class ResGroupsModifier(models.Model):
    _inherit = "res.company"

    company_code = fields.Char(string="Kode Company")