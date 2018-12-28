# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta


class QuotationContract(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        res = super(QuotationContract, self).action_confirm()
        for record in self:
            job_estimate = self.env['sale.estimate.job'].search([('quotation_id', '=', record.id), ('state', '=', 'quotesend')], limit=1)
            group_product_obj = self.env['group.products']
            contract_obj = self.env['account.analytic.account']
            current_year = datetime.today().year
            if job_estimate:
                if job_estimate.project_id and job_estimate.project_id.user_id:
                    manager_id = job_estimate.project_id.user_id.id
                    budget = '%s %s' % (job_estimate.project_id.name , current_year)
                else:
                    manager_id = False
                    budget = False

                start_date = datetime.strptime(record.confirmation_date,DEFAULT_SERVER_DATETIME_FORMAT)

                if job_estimate.duration_type == 'days':
                    end_date = (start_date + relativedelta(days=job_estimate.duration or 0))
                elif job_estimate.duration_type == 'months':
                    end_date = (start_date + relativedelta(months=job_estimate.duration or 0))
                elif job_estimate.duration_type == 'years':
                    end_date = (start_date + relativedelta(years=job_estimate.duration or 0))
                else:
                    end_date = start_date


                product_budget_vals = []
                products = []


                if job_estimate.labour_estimate_line_ids:
                    total_expect = sum(line.price_subtotal for line in job_estimate.labour_estimate_line_ids)
                else:
                    total_expect = 0

                for material in job_estimate.estimate_ids:
                    if material.product_id.id not in products:
                        group_id = group_product_obj.search([('name', '=', material.product_id.name)], limit=1)
                        if not group_id:
                            group_id = group_product_obj.create({
                                'name': material.product_id.name,
                                'code': material.product_id.barcode or material.product_id.name,
                                'product_ids' : [(4, material.product_id.id)]
                            })

                        product_budget_vals.append((0, 0, {
                            'name'    : budget,
                            'group_product_id': group_id.id,
                            'start_date'      : start_date,
                            'end_date'        : end_date,
                            'planned_amount'  : material.price_unit * material.product_uom_qty,
                        }))
                        products.append(material.product_id.id)

                for over_head in job_estimate.overhead_estimate_line_ids:
                    if over_head.product_id.id not in products:
                        group_id = group_product_obj.search([('name', '=', over_head.product_id.name)], limit=1)
                        if not group_id:
                            group_id = group_product_obj.create({
                                'name': over_head.product_id.name,
                                'code': over_head.product_id.barcode or over_head.product_id.name,
                                'product_ids' : [(4, over_head.product_id.id)]
                            })
                        product_budget_vals.append((0, 0, {
                            'name'    : budget,
                            'group_product_id': group_id.id,
                            'start_date'      : start_date,
                            'end_date'        : end_date,
                            'planned_amount'  : over_head.price_unit * over_head.product_uom_qty,
                        }))
                        products.append(over_head.product_id.id)

                to_invoice = self.env['hr_timesheet_invoice.factor'].search([('name', '=', 'Yes (100%)')])

                contract_vals = {
                    'name'       : record.related_project_id.name,
                    'partner_id' : record.partner_id.id,
                    'type'       : 'contract',
                    'is_project' : True,
                    'manager_id' : manager_id,
                    'code'       : record.name,
                    'company_id' : record.company_id.id,
                    'product_budget_lines' : product_budget_vals,
                    'invoice_on_timesheets': True,
                    'hours_qtt_est'        : total_expect,
                    'pricelist_id'         : record.pricelist_id.id,
                    'to_invoice'           : to_invoice.id
                }
                contract_obj.create(contract_vals)
        return res