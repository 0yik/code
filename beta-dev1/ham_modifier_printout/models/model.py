from odoo import api, fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    po_no = fields.Char('Your PO No')
    job_po_no = fields.Char('JOb Order / Purchase Order')

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    job_po_no = fields.Char('JOb Order / Purchase Order')
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    job_po_no = fields.Char('JOb Order / Purchase Order')