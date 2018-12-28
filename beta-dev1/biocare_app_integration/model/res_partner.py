# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    current_pwd = fields.Char('current password')

ResPartner()
