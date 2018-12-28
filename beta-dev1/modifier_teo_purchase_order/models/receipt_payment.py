from odoo import api, fields, models, _

class ReceiptPayment(models.Model):
    _inherit = "receipt.payment"

    ref_cr = fields.Char('Reference Credits',
                                 related='line_cr_ids.move_line_id.ref')
    ref_dr = fields.Char('Reference Debits',
                      related='line_dr_ids.move_line_id.ref')