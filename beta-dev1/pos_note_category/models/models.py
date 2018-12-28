# -*- coding: utf-8 -*-

from odoo import models, fields, api

class pos_note_category(models.Model):
    _name = 'pos.note.category'

    name = fields.Char('Attribute')
    pos_category_id = fields.Many2one('pos.category')

class pos_category(models.Model):
    _inherit = 'pos.category'

    note_ids = fields.One2many('pos.note.category','pos_category_id')



