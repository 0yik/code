# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LoyaltyMembershipPoint(models.Model):
	_name = 'loyalty.membership'

	name = fields.Char('Name')
	membership_point = fields.Float('Membership Point')
	loyalty_program_id = fields.Many2one('loyalty.program', string='Loyalty Program', help='The Loyalty Program this exception belongs to')

class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    rule_type = fields.Selection((('product', 'Product'), ('category', 'Category'), ('spend_amount','Spend Amount')), old_name='type', required=True, default='product', help='Does this rule affects products, or a category of products ?')
    spending_amount = fields.Float('Spending Amount')


class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    loyalty_option = fields.Selection([('reward', 'Rules & Reward'),('membership', 'Membership Point')],string='Select',default='reward')
    membership_ids = fields.One2many('loyalty.membership', 'loyalty_program_id', string='Membership')
