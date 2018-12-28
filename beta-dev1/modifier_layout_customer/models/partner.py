from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.modules import get_module_resource

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name', 'company_title_id')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            if partner.is_company:
                display_name = "%s [%s]" % (names.get(partner.id),partner.company_title_id and partner.company_title_id.name or '')
            else:
                display_name = names.get(partner.id)
            partner.display_name = display_name



    # @api.constrains('pelanggan')
    # def _check_pelanggan(self):
    #     for rec in self:
    #         code = rec.search([('pelanggan', '=', rec.pelanggan)])
    #         if len(code) > 1:
    #             raise ValidationError(_("Kode Pelanggan must be unique."))

    phone = fields.Char(string="Telepon 1")
    phone2 = fields.Char(string="Telepon 2")
    blok2  = fields.Char(string='Blok')
    nomor2 = fields.Char(string="Nomor")
    city_id = fields.Many2one('vit.kota', string="Kelurahan", required=False)
    kecamatan_id2 = fields.Many2one('vit.kecamatan', string="Kecamatan", required=False)
    rt2 = fields.Char(string="RT")
    rw2 = fields.Char(string="RW")

    kelurahan_id2 = fields.Many2one('vit.kelurahan', string="Kelurahan", required=False)
    # pelanggan = fields.Char(string='Pelanggan', required=True)
    zip = fields.Char(related='kelurahan_id2.zip', change_default=True)
    kodepos = fields.Char(related='kelurahan_id2.zip', change_default=True)

    city_id_related         = fields.Char(related='city_id.name', string="Kota/Kab", readonly=True)
    kecamatan_id2_related   = fields.Char(related='kecamatan_id2.name', string="Kecamatan", readonly=True)
    kelurahan_id2_related   = fields.Char(related='kelurahan_id2.name', string="Kelurahan", readonly=True)
    state_id_related   = fields.Char(related='state_id.name', string="Propinsi", readonly=True)
    zip_related   = fields.Char(related='zip', string="Propinsi", readonly=True)
    company_title_id = fields.Many2one('company.title', 'Company Title')


    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        if self.env.context:
            if self.env.context['lang']:
                res['lang'] = self.env.context['lang']
        else:
            res['lang'] = 'id_ID'
        return res

    @api.onchange('company_type')
    def onchange_company_type(self):
        if not self.supplier:
            if self.company_type == 'company' and self.customer:
                img_path = get_module_resource('modifier_layout_customer', 'static/src/img', 'company.png')
                self.is_company = True
            else:
                img_path = get_module_resource('modifier_layout_customer', 'static/src/img', 'individual.png')
                self.is_company = False

            if img_path:
                with open(img_path, 'rb') as f:
                    image = f.read()
                    img = image.encode('base64')
                    self.image = img

        # For Vendor
        if self.supplier:
            if self.company_type == 'company':
                img_path = get_module_resource('modifier_layout_customer', 'static/src/img', 'company.png')
                self.is_company = True
            else :
                img_path = get_module_resource('modifier_layout_customer', 'static/src/img', 'individual.png')
                self.is_company = False

            if img_path:
                with open(img_path, 'rb') as f:
                    image = f.read()
                    img = image.encode('base64')
                    self.image = img


    @api.model
    def create(self, vals):
        if not vals.get('function',False):
            vals.update({'function': '-'})
        if not vals.get('phone', False):
            vals.update({'phone': '-'})
        if not vals.get('phone2',False):
            vals.update({'phone2': '-'})
        if not vals.get('mobile',False):
            vals.update({'mobile': '-'})
        if not vals.get('fax',False):
            vals.update({'fax': '-'})
        if not vals.get('email',False):
            vals.update({'email': '-'})
        if not vals.get('website',False):
            vals.update({'website': 'http://-'})
        # if not vals.get('title',False):
        #     vals.update({'title': self.env['res.partner.title'].search([('name','=','-')])[0].id})
        partner = super(ResPartner, self).create(vals)
        partner.set_e_faktur_values()
        return partner

    @api.multi
    def write(self, vals):
        # if not vals.get('function',False):
        #     vals.update({'function': '-'})
        # if not vals.get('phone', False):
        #     vals.update({'phone': '-'})
        # if not vals.get('phone2',False):
        #     vals.update({'phone2': '-'})
        # if not vals.get('mobile',False):
        #     vals.update({'mobile': '-'})
        # if not vals.get('fax',False):
        #     vals.update({'fax': '-'})
        # if not vals.get('email',False):
        #     vals.update({'email': '-'})
        # if not vals.get('website',False):
        #     vals.update({'website': 'http://-'})
        # if not vals.get('title',False):
        #     vals.update({'title': self.env['res.partner.title'].search([('name','=','-')])[0].id})
        # for rec in self:
        res = super(ResPartner, self).write(vals)
        for partner in self:
            partner.set_e_faktur_values()
        return res

    @api.multi
    def set_e_faktur_values(self):
        if self.blok2 and not self.blok:
            self.blok = self.blok2
        elif not self.blok2 and self.blok:
            self.blok2 = self.blok
        if self.nomor2 and not self.nomor:
            self.nomor = self.nomor2
        elif not self.nomor2 and self.nomor:
            self.nomor2 = self.nomor
        if self.rt2 and not self.rt:
            self.rt = self.rt2
        elif not self.rt2 and self.rt:
            self.rt2 = self.rt
        if self.rw2 and not self.rw:
            self.rw = self.rw2
        elif not self.rw2 and self.rw:
            self.rw2 = self.rw
        if self.blok and not self.blok2:
            self.blok2 = self.blok
        elif not self.blok and self.blok2:
            self.blok = self.blok2
        if self.street and not self.alamat_lengkap:
            self.alamat_lengkap = self.street
        elif not self.street and self.alamat_lengkap:
            self.street = self.alamat_lengkap
        if self.provinsi and not self.state_id:
            self.state_id = self.provinsi.id
        elif not self.provinsi and self.state_id:
            self.provinsi = self.state_id.id
        if self.kota_id and not self.city_id:
            self.city_id = self.kota_id.id
        elif not self.kota_id and self.city_id:
            self.kota_id = self.city_id.id
        if self.kecamatan_id and not self.kecamatan_id2:
            self.kecamatan_id2 = self.kecamatan_id.id
        elif not self.kecamatan_id and self.kecamatan_id2:
            self.kecamatan_id = self.kecamatan_id2.id
        if self.kelurahan_id and not self.kelurahan_id2:
            self.kelurahan_id2 = self.kelurahan_id.id
        elif not self.kelurahan_id and self.kelurahan_id2:
            self.kelurahan_id = self.kelurahan_id2.id

