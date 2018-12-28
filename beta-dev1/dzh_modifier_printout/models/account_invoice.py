from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
import string
from odoo.tools.misc import formatLang

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    def get_tax_name(self,invoice_line_tax_ids):
        tax_name = ''
        for tax in invoice_line_tax_ids:
            tax_name += tax.name +' '
        return tax_name
