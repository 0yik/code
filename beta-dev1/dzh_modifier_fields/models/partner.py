# -*- coding: utf-8 -*-
from odoo import fields, api, models

class ResPartner(models.Model):
    _inherit = 'res.partner'


    dzh_user = fields.Char('User ID')
    billing_cycle = fields.Selection([('monthly', 'Monthly'),
                                      ('quarterly', 'Quarterly'),
                                      ('semiannually', ' Semi-annually'),
                                      ('annually', 'Annually')
                                      ], string='Billing Cycle')

    dzh_status_id = fields.Many2one('dzh.partner.status', string='Status', groups='base.group_user')
    partner_users = fields.One2many('dzh.partner.user', 'dzh_partner_id', string='')
    market_segment_id = fields.Many2one('market.segment', string="Market Segment")
    member_type_id = fields.Many2one('member.type', string="Member Type")
    sn_code_count = fields.Integer('S/N', default=0)

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        res = super(ResPartner, self).onchange_parent_id()
        parent_id = self.parent_id
        if res:
            res['value'].update({
                 'market_segment_id':parent_id.market_segment_id.id,
                 'member_type_id':parent_id.member_type_id.id,
                 'website': parent_id.website,
                 'category_id': [(6, 0, parent_id.category_id.ids)],
                 })
        return res

class ResPartnerStatus(models.Model):
    _name = 'dzh.partner.status'

    name = fields.Char('Name')

class ResPartnerUSERS(models.Model):
    _name = 'dzh.partner.user'
    _rec_name = 'user_id'
    # _order = 'id'

    serial_number = fields.Char('Serial Number')
    serial_number_sub = fields.Integer(compute='_default_value')
    name = fields.Text('Name')
    user_id = fields.Text('User ID')
    status = fields.Selection(
                  [('active', 'ACTIVE'),('inactive', 'INACTIVE')], 
                  string='Status', default='active')
    dzh_partner_id = fields.Many2one('res.partner',string='Partner id')
    order_line_id = fields.Many2many('sale.order.line', id1='sale_user_id', id2='order_line_id', string='Order Lines')
    invoice_line_id = fields.Many2many('account.invoice.line', id1='account_user_id', id2='invoice_line_id', string="Invoice IDS")

    @api.one
    @api.depends('serial_number')
    def _default_value(self):
        self.serial_number_sub = int(self.serial_number)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(ResPartnerUSERS, self).name_search(name, args=args, operator=operator, limit=limit)
        return res

    @api.model
    def create(self, vals):
        count = 1
        if vals.get('dzh_partner_id', False):
            partner = self.env['res.partner'].sudo().browse(vals.get('dzh_partner_id'))
            if partner.sn_code_count or partner.sn_code_count !=0:
                count = partner.sn_code_count + 1
            else:
                count = 1
            partner.sn_code_count = count
        vals['serial_number'] = count
        return super(ResPartnerUSERS, self).create(vals)

class MarketSegmet(models.Model):
    _name = 'dzh.market.segment'

    name = fields.Char('Name')

class MemberType(models.Model):
    _name = 'dzh.member.type'

    name = fields.Char('Name')







