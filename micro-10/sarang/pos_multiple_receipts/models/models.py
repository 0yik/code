# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PosConfig(models.Model):
    _inherit = 'pos.config'

    no_of_print_for_proxy_ip = fields.Integer(string='No. of Receipts', default=1)
    wk_printer_ids = fields.Many2many('pos.order.printer', 'pos_config_printer_rel', 'config_id', 'printer_id', string='Printers (For Duplicate Receipts)')
    allow_multiple_receipt_printer = fields.Boolean(string="Allow Multiple Receipt Printers")

    @api.model
    def enable_multi_receipt_printer(self):
        config_ids = self.search([])
        if config_ids:
            config_ids[0].iface_print_via_proxy = True
            config_ids[0].allow_multiple_receipt_printer = True
    
    @api.constrains('no_of_print_for_proxy_ip')
    def validate_no_of_prints(self):
        if self.no_of_print_for_proxy_ip < 1:
            raise ValidationError("Number of receipts must be greater than zero")

class PosOrderPrinter(models.Model):

    _name = 'pos.order.printer'

    name = fields.Char('Printer Name', required=True, default='Printer', help='An internal identification of the printer')
    wk_proxy_ip = fields.Char('Proxy IP Address', help="The IP Address or hostname of the Printer's hardware proxy")
    no_of_print = fields.Integer("Number of Receipts",default=1)
    short_code = fields.Char("Short Code",required=True,size=3)

    @api.constrains('no_of_print')
    def validate_no_of_prints(self):
        if self.no_of_print < 1:
            raise ValidationError(" Number of receipts must be greater than zero")