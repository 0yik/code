from odoo import models, fields, api


class BuktiPotongPPhF113301Out(models.Model):
    _name = "l10n_id.bukti_potong_pph_f113301_out"
    _inherit = "l10n_id.bukti_potong_pph"
    _table = "l10n_id_bukti_potong_pph"
    _description = "Bukti Potong PPh f.1.1.33.01 Out"

    @api.model
    def _default_type_id(self):
        return self.env.ref(
            "indonesia_income_tax."
            "bukti_potong_pph_type_f113301_out").id

    type_id = fields.Many2one(
        default=lambda self: self._default_type_id(),
    )

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        type_id = self.env.ref(
            "indonesia_income_tax."
            "bukti_potong_pph_type_f113301_out")
        args.append(("type_id", "=", type_id.id))
        return super(BuktiPotongPPhF113301Out, self).\
            search(args, offset, limit, order)
