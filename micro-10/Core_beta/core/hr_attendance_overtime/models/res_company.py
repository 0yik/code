# -*- encoding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    ot1_monday = fields.Boolean(string="Monday", default=True)
    ot1_tuesday = fields.Boolean(string="Tuesday", default=True)
    ot1_wednesday = fields.Boolean(string="Wednesday", default=True)
    ot1_thursday = fields.Boolean(string="Thursday", default=True)
    ot1_friday = fields.Boolean(string="Friday", default=True)
    ot1_saturday = fields.Boolean(string="Saturday")
    ot1_sunday = fields.Boolean(string="Sunday")

    ot1_5_monday = fields.Boolean(string="Monday", default=True)
    ot1_5_tuesday = fields.Boolean(string="Tuesday", default=True)
    ot1_5_wednesday = fields.Boolean(string="Wednesday", default=True)
    ot1_5_thursday = fields.Boolean(string="Thursday", default=True)
    ot1_5_friday = fields.Boolean(string="Friday", default=True)
    ot1_5_saturday = fields.Boolean(string="Saturday")
    ot1_5_sunday = fields.Boolean(string="Sunday")

    ot2_saturday = fields.Boolean(string="Saturday", default=True)
    ot2_sunday = fields.Boolean(string="Sunday", default=True)

