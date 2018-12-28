# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import math, time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class POFabricWizard(models.TransientModel):
    _name = 'po.fabric.wizard'
    
    @api.multi
    def generate_po_fabric(self):
        data = {}
        main_lst = []
        po_list = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        for po in po_list:
            uom_list = list(set([x.product_uom for x in po.order_line]))
            summary_list = []
            for uom in uom_list:
                total_qty = 0.0
                for line in po.order_line:
                    if line.product_uom == uom:
                        total_qty += line.fabric_quantity
                summary_list.append({'uom_id': uom.name, 'quantity': total_qty})
            po_tax_amount = po_net_total = po_total = 0.0
            po_line_list = []
            for line in po.order_line:
                line_dict = {'stk_id': line.ref_no.name,
                             'name': line.name,
                             'fabric_id': line.product_id.name,
                             'col_code': line.col_code,
                             'weight': line.weight,
                             'width': line.width,
                             'colour_name': line.colour_name,
                             'uom': line.product_uom.name,
                             'product_qty': line.fabric_quantity,
                             'price_unit': line.price_unit,
                             'price_subtotal': line.fabric_quantity * line.price_unit,
                             }
                taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.fabric_quantity, product=line.product_id, partner=line.order_id.partner_id)
                po_tax_amount += taxes['total_included'] - taxes['total_excluded']
                po_net_total += taxes['total_excluded']
                po_total += taxes['total_included']
                if len(po_line_list) > 0:
                    count = 0
                    for po_line in po_line_list:
                        if po_line['stk_id'] == line_dict['stk_id'] and po_line['fabric_id'] == line_dict['fabric_id'] and po_line['uom'] == line_dict['uom']:
                            count = 1
                            po_line['product_qty'] += line_dict['product_qty']
                            po_line['price_subtotal'] += line_dict['price_subtotal']
                            
                    if count == 0:
                        po_line_list.append(line_dict)
                else:
                    po_line_list.append(line_dict)
            po_dict = {'date_order': po.date_order,
                       'date_planned': po.date_planned,
                       'name': po.name,
                       'partner_id': po.partner_id.name,
                       'p_street': po.partner_id.street,
                       'p_street2': po.partner_id.street2,
                       'p_city': po.partner_id.city,
                       'p_state': po.partner_id.state_id.name,
                       'p_zip': po.partner_id.zip,
                       'p_country': po.partner_id.country_id.name,
                       'company_id': po.company_id.name,
                       'c_street': po.company_id.street,
                       'c_street2': po.company_id.street2,
                       'c_city': po.company_id.city,
                       'c_state': po.company_id.state_id.name,
                       'c_zip': po.company_id.zip,
                       'c_country': po.company_id.name,
                       'buyer': po.customer_id.name,
                       'delivery': po.delydate,
                       'supp_ref': po.supp_ref,
                       'currency_name': po.currency_id.name,
                       'currency_id': po.currency_id.symbol,
                       'payment_term_id': po.payment_term_id.name,
                       'remarks': po.subject,
                       'sketch': po.order_line[0].ref_no.image_medium,
                       'amount_untaxed': po_net_total,
                       'amount_tax': po_tax_amount,
                       'amount_total': po_total,
                       'state': po.state,
                       'lines': po_line_list,
                       'summary_list': summary_list,
                       'issued_by': po.create_uid.name,
                       'verified_by': po.verified_uid.name,
                       'approved_by': po.write_uid.name if po.state == 'purchase' else '',
                       }
            main_lst.append(po_dict)
        data.update({'get_data': main_lst})
        data.update(self.read([])[0])
        return self.env['report'].get_action([], 'modifier_teo_purchase_order_report.po_fabric_report', data=data)
