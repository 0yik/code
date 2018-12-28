# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class mgm_sales_dashboard(models.Model):
    _inherit = 'crm.team'

    @api.one
    def _kanban_sale_requisition_dashboard(self):
        self.sale_requisition_dashboard = json.dumps(self.get_sale_requisition_dashboard())

    sale_requisition_dashboard = fields.Text(compute='_kanban_sale_requisition_dashboard')

    @api.model
    def get_sale_requisition_dashboard(self):
        sale_requisition_ids = self.sudo().env['sale.requisition'].search([])
        ferry_draft = 0.00
        ferry_daily_rit = 0.00
        ferry_asdp_final = 0.00

        tug_barge_draft = 0.00
        tug_barge_daily_rit = 0.00
        tug_barge_asdp_final = 0.00

        stevedoring_draft = 0.00
        stevedoring_daily_rit = 0.00
        stevedoring_asdp_final = 0.00

        fls_draft = 0.00
        fls_daily_rit = 0.00
        fls_asdp_final = 0.00

        for sale_requisition_id in sale_requisition_ids:
            if sale_requisition_id.business_unit.unit == 'ferry' and sale_requisition_id.state == 'draft1':
                ferry_draft +=  sum(sale_requisition_id.line_ids.mapped('sub_total'))
            if sale_requisition_id.business_unit.unit == 'ferry' and sale_requisition_id.state in ['inprogress','dailynote']:
                ferry_daily_rit +=  sum(sale_requisition_id.line_ids.mapped('sub_total'))

            if sale_requisition_id.business_unit.unit == 'tug_barge' and sale_requisition_id.state == 'drafts':
                tug_barge_draft +=  sum(sale_requisition_id.line_ids.mapped('sub_total'))
            if sale_requisition_id.business_unit.unit == 'tug_barge' and sale_requisition_id.state in ['in_progress','done']:
                tug_barge_daily_rit +=  sum(sale_requisition_id.line_ids.mapped('sub_total'))

            if sale_requisition_id.business_unit.unit == 'stevedoring' and sale_requisition_id.state == 'drafts':
                stevedoring_draft +=  sum(sale_requisition_id.line_ids.mapped('sub_total'))
            if sale_requisition_id.business_unit.unit == 'stevedoring' and sale_requisition_id.state in ['in_progress','done']:
                stevedoring_daily_rit +=  sum(sale_requisition_id.line_ids.mapped('sub_total'))

            if sale_requisition_id.business_unit.unit == 'fls' and sale_requisition_id.state == 'drafts':
                fls_draft +=  sum(sale_requisition_id.line_ids.mapped('sub_total'))
            if sale_requisition_id.business_unit.unit == 'fls' and sale_requisition_id.state in ['in_progress','done']:
                fls_daily_rit +=  sum(sale_requisition_id.line_ids.mapped('sub_total'))

        sale_order_ids = self.sudo().env['sale.order'].search([])
        for sale_order_id in sale_order_ids:
            if sale_order_id.requisition_id.business_unit.unit == 'ferry' and sale_order_id.state not in ['draft', 'sent', 'cancel']:
                ferry_asdp_final +=  sale_order_id.amount_total

            if sale_order_id.requisition_id.business_unit.unit == 'tug_barge' and sale_order_id.state not in ['draft', 'sent', 'cancel']:
                tug_barge_asdp_final +=  sale_order_id.amount_total

            if sale_order_id.requisition_id.business_unit.unit == 'stevedoring' and sale_order_id.state not in ['draft', 'sent', 'cancel']:
                stevedoring_asdp_final +=  sale_order_id.amount_total

            if sale_order_id.requisition_id.business_unit.unit == 'fls' and sale_order_id.state not in ['draft', 'sent', 'cancel']:
                fls_asdp_final +=  sale_order_id.amount_total

        return {
            'ferry_draft' :  "Rp " + '{0:,.2f}'.format(ferry_draft),
            'ferry_daily_rit': "Rp " + '{0:,.2f}'.format(ferry_daily_rit),
            'ferry_asdp_final': "Rp " + '{0:,.2f}'.format(ferry_asdp_final),

            'tug_barge_draft': "Rp " + '{0:,.2f}'.format(tug_barge_draft),
            'tug_barge_daily_rit': "Rp " + '{0:,.2f}'.format(tug_barge_daily_rit),
            'tug_barge_asdp_final': "Rp " + '{0:,.2f}'.format(tug_barge_asdp_final),

            'stevedoring_draft': "Rp " + '{0:,.2f}'.format(stevedoring_draft),
            'stevedoring_daily_rit': "Rp " + '{0:,.2f}'.format(stevedoring_daily_rit),
            'stevedoring_asdp_final': "Rp " + '{0:,.2f}'.format(stevedoring_asdp_final),

            'fls_draft': "Rp " + '{0:,.2f}'.format(fls_draft),
            'fls_daily_rit': "Rp " + '{0:,.2f}'.format(fls_daily_rit),
            'fls_asdp_final': "Rp " + '{0:,.2f}'.format(fls_asdp_final),
        }
