# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_branch(models.Model):
    _inherit = 'res.branch'

    street = fields.Char('Street')
    postcode = fields.Char('Postcode')