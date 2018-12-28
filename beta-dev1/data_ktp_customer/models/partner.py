from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartnerKitData(models.Model):
    _name = 'res.partner.kit.data'

    color = fields.Integer('Color Index')
    name = fields.Char('Nama')
    nik = fields.Char('NIK')
    tempat_lahir = fields.Char('Tempat Lahir')
    tanggal_lahir = fields.Date('Tanggal Lahir')
    alamat = fields.Char('Alamat')
    blok = fields.Char('Blok')
    rt = fields.Char('RT')
    rw = fields.Char('RW')
    provinsi_id = fields.Many2one('res.country.state', string='Provinsi')
    partner_id = fields.Many2one('res.partner', 'Partner')
    kelurahan_id = fields.Many2one('vit.kelurahan', string="Kelurahan", required=False)
    kecamatan_id = fields.Many2one('vit.kecamatan', string="Kecamatan", required=False)
    kota_id = fields.Many2one('vit.kota', string="Kota/Kabupaten", required=False)
    kodepos = fields.Char(related='kelurahan_id.zip', string='Kode Pos')
    nomor = fields.Char('Nomor')
    # permilik_akun_poin = fields.Boolean('Pemilik Akun Poin')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    kit_ids = fields.One2many('res.partner.kit.data', 'partner_id', string='KITs')

    # @api.one
    # @api.constrains('kit_ids')
    # def _check_permilik_akun_poin(self):
    #     if len(self.kit_ids.filtered(lambda l: l.permilik_akun_poin))>2:
    #         raise ValidationError(_('Pemilik akun poin hanya bisa untuk dua KTP!'))
        