# Commented all onchanges because the logic moved to save button for create and write
    # @api.onchange('blok2')
    # def onchange_blok2(self):
    #     if self.blok2 and not self.blok:
    #         self.blok = self.blok2
    #     if not self.blok2 and self.blok:
    #         self.blok2 = self.blok

    # @api.onchange('nomor2')
    # def onchange_nomor2(self):
    #     if self.nomor2 and not self.nomor:
    #         self.nomor = self.nomor2
    #     if not self.nomor2 and self.nomor:
    #         self.nomor2 = self.nomor

    # @api.onchange('rt2')
    # def onchange_rt2(self):
    #     if self.rt2 and not self.rt:
    #         self.rt = self.rt2
    #     if not self.rt2 and self.rt:
    #         self.rt2 = self.rt

    # @api.onchange('rw2')
    # def onchange_rw2(self):
    #     if self.rw2 and not self.rw:
    #         self.rw = self.rw2
    #     if not self.rw2 and self.rw:
    #         self.rw2 = self.rw

    # @api.onchange('blok')
    # def onchange_blok(self):
    #     if self.blok and not self.blok2:
    #         self.blok2 = self.blok
    #     if not self.blok and self.blok2:
    #         self.blok = self.blok2

    # @api.onchange('nomor')
    # def onchange_nomor(self):
    #     if self.nomor and not self.nomor2:
    #         self.nomor2 = self.nomor
    #     if not self.nomor and self.nomor2:
    #         self.nomor = self.nomor2

    # @api.onchange('rt')
    # def onchange_rt(self):
    #     if self.rt and not self.rt2:
    #         self.rt2 = self.rt
    #     if not self.rt and self.rt2:
    #         self.rt = self.rt2

    # @api.onchange('rw')
    # def onchange_rw(self):
    #     if self.rw and not self.rw2:
    #         self.rw2 = self.rw
    #     if not self.rw and self.rw2:
    #         self.rw = self.rw2

    # @api.onchange('street')
    # def onchange_street(self):
    #     if self.street and not self.alamat_lengkap:
    #         self.alamat_lengkap = self.street
    #     if not self.street and self.alamat_lengkap:
    #         self.street = self.alamat_lengkap

    # @api.onchange('alamat_lengkap')
    # def onchange_alamat_lengkap(self):
    #     if self.alamat_lengkap and not self.street:
    #         self.street = self.alamat_lengkap
    #     if not self.alamat_lengkap and self.street:
    #         self.alamat_lengkap = self.street

    @api.onchange('provinsi')
    def onchange_provinsi(self):
    #     if self.provinsi and not self.state_id:
    #         self.state_id = self.provinsi.id
    #     if not self.provinsi and self.state_id:
    #         self.provinsi = self.state_id.id
        if not self.provinsi:
            self.kota_id = False

    @api.onchange('state_id')
    def onchange_state_id(self):
    #     print "HELOOOOOOOOOOOOOOOOOO",self.state_id
    #     if self.state_id and not self.provinsi:
    #         self.provinsi = self.state_id.id
    #     if not self.state_id and self.provinsi:
    #         self.state_id = self.provinsi.id
        if not self.state_id:
            self.city_id = False

    @api.onchange('kota_id')
    def onchange_kota_id(self):
        # if self.kota_id and not self.city_id:
        #     self.city_id = self.kota_id.id
        # if not self.kota_id and self.city_id:
        #     self.kota_id = self.city_id.id
        if not self.kota_id:
            self.kecamatan_id = False

    @api.onchange('city_id')
    def onchange_city_id(self):
        # if self.city_id and not self.kota_id:
        #     self.kota_id = self.city_id.id
        # if not self.city_id and self.kota_id:
        #     self.city_id = self.kota_id.id
        if not self.city_id:
            self.kecamatan_id2 = False

    @api.onchange('kecamatan_id')
    def onchange_kecamatan_id(self):
        # if self.kecamatan_id and not self.kecamatan_id2:
        #     self.kecamatan_id2 = self.kecamatan_id.id
        # if not self.kecamatan_id and self.kecamatan_id2:
        #     self.kecamatan_id = self.kecamatan_id2.id
        if not self.kecamatan_id:
            self.kelurahan_id = False

    @api.onchange('kecamatan_id2')
    def onchange_kecamatan_id2(self):
        # if self.kecamatan_id2 and not self.kecamatan_id:
        #     self.kecamatan_id = self.kecamatan_id2.id
        # if not self.kecamatan_id2 and self.kecamatan_id:
        #     self.kecamatan_id2 = self.kecamatan_id.id
        if not self.kecamatan_id2:
            self.kelurahan_id2 = False

    # @api.onchange('kelurahan_id')
    # def onchange_kelurahan_id(self):
    #     if self.kelurahan_id and not self.kelurahan_id2:
    #         self.kelurahan_id2 = self.kelurahan_id.id
    #     if not self.kelurahan_id and self.kelurahan_id2:
    #         self.kelurahan_id = self.kelurahan_id2.id

    # @api.onchange('kelurahan_id2')
    # def onchange_kelurahan_id2(self):
    #     if self.kelurahan_id2 and not self.kelurahan_id:
    #         self.kelurahan_id = self.kelurahan_id2.id
    #     if not self.kelurahan_id2 and self.kelurahan_id:
    #         self.kelurahan_id2 = self.kelurahan_id.id


    # lang = fields.Selection(_lang_get, string='Language', default=_lang_get,
    #                         help="If the selected language is loaded in the system, all documents related to "
    #                              "this contact will be printed in this language. If not, it will be English.")
    
