# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    gst_no = fields.Char('GST No.')
    registration_no = fields.Char('Registration No.')
