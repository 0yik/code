# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

class Contract(models.Model):
    _inherit = "account.analytic.account"

    @api.multi
    def open_purchase_tender(self):
        action = self.env.ref('purchase_tender_comparison.action_purchase_tender').read()[0]
        action['views'] = [(self.env.ref('purchase_requisition.view_purchase_requisition_form').id, 'form')]
        action['context'] = {
            'contract_id': self.id,
        }
        return action

class PurchaseTender(models.Model):
    _inherit = 'purchase.requisition'

    @api.model
    def default_get(self, fields):
        res          = super(PurchaseTender, self).default_get(fields)
        context      = dict(self._context or {})
        active_model = context.get('active_model')
        active_id    = context.get('active_id')
        if active_model and active_id:
            contract_id = self.env[active_model].browse(active_id)
            so_id       = self.env['sale.order'].search([('name', '=', contract_id.code)], limit=1)
            now         = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
            if so_id:
                job_estimate = self.env['sale.estimate.job'].search([('quotation_id', '=', so_id.id), ('state', '=', 'quotesend')], limit=1)
                line_vals    = []
                products     = []
                res['user_id']       = so_id.user_id.id
                res['date_end']      = now
                res['ordering_date'] = now
                if job_estimate:
                    for material in job_estimate.estimate_ids:
                        if material.product_id.id not in products and material.product_id.type != 'service':
                            line_vals.append((0, 0, {
                                'product_id'    : material.product_id.id,
                                'product_qty'   : material.product_uom_qty,
                                'product_uom_id': material.product_uom.id,
                                'schedule_date' : now,
                                'price_unit'    : material.price_unit,
                            }))
                            products.append(material.product_id.id)

                    for over_head in job_estimate.overhead_estimate_line_ids:
                        if over_head.product_id.id not in products and over_head.product_id.type != 'service':
                            line_vals.append((0, 0, {
                                'product_id'    : over_head.product_id.id,
                                'product_qty'   : over_head.product_uom_qty,
                                'product_uom_id': over_head.product_uom.id,
                                'schedule_date' : now,
                                'price_unit'    : over_head.price_unit,
                            }))
                            products.append(over_head.product_id.id)
                if line_vals:
                    res['line_ids'] = line_vals
        return res