class res_country_state(models.Model):
    _inherit = 'res.country.state'
    _order = 'name'

class vit_kota(models.Model):
    _inherit = 'vit.kota'
    _order = 'name'

class vit_kecamatan(models.Model):
    _inherit = 'vit.kecamatan'
    _order = 'name'

class vit_kelurahan(models.Model):
    _inherit = 'vit.kelurahan'
    _order = 'name'

class ResCompany(models.Model):
    _inherit = 'res.company'

    # @api.constrains('pelanggan')
    # def _check_pelanggan(self):
    #     for rec in self:
    #         code = rec.search([('pelanggan', '=', rec.pelanggan)])
    #         if len(code) > 1:
    #             raise ValidationError(_("Kode Pelanggan must be unique."))

    phone = fields.Char(string="Telepon 1")
    phone2 = fields.Char(string="Telepon 2")
    blok2 = fields.Char(string='Blok')
    nomor2 = fields.Char(string="Nomor")
    city_id = fields.Many2one('vit.kota', string="Kelurahan", required=False)
    kecamatan_id2 = fields.Many2one('vit.kecamatan', string="Kecamatan", required=False)
    rt2 = fields.Char(string="RT")
    rw2 = fields.Char(string="RW")

    kelurahan_id2 = fields.Many2one('vit.kelurahan', string="Kelurahan", required=False)
    # pelanggan = fields.Char(string='Pelanggan', required=True)
    zip = fields.Char(related='kelurahan_id2.zip', change_default=True)

    city_id_related = fields.Char(related='city_id.name', string="Kota/Kab", readonly=True)
    kecamatan_id2_related = fields.Char(related='kecamatan_id2.name', string="Kecamatan", readonly=True)
    kelurahan_id2_related = fields.Char(related='kelurahan_id2.name', string="Kelurahan", readonly=True)
    state_id_related = fields.Char(related='state_id.name', string="Propinsi", readonly=True)
    zip_related = fields.Char(related='zip', string="Propinsi", readonly=True)

    # @api.model
    # def default_get(self, fields):
    #     res = super(ResPartner, self).default_get(fields)
    #     res['lang'] = 'id_ID'
    #     return res

    @api.onchange('company_type')
    def onchange_company_type(self):
        if not self.supplier:
            if self.company_type == 'company' and self.customer:
                img_path = get_module_resource('modifier_layout_customer', 'static/src/img', 'company.png')
                self.is_company = True
            else:
                img_path = get_module_resource('modifier_layout_customer', 'static/src/img', 'individual.png')
                self.is_company = False

            if img_path:
                with open(img_path, 'rb') as f:
                    image = f.read()
                    img = image.encode('base64')
                    self.image = img

    # @api.model
    # def create(self, vals):
    #     if not vals.get('function', False):
    #         vals.update({'function': '-'})
    #     if not vals.get('phone', False):
    #         vals.update({'phone': '-'})
    #     if not vals.get('phone2', False):
    #         vals.update({'phone2': '-'})
    #     if not vals.get('mobile', False):
    #         vals.update({'mobile': '-'})
    #     if not vals.get('fax', False):
    #         vals.update({'fax': '-'})
    #     if not vals.get('email', False):
    #         vals.update({'email': '-'})
    #     if not vals.get('website', False):
    #         vals.update({'website': 'http://-'})
    #     if not vals.get('title', False):
    #         vals.update({'title': self.env['res.partner.title'].search([('name', '=', '-')])[0].id})
    #     partner = super(ResCompany, self).create(vals)
    #     partner.set_e_faktur_values()
    #     return partner
    #
    # @api.multi
    # def write(self, vals):
    #     if not vals.get('function', False):
    #         vals.update({'function': '-'})
    #     if not vals.get('phone', False):
    #         vals.update({'phone': '-'})
    #     if not vals.get('phone2', False):
    #         vals.update({'phone2': '-'})
    #     if not vals.get('mobile', False):
    #         vals.update({'mobile': '-'})
    #     if not vals.get('fax', False):
    #         vals.update({'fax': '-'})
    #     if not vals.get('email', False):
    #         vals.update({'email': '-'})
    #     if not vals.get('website', False):
    #         vals.update({'website': 'http://-'})
    #     if not vals.get('title', False):
    #         vals.update({'title': self.env['res.partner.title'].search([('name', '=', '-')])[0].id})
    #     res = super(ResCompany, self).write(vals)
    #     for partner in self:
    #         partner.set_e_faktur_values()
    #     return res

    @api.multi
    def set_e_faktur_values(self):
        if self.blok2 and not self.blok:
            self.blok = self.blok2
        elif not self.blok2 and self.blok:
            self.blok2 = self.blok
        if self.nomor2 and not self.nomor:
            self.nomor = self.nomor2
        elif not self.nomor2 and self.nomor:
            self.nomor2 = self.nomor
        if self.rt2 and not self.rt:
            self.rt = self.rt2
        elif not self.rt2 and self.rt:
            self.rt2 = self.rt
        if self.rw2 and not self.rw:
            self.rw = self.rw2
        elif not self.rw2 and self.rw:
            self.rw2 = self.rw
        if self.blok and not self.blok2:
            self.blok2 = self.blok
        elif not self.blok and self.blok2:
            self.blok = self.blok2
        if self.street and not self.alamat_lengkap:
            self.alamat_lengkap = self.street
        elif not self.street and self.alamat_lengkap:
            self.street = self.alamat_lengkap
        if self.provinsi and not self.state_id:
            self.state_id = self.provinsi.id
        elif not self.provinsi and self.state_id:
            self.provinsi = self.state_id.id
        if self.kota_id and not self.city_id:
            self.city_id = self.kota_id.id
        elif not self.kota_id and self.city_id:
            self.kota_id = self.city_id.id
        if self.kecamatan_id and not self.kecamatan_id2:
            self.kecamatan_id2 = self.kecamatan_id.id
        elif not self.kecamatan_id and self.kecamatan_id2:
            self.kecamatan_id = self.kecamatan_id2.id
        if self.kelurahan_id and not self.kelurahan_id2:
            self.kelurahan_id2 = self.kelurahan_id.id
        elif not self.kelurahan_id and self.kelurahan_id2:
            self.kelurahan_id = self.kelurahan_id2.id

    @api.onchange('provinsi')
    def onchange_provinsi(self):
        if not self.provinsi:
            self.kota_id = False

    @api.onchange('state_id')
    def onchange_state_id(self):
        if not self.state_id:
            self.city_id = False

    @api.onchange('kota_id')
    def onchange_kota_id(self):
        if not self.kota_id:
            self.kecamatan_id = False

    @api.onchange('city_id')
    def onchange_city_id(self):
        if not self.city_id:
            self.kecamatan_id2 = False

    @api.onchange('kecamatan_id')
    def onchange_kecamatan_id(self):
        if not self.kecamatan_id:
            self.kelurahan_id = False

    @api.onchange('kecamatan_id2')
    def onchange_kecamatan_id2(self):
        if not self.kecamatan_id2:
            self.kelurahan_id2 = False
