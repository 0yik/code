# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class qr_code(models.Model):
    _name = 'qr.code'
    _rec_name = 'file_name'

    image = fields.Binary(string="QR Code image")
    file_name = fields.Char(string="File Name")
    uen_no = fields.Char(string='UEN #')

qr_code()