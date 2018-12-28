from odoo import api, fields, models, _

class invoice(models.Model):
    _inherit = 'account.invoice'

    efaktur_id  = fields.Many2one("vit.efaktur", string="Nomor Seri Faktur Pajak", required=False)
    is_efaktur_exported = fields.Boolean("Is eFaktur Exported")
    date_efaktur_exported = fields.Datetime("eFaktur Exported Date", required=False)

    masa_pajak = fields.Char("Masa Pajak", required=False, compute="_masa_pajak" )
    tahun_pajak = fields.Char("Tahun Pajak", required=False, compute="_tahun_pajak")

    efaktur_masukan = fields.Char("Nomor Seri Faktur Pajak", required=False) 

    @api.depends("date_invoice")
    def _masa_pajak(self):
        for inv in self:
            if inv.date_invoice:
                d = inv.date_invoice.split("-")
                inv.masa_pajak = d[1]

    @api.depends("date_invoice")
    def _tahun_pajak(self):
        for inv in self:
            if inv.date_invoice:
                d = inv.date_invoice.split("-")
                inv.tahun_pajak = d[0]

    @api.multi
    def action_invoice_open(self):
        res = super(invoice, self).action_invoice_open()
        self.is_efaktur_exported=False
        return res
