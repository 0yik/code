# -*- coding: utf-8 -*-

from ..services.data_getter_interface import DataGetterType
from odoo import models, fields, api

class data_update(models.Model):
    _name = 'marketplaces.data.update'

    def _selection_service(self, **k):
        res = [(x.code, x.name) for x in DataGetterType.getters.values()]
        return res

    service = fields.Selection(_selection_service, string='Webservice', required=True)
    app_id = fields.Char('App ID')
    app_secret = fields.Char('App Secret')

    def get_getter(self):
        result = None
        if self.service:
            result = DataGetterType.get(self.service, self.app_id, self.app_secret)
        return result

    @api.multi
    def action_get_products(self):
        product_obj = self.env['marketplaces.data.product']
        attribute_obj = self.env['marketplaces.data.product.attribute']
        productLine_obj = self.env['marketplaces.data.product.line']
        getter = self.get_getter()
        products = getter.get_products()
        for product in products:
            item = {
                'name': product.get('name')
            }
            existed = product_obj.search([('name', '=', product.get('name'))], limit=1)
            if existed and len(existed)>0:
                existed.write(item)
            else:
                existed = product_obj.create(item)

            for attribute in product['attributes']:
                if attribute:
                    attr = {
                        'code': attribute,
                        'name': attribute
                    }
                    existedAttr = attribute_obj.search([('code', '=', attribute)], limit=1)
                    if existedAttr and len(existedAttr)>0:
                        existedAttr.write(attr)
                    else:
                        existedAttr = attribute_obj.create(attr)

                    productLine = {
                        'parent_id': existed.id,
                        'attribute_id': existedAttr.id,
                        'value': product['attributes'][attribute],
                    }
                    existedPL = productLine_obj.search([('parent_id', '=', existed.id), ('attribute_id', '=', existedAttr.id)])
                    if existedPL and len(existedPL) > 0:
                        existedPL.write(productLine)
                    else:
                        productLine_obj.create(productLine)

        return True