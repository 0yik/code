# coding=utf-8

from odoo import api, fields, models, _
from odoo.modules import get_module_resource


class ModifiedResPartner(models.Model):
    _inherit = 'res.partner'

    # For Foreign Vendors
    vendor_localization = fields.Selection(string="Type", selection=[('local', 'Local'), ('foreign', 'Foreign')],
                                           default='local')
    street = fields.Text('Street')
    foreign_street = fields.Char(string="Nama Jalan")
    foreign_street2 = fields.Char(string="Street")
    nomor_rumah = fields.Text(string="Nama Jalan")
    level_no = fields.Char()
    unit_no = fields.Char()
    kota = fields.Char()
    negara_bagian = fields.Char()
    kode_pos = fields.Char()
    negara = fields.Char()
    fv_phone = fields.Char()
    fv_phone2 = fields.Char(string="Telepon 2")
    fv_title = fields.Many2one('res.partner.title')
    fv_function = fields.Char()
    fv_mobile = fields.Char()
    fv_fax = fields.Char()
    fv_email = fields.Char()
    fv_website = fields.Char()
