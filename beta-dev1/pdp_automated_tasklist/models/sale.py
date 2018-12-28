# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from odoo import api, exceptions, fields, models, _, modules

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, values):
        order = super(SaleOrder, self).create(values)
        self.create_auto_mail_activity(order)
        return order

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.create_auto_mail_activity(self)
        return res
    
    @api.multi
    def create_auto_mail_activity(self, order):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env['ir.model.data'].get_object_reference('sale', 'menu_sale_order')[1]
        action_id =  self.env['ir.model.data'].get_object_reference('sale','action_orders')[1]
        url = base_url + "/web?#id="+ str(order.id) +"&view_type=form&model=sale.order&menu_id="+str(menu_id)+"&action=" + str(action_id)
        if order.state=='draft':
            name = 'Quotation'
            activity_type_id = self.env['mail.activity.type'].search([('name','=','Quotation')])
            if not activity_type_id:
                activity_type_id = self.env['mail.activity.type'].create({'name':'Quotation','summary':'Follow up Quotation Entries'})
        else:
            name = 'Sale Order'
            activity_type_id = self.env['mail.activity.type'].search([('name','=','Sales Order')])
            if not activity_type_id:
                activity_type_id = self.env['mail.activity.type'].create({'name':'Sales Order','summary':'Follow up Sales Order Entries'})
        note = """
                <html>
                    <head>
                        Dear %s (requester)
                    </head>
                    <body>
                        <span>
                            You need to follow up the %s <a href="%s" target="_blank">%s</a> <br/>
                            Thank You,
                        </span>
                    </body> 
                <html>""" % (self.env.user.name, name, url, order.name)
        model_id = self.env['ir.model'].search([('model', '=', 'sale.order')])
        activity_vals = {
            'user_id':self._uid,
            'date_deadline':datetime.today(),
            'activity_type_id':activity_type_id and activity_type_id[0].id,
            'note': note,
            'res_id':order.id,
            'res_model':'sale.order',
            'res_model_id':model_id.id,
            'summary':activity_type_id.summary
        }
        self.env['mail.activity'].create(activity_vals)
        return True