from odoo import api, fields, models, _
import time

class partner(models.Model):
    _inherit = 'res.partner'

    # after zip
    kelurahan_id = fields.Many2one('vit.kelurahan', string="Kelurahan", required=False)
    kecamatan_id  = fields.Many2one('vit.kecamatan', string="Kecamatan", required=False)
    kota_id = fields.Many2one('vit.kota', string="Kota/Kabupaten", required=False)

class kelurahan(models.Model):
    _name = 'vit.kelurahan'
    # Commented this because Name should be displayed in relational field
    # _rec_name = 'code'

    code = fields.Char('Kode Wilayah')
    name = fields.Char('Kelurahan')
    zip = fields.Char(string="Kode POS", required=False)
    kecamatan_id = fields.Many2one('vit.kecamatan', string="Kecamatan", required=False)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Kode Wilayah must be unique !'),
    ]

class kecamatan(models.Model):
    _name = 'vit.kecamatan'
    # _rec_name = 'code'

    code = fields.Char('Kode Wilayah')
    name = fields.Char('Kecamatan', index=1)
    kota_id = fields.Many2one('vit.kota', string="Kota", required=False)
    state_id = fields.Many2one('res.country.state',  string="Nama Propinsi")

    @api.onchange('kota_id')
    def onchange_kota_id(self):
        for rec in self:
            if rec.kota_id:
                self.state_id = rec.kota_id.state_id

    @api.multi
    def update_state_id(self):

        vit_kecamatans = self.env['vit.kecamatan'].sudo().search([])
        for rec in vit_kecamatans:
            if rec.kota_id and rec.kota_id.state_id:
                self._cr.execute('update vit_kecamatan set state_id = %s ' 'where id=%s',(rec.kota_id.state_id.id, rec.id))
        return True

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Kode Wilayah must be unique !'),
    ]

class kota(models.Model):
    _name = 'vit.kota'
    # Commented this because Name should be displayed in relational field
    # _rec_name = 'code'

    code = fields.Char('Kode Wilayah')
    name = fields.Char('Kota/Kabupaten', index=1)
    jenis = fields.Selection(string="Jenis", selection=[('kota', 'Kota'), ('kab', 'Kab.'), ], required=False, index=1)
    state_id = fields.Many2one('res.country.state', string="State", required=False)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Kode Wilayah must be unique !'),
    ]

# Inherited this because While importing data for vit.kecamatan kode_id should be matched with code not name
# Inherited this because While importing data for vit.kelurahan kecamatan_id should be matched with code not name
class IrFieldsConverter(models.AbstractModel):
    _inherit = 'ir.fields.converter'

    @api.model
    def db_id_for(self, model, field, subfield, value):
        id = None
        warnings = []
        if (field.comodel_name=='vit.kota' or field.comodel_name=='vit.kecamatan' or field.comodel_name=='vit.kelurahan')and subfield is None:
            field_type = _(u"name")
            RelatedModel = self.env[field.comodel_name]
            ids = RelatedModel.name_search(args=[('code', '=', value)])
            if ids:
                if len(ids) > 1:
                    warnings.append(ImportWarning(
                        _(u"Found multiple matches for field '%%(field)s' (%d matches)")
                        % (len(ids))))
                id, _name = ids[0]
            return id, field_type, warnings

        return super(IrFieldsConverter, self).db_id_for(model, field, subfield, value)