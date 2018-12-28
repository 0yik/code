# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class Respartner(models.Model):
    _inherit = 'res.partner'

    # @api.onchange('npwp')
    # def onchange_npwp(self):
    #     warning = {}
    #     if self.npwp and len(self.npwp) != 20:
    #         warning = {'title': 'Value Error', 'message': "You enter the wrong NPWP. It must be 20 characters long."}
    #     if self.npwp and len(self.npwp) == 20:
    #         self.npwp = str(self.npwp)[:2] +'.'+ str(self.npwp)[2:5] +'.'+ str(self.npwp)[5:8] +'.'+str(self.npwp)[8:9] +'-'+ str(self.npwp)[9:12] + '.'+ str(self.npwp)[12:15]
    #     else:
    #         self.npwp = ''
    #     print"npwp:", self.npwp
    #     return {'warning': warning}

    @api.multi
    def _check_npwp1(self, npwp):
        npwp = npwp.replace('.','')
        npwp = npwp.replace('-','')
        return npwp

    @api.model
    def create(self, vals):
        if vals.get('npwp'):
            npwp = self._check_npwp1(vals.get('npwp'))
            vals['npwp'] = npwp
        return super(Respartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('npwp'):
            npwp = self._check_npwp1(vals.get('npwp'))
            vals['npwp'] = npwp
        return super(Respartner, self).write(vals)

    nama_wajib_pajak = fields.Char("Nama Wajib Pajak")
    provinsi = fields.Many2one('res.country.state', string="Provinsi")
    kodepos = fields.Char(related='kelurahan_id.zip' , string='Kode Pos')

Respartner()
