from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class efaktur_reserver(models.TransientModel):
    _name = 'vit.reserve_efaktur'

    start_id = fields.Many2one('vit.efaktur', 'Start')
    end_id = fields.Many2one('vit.efaktur', 'End')

    @api.multi
    def confirm_button(self):
        if self.end_id.id >= self.start_id.id:
            res = self.env['vit.efaktur'].browse(range(self.start_id.id,self.end_id.id+1))
            for rec in res:
                rec.is_reserved = True
        else:
            raise ValidationError(_('End number must be greater then or equal to start number!'))
