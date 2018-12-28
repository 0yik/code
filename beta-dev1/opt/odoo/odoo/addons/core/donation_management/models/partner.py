# -*- coding: utf-8 -*-
from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    donor = fields.Boolean('Is Donor?')
    donation_ids = fields.One2many('donation', 'partner_id', string='Donations')

ResPartner()