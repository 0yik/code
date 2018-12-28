# -*- coding: utf-8 -*-
from odoo import models, fields, api
from lxml import etree
from odoo.osv.orm import setup_modifiers
from odoo.tools.safe_eval import safe_eval

class product_template(models.Model):
    _inherit = 'product.template'

    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string="Status", default='draft')

    @api.multi
    def confirm_product(self):
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def product_reset_to_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(product_template, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        if view_type == "form":
            doc = etree.XML(result['arch'])
            for node in doc.iter(tag="field"):
                if 'readonly' in node.attrib.get("modifiers", ''):
                    attrs = node.attrib.get("attrs", '')
                    if 'readonly' in attrs:
                        attrs_dict = safe_eval(node.get('attrs'))
                        r_list = attrs_dict.get('readonly',)
                        if type(r_list) == list:
                            r_list.insert(0, ('state', '=', 'confirmed'))
                            if len(r_list) > 1:
                                r_list.insert(0, '|')
                        attrs_dict.update({'readonly': r_list})
                        node.set('attrs', str(attrs_dict))
                        setup_modifiers(node, result['fields'][node.get("name")])
                        continue
                    else:
                        continue
                node.set('attrs', "{'readonly':[('state','=','confirmed')]}")
                setup_modifiers(node, result['fields'][node.get("name")])
            result['arch'] = etree.tostring(doc)
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        args += [['state', '=', 'confirmed']]
        res = super(product_template, self).name_search(name, args=args, operator=operator, limit=limit)
        return res
