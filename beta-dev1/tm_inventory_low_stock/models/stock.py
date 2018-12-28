from odoo import models, fields, api,_
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo.exceptions import ValidationError
from lxml import etree

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # is_low_stock = fields.Boolean('low stock',compute='_compute_is_low_stock')
    @api.multi
    def get_action_low_stock(self, cr, uid, context=None):
        ids = []
        reordering = self.env['stock.warehouse.orderpoint'].search([])
        for item in reordering:
            if item.product_id.qty_available <= item.product_min_qty:
                ids.append(item.product_id.product_tmpl_id.id)
        tree_id = self.env.ref('product.product_template_tree_view')
        form_id = self.env.ref('product.product_template_only_form_view')
        kanban_id = self.env.ref('tm_inventory_low_stock.dashboard_inventory_product_template_kanban_view')
        context.update({
            'is_low_stock_product' : True,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Low Stock Product',
            'views': [(kanban_id.id,'kanban'),(tree_id.id, 'tree'), (form_id.id, 'form')],
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'product.template',
            'domain': [('id', 'in', ids)],
            'context': context,
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
        res = super(ProductTemplate, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                            toolbar=toolbar, submenu=False)
        doc = etree.XML(res['arch'])
        if self.env.context.get('is_low_stock_product',False):
            if view_type == 'tree':
                nodes = doc.xpath("//tree[@string='Product']")
                for node in nodes:
                    node.set('create', '0')
                res['arch'] = etree.tostring(doc)
            # elif view_type == 'form':
            #     nodes = doc.xpath("//form[@name='Product Template']")
            #     for node in nodes:
            #         node.set('create', '0')
            #     res['arch'] = etree.tostring(doc)
            elif view_type == 'kanban':
                nodes = doc.xpath("//kanban")
                for node in nodes:
                    node.set('create', '0')
                res['arch'] = etree.tostring(doc)
        return res

