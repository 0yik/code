# -*- coding: utf-8 -*-

from odoo import api, fields, models
import datetime


class CrmLeadWon(models.TransientModel):
    _name = 'crm.lead.won'
    _description = 'Get Won Reason'

    won_reason = fields.Selection([('closed', 'Closed'), ('in_progress', 'In Progress')], 'Won Reason', required=True)
    lead_id = fields.Many2one('crm.lead',string="Lead")

    @api.multi
    def action_won_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        if leads:
            if self.won_reason == 'in_progress':

                in_progress_dict = {}

                if leads.partner_id:
                    in_progress_dict['partner_id'] = leads.partner_id.id
                    in_progress_dict['primary_sales_person_id'] = leads.user_id.id
                    in_progress_dict['product_name'] = leads.products.id
                    in_progress_dict['sales_won_date'] = datetime.datetime.now()
                sale_order_id = self.env['sale.order'].search([('opportunity_id', '=',leads.id)], limit=1)
                if sale_order_id:
                    purchase = []
                    for record in sale_order_id.order_line:
                        purchase_order_line = {}
                        # purchase_order_line['sources'] = record.product_id.id
                        # purchase_order_line['fees'] = record.price_subtotal

                        # purchase_order_line['product_qty'] = record.product_uom_qty
                        # purchase_order_line['price_unit'] = record.price_unit
                        # purchase_order_line['date_planned'] = self.date_order
                        # purchase_order_line['description'] = record.product_id.name
                        # purchase_order_line['product_uom'] = record.product_uom.id
                        tax_list = []
                        # for tax_id in record.tax_id:
                        #     tax_list.append(tax_id.id)
                        # purchase_order_line['taxes_id'] = [(6, 0, tax_list)]
                        purchase.append((0, 0, purchase_order_line))

                    # in_progress_dict['order_line'] = purchase

                if in_progress_dict:
                    self.env['in.progress'].create(in_progress_dict)
            stage_id = self.env['crm.stage'].search([('name','=','Status')])

            if stage_id:
                lead_vals = {'stage_id' : stage_id.id, 'won_reasion_id': self.won_reason, 'crm_lead_status': 'won'}
                leads.write(lead_vals)
                leads.ehl_renewal_scheduler()
        else:
            if self.won_reason == 'in_progress':

                in_progress_dict = {}

                if self.lead_id.partner_id:
                    in_progress_dict['partner_id'] = self.lead_id.partner_id.id
                    in_progress_dict['primary_sales_person_id'] = self.lead_id.user_id.id
                    in_progress_dict['product_name'] = self.lead_id.products.id
                sale_order_id = self.env['sale.order'].search([('opportunity_id', '=', self.lead_id.id)], limit=1)
                if sale_order_id:
                    purchase = []
                    for record in sale_order_id.order_line:
                        purchase_order_line = {}
                        # purchase_order_line['sources'] = record.product_id.id
                        # purchase_order_line['fees'] = record.price_subtotal

                        # purchase_order_line['product_qty'] = record.product_uom_qty
                        # purchase_order_line['price_unit'] = record.price_unit
                        # purchase_order_line['date_planned'] = self.date_order
                        # purchase_order_line['description'] = record.product_id.name
                        # purchase_order_line['product_uom'] = record.product_uom.id
                        tax_list = []
                        # for tax_id in record.tax_id:
                        #     tax_list.append(tax_id.id)
                        # purchase_order_line['taxes_id'] = [(6, 0, tax_list)]
                        purchase.append((0, 0, purchase_order_line))

                        # in_progress_dict['order_line'] = purchase

                if in_progress_dict:
                    self.env['in.progress'].create(in_progress_dict)
            stage_id = self.env['crm.stage'].search([('name', '=', 'Status')])

            if stage_id:
                lead_vals = {'stage_id' : stage_id.id, 'won_reasion_id': self.won_reason, 'crm_lead_status': 'won'}
                self.lead_id.write(lead_vals)
                self.lead_id.ehl_renewal_scheduler()


        return {'type': 'ir.actions.act_window_close'}