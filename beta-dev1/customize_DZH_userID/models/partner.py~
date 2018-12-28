# -*- coding: utf-8 -*-
from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'


    dzh_user = fields.Char('User ID')
    billing_cycle = fields.Selection([('monthly', 'Monthly'),
                                      ('quarterly', 'Quarterly'),
                                      ('semiannually', ' Semi-annually'),
                                      ('annually', 'Annually')
                                      ], string='Billing Cycle')

    dzh_status_id = fields.Many2one('dzh.partner.status', string='Status')
    partner_users = fields.One2many('dzh.partner.user', 'dzh_partner_id', string='')
    market_segment_id = fields.Many2one('market.segment', string="Market Segment")
    member_type_id = fields.Many2one('member.type', string="Member Type")

class ResPartnerStatus(models.Model):
    _name = 'dzh.partner.status'

    name = fields.Char('Name')

class ResPartnerUSERS(models.Model):
    _name = 'dzh.partner.user'
    _rec_name = 'user_id'

    name = fields.Text('Name')
    user_id = fields.Text('User ID')
    dzh_partner_id = fields.Many2one('res.partner',string='Partner id')

class MarketSegmet(models.Model):
    _name = 'dzh.market.segment'

    name = fields.Char('Name')

class MemberType(models.Model):
    _name = 'dzh.member.type'

    name = fields.Char('Name')


