# # -*- coding: utf-8 -*-
# from odoo import api, models, fields, registry
# import json
# class AccountPayment(models.Model):
#     _inherit = 'account.payment'
#
#     @api.model
#     def get_list_customer_deposit(self):
#         customers = self.env['account.payment'].search([('is_deposit', '=', True), ('payment_type', '=', 'inbound'),('partner_type', '=', 'customer')], limit=100)
#         result = []
#         for customer in customers:
#             result.append(customer.convert_to_json())
#         return result
#
#     @api.model
#     def convert_to_json(self):
#         return {
#             'id': self.id,
#             'communication': self.communication,
#             'name': self.name,
#             'partner_id': self.partner_id.name,
#             'payment_date': self.payment_date,
#             'amount': self.amount,
#             'state': self.state,
#         }