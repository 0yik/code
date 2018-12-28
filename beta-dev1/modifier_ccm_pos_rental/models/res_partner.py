# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartnerSize(models.Model):
    _name = 'res.partner.size'
    _description = 'Partner Sizes'
    _rec_name = 'size_name'

    size_name = fields.Char("Size Name", required=True)


class ResPartnerRemarkTags(models.Model):
    _name = 'res.partner.remark.tags'
    _description = 'Remark Tags'

    name = fields.Char(required=True)
    color = fields.Integer('Color Index')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    size_id = fields.Many2one('res.partner.size', string="Size")
    remark_tag_ids = fields.Many2many('res.partner.remark.tags', string="Remarks")
    citizenship = fields.Selection([('singaporean', 'Singaporean/PR'), ('foreigner', 'Foreign Citizen')], required=True, default="singaporean")
    passport_no = fields.Char('Passport No')

    @api.multi
    def write(self, vals):
        if vals.get('citizenship') == 'singaporean':
            vals['passport_no'] = ''
        if vals.get('citizenship') == 'foreigner':
            vals['nric_no'] = ''
        return super(ResPartner, self).write(vals)
