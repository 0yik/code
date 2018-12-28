# -*- coding: utf-8 -*-

from odoo import models, fields, api

class industry(models.Model):
    _name = 'industry'

    name = fields.Char('Name')