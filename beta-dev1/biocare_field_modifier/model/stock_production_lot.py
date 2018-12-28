# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _, SUPERUSER_ID
from lxml import etree


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(StockProductionLot, self).fields_view_get(
                        view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        print self.env.user.has_group('stock.group_stock_manager')
        if (view_type == 'form' or view_type == 'tree') and self.env.user.has_group('stock.group_stock_user') and not self.env.user.has_group('stock.group_stock_manager') and self.env.user.id != 1:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                node.set('create', 'false')
                node.set('edit', 'false')
            for node in doc.xpath("//tree"):
                node.set('create', 'false')
                node.set('edit', 'false')
            res['arch'] = etree.tostring(doc)
        elif (view_type == 'form' or view_type == 'tree') and self.env.user.id == 1 and self.env.user.has_group('stock.group_stock_manager'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                node.set('create', 'true')
                node.set('edit', 'true')
            for node in doc.xpath("//tree"):
                node.set('create', 'true')
                node.set('edit', 'true')
            res['arch'] = etree.tostring(doc)
            return res
        elif (view_type == 'form' or view_type == 'tree') and self.env.user.has_group('stock.group_stock_user') and self.env.user.has_group('stock.group_stock_manager') and self._uid != SUPERUSER_ID :
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                node.set('create', 'true')
                node.set('edit', 'true')
            for node in doc.xpath("//tree"):
                node.set('create', 'true')
                node.set('edit', 'true')
            res['arch'] = etree.tostring(doc)
            return res

        else:
            return res
        return res


