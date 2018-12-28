# -*- coding: utf-8 -*-
from odoo import fields, models, api

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    market_segment_id = fields.Many2one('market.segment', string="Market Segment")
    member_type_id = fields.Many2one('member.type', string="Member Type")
    dzh_user = fields.Char('User ID')
    dzh_check_box = fields.Boolean(string="Trial Account")
    dzh_user_id = fields.Char('User ID')
    start_date= fields.Date('Start Date')
    end_date = fields.Date('End Date')
    product_id = fields.Many2many('product.product', string="Product")
    currency_id = fields.Many2one("res.currency", "Currency")
    remarks = fields.Text('Remarks')

    def _onchange_partner_id_values(self, partner_id):
        """ returns the new values when partner_id has changed """
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)

            partner_name = partner.parent_id.name
            if not partner_name or partner.is_company:
                partner_name = partner.name

            return {
                'partner_name': partner_name,
                'contact_name': partner.name if not partner.is_company else False,
                'title': partner.title.id,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id.id,
                'country_id': partner.country_id.id,
                'email_from': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'fax': partner.fax,
                'zip': partner.zip,
                'function': partner.function,
            }
        return {}

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            sales_team_ids = self.env['crm.team'].search([])
            for sales_team in sales_team_ids:
                fla = 0
                for user in sales_team.member_ids:
                    if user.id == self.user_id.id:
                        fla = 1
                if fla == 1:
                    self.team_id = sales_team.id
                    break
                else:
                    self.team_id = None

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.user_id and self.team_id:
            fla = 0
            for user in self.team_id.member_ids:
                if user.id == self.user_id.id:
                    fla = 1
            if fla == 0:
                self.user_id = None

    @api.onchange('partner_id')
    def onchange_customer(self):
        if self.partner_id:
            self.market_segment_id = self.partner_id.market_segment_id
            self.member_type_id = self.partner_id.member_type_id

    @api.model
    def create(self,vals):
        if 'partner_id' in vals and vals['partner_id']:
            customer_id = self.env['res.partner'].browse(vals['partner_id'])
            if 'market_segment_id' not in vals:
                vals.update({'market_segment_id':customer_id.market_segment_id.id})
            if 'member_type_id' not in vals:
                vals.update({'member_type_id':customer_id.member_type_id.id})
        res = super(CRMLead, self).create(vals)
        return res

    @api.multi
    def write(self,vals):
        if 'partner_id' in vals and vals['partner_id']:
            customer_id = self.env['res.partner'].browse(vals['partner_id'])
            if 'market_segment_id' not in vals:
                vals.update({'market_segment_id':customer_id.market_segment_id.id})
            if 'member_type_id' not in vals:
                vals.update({'member_type_id':customer_id.member_type_id.id})
        res = super(CRMLead, self).write(vals)
        return res

class MarketSegmet(models.Model):
    _name = 'market.segment'

    name = fields.Char('Name')

class MemberType(models.Model):
    _name = 'member.type'

    name = fields.Char('Name')

class crm_sales_team(models.Model):
    _inherit = 'crm.team'

    country = fields.Many2one('res.country','Country')
