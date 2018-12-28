# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class crm_askcode_partner(models.TransientModel):
    _name = 'crm.askcode.partner'
    _description = 'Lead To Partner'

    code_partner = fields.Char('Code',required=True)

    @api.v7
    def convert_to_part(self,context=None):
        if context.get('active_id'):
            w = self
            lead_obje = self.env['crm.lead'].browse(context.get('active_id'))
            partner = self.env['res.partner']
            vals_dict = {}
            if lead_obje.partner_name:
                sale_pricelist_id = self.env['product.pricelist'].create({'name':lead_obje.partner_name})
                vals_dict = {
                    'partner_code': w.code_partner,
                    'name':lead_obje.partner_name,
                    'phone':lead_obje.phone,
                    'user_id': self._uid,
                    'partner_code':w.code_partner,
                    'email':lead_obje.email_from,
                    'street':lead_obje.street,
                    'street2':lead_obje.street2,
                    'country_id':lead_obje.country_id.id,
                    'zip':lead_obje.zip,
                    'property_product_pricelist':sale_pricelist_id.id,
                    'is_company': False,
                    'type': 'contact',
                    'customer':True,
                    'supplier':False,
                }
                partner_id = partner.create(vals_dict)
                lead_obje.write({'partner_id':partner_id.id})
                models_data = self.env['ir.model.data']

                # Get opportunity views
                dummy, form_view = models_data.get_object_reference('base', 'view_partner_form')
                dummy, tree_view = models_data.get_object_reference('base', 'view_partner_tree')
                return {
                    'name': _('Accounts'),
                    'view_type': 'form',
                    'view_mode': 'tree, form',
                    'res_model': 'res.partner',
                    'res_id': int(partner_id),
                    'view_id': False,
                    'views': [(form_view or False, 'form'),
                              (tree_view or False, 'tree'),],
                    'type': 'ir.actions.act_window',
                    'context': {}
                }