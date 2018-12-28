from odoo import api, fields, models, _
import math
from lxml import etree

class product_template(models.Model):

    _inherit ='product.template'

    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
        context = self._context or {}
        res = super(product_template, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                     toolbar=toolbar, submenu=False)
        #
        # dealer_group_id = self.env.user.has_group('helpdesk_lite.helpdesk_lite_dealer')
        # distributor_group_id = self.env.user.has_group('helpdesk_lite.helpdesk_lite_distributor')
        admin = self.env.user.has_group('base.group_system')

        doc = etree.XML(res['arch'])

        # if dealer_group_id or distributor_group_id:
        if not admin:
            if view_type == 'tree':
                nodes = doc.xpath("//tree[@string='Product']")
                for node in nodes:
                    node.set('create', '0')

                res['arch'] = etree.tostring(doc)
            elif view_type == 'form':
                nodes = doc.xpath("//form[@name='Product Template']")
                for node in nodes:
                    node.set('create', '0')
                    node.set('edit', '0')

                res['arch'] = etree.tostring(doc)
            elif view_type == 'kanban':
                nodes = doc.xpath("//kanban")
                for node in nodes:
                    node.set('create', '0')

                res['arch'] = etree.tostring(doc)
        return res

class product_product_template_inherit(models.Model):

    _inherit ='product.product'

    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
        context = self._context or {}
        res = super(product_product_template_inherit, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                    toolbar=toolbar, submenu=False)

        # dealer_group_id = self.env.user.has_group('helpdesk_lite.helpdesk_lite_dealer')
        # distributor_group_id = self.env.user.has_group('helpdesk_lite.helpdesk_lite_distributor')
        admin = self.env.user.has_group('base.group_system')

        doc = etree.XML(res['arch'])

        # if dealer_group_id or distributor_group_id:
        if not admin:
            if view_type == 'tree':
                nodes = doc.xpath("//tree[@string='Order Lines']")
                for node in nodes:
                    node.set('create', '0')

                res['arch'] = etree.tostring(doc)
            elif view_type == 'form':
                nodes = doc.xpath("//form[@name='Sales Order Lines']")
                for node in nodes:
                    node.set('create', '0')
                    node.set('edit', '0')

                res['arch'] = etree.tostring(doc)
            # elif view_type == 'kanban':
            #     nodes = doc.xpath("//kanban")
            #     for node in nodes:
            #         node.set('create','0')
            #
            #     res['arch'] = etree.tostring(doc)

        return res


