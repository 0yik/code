# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import ValidationError


class res_partner(models.Model):
    _inherit = 'res.partner'

    fax2 = fields.Char('Fax 2')
    note = fields.Text('Notes')
    is_active = fields.Boolean('Active')
    is_lock = fields.Boolean('Lock')
    active_lock = fields.Selection([('active', 'Active'), ('lock', 'Lock')], default='active')
    vendor_code = fields.Char('Vendor Code')

    @api.one
    @api.constrains('vendor_code')
    def _check_vendor_code(self):
        vendor_code = self.search([('vendor_code', '!=', False),('vendor_code', '=', self.vendor_code)])
        if len(vendor_code) > 1:
            raise ValidationError(_("Vendor Code must be unique."))

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(res_partner, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
    #     vendor = self.env.ref('base.action_partner_supplier_form').id
    #     doc = etree.XML(res['arch'])
    #     if self._context.get('params') and self._context.get('params').get('action') and vendor == self._context.get(
    #             'params').get('action'):
    #         if view_type == 'form':
    #             for node in doc.xpath("//field[@name='phone']"):
    #                 node.set('string', "Phone 1")
    #             for node in doc.xpath("//field[@name='mobile']"):
    #                 node.set('string', "Phone 2")
    #             for node in doc.xpath("//field[@name='fax']"):
    #                 node.set('string', "Fax 1")
                # for node in doc.xpath("//field[@name='credit_limit']"):
                #     node.set('string', "Debit Limit")
        #         res['arch'] = etree.tostring(doc)
        # return res
