# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from odoo import api, exceptions, fields, models, _, modules

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_approve(self, force=False):
        for record in self:
            record._create_picking()
            if record.company_id.po_lock == 'lock':
                record.write({'state': 'done'})
            if record.approval_id.user_id == self.env.user:
                record.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self)})
            record.shipment_notification_template()
            record.create_auto_mail_activity(record)
        return {}

    @api.multi
    def create_auto_mail_activity(self, order):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env['ir.model.data'].get_object_reference('purchase', 'menu_purchase_rfq')[1]
        action_id = self.env['ir.model.data'].get_object_reference('purchase','purchase_rfq')[1]
        url = base_url + "/web?#id="+ str(order.id) +"&view_type=form&model=purchase.order&menu_id="+str(menu_id)+"&action=" + str(action_id)
        activity_type_id = self.env['mail.activity.type'].search([('name','=','Purchase Order')])
        if not activity_type_id:
            activity_type_id = self.env['mail.activity.type'].create({'name':'Purchase Order','summary':'Follow up Purchase Order Entries'})
        note = """
                <html>
                    <head>
                        Dear %s (requester)
                    </head>
                    <body>
                        <span>
                            You need to follow up the Purchase Order <a href="%s" target="_blank">%s</a> <br/>
                            Thank You,
                        </span>
                    </body> 
                <html>""" % (self.env.user.name, url, order.name)
        model_id = self.env['ir.model'].search([('model', '=', 'purchase.order')])
        activity_vals = {
            'user_id':self._uid,
            'date_deadline':datetime.today(),
            'activity_type_id':activity_type_id and activity_type_id[0].id,
            'note': note,
            'res_id':order.id,
            'res_model':'purchase.order',
            'res_model_id':model_id.id,
            'summary':activity_type_id.summary
        }
        self.env['mail.activity'].create(activity_vals)
        return True