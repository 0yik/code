# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError, ValidationError
import json


class AccountPaymentDeposite(models.Model):
    _inherit = "account.invoice"
    

    user_ids = fields.Many2one('res.users', string="Collector")