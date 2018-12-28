# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MakeProcurement(models.TransientModel):
    _inherit = 'make.procurement'

    @api.multi
    def make_procurement(self):
        """ Creates procurement order for selected product. """
        ProcurementOrder = self.env['procurement.order']
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        for wizard in self:
            procurement = ProcurementOrder.create({
                'name': 'INT: %s' % (self.env.user.login),
                'date_planned': wizard.date_planned,
                'product_id': wizard.product_id.id,
                'branch_id': branch_id,
                'product_qty': wizard.qty,
                'product_uom': wizard.uom_id.id,
                'warehouse_id': wizard.warehouse_id.id,
                'location_id': wizard.warehouse_id.lot_stock_id.id,
                'company_id': wizard.warehouse_id.company_id.id,
                'route_ids': [(6, 0, wizard.route_ids.ids)]})
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'procurement.order',
            'res_id': procurement.id,
            'views': [(False, 'form'), (False, 'tree')],
            'type': 'ir.actions.act_window',
        }
