# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class sign_in_historu(models.Model):
    _name = 'sign_in.history'

    subject            = fields.Char('Subject')
    author_user     = fields.Many2one('res.users', string='Author Metting')

    sign_in_time    = fields.Datetime('Time Sign In')
    sign_out_time   = fields.Datetime('Time Sign Out')

    latitude_in     = fields.Char('Latitude In')
    longitude_in    = fields.Char('Longitude In')
    latitude_out    = fields.Char('Latitude Out')
    longitude_out   = fields.Char('Longitude Out')

    author_in       = fields.Many2one('res.users', string='Sign In User')
    author_out      = fields.Many2one('res.users', string='Sign Out User')

    meeting_sumary  = fields.Text('Meeting Summary' )
    sign_in_id = fields.Many2many('sign.in', id1='history_ids', id2='sign_in_id', string='Parent')