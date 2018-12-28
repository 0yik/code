# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from odoo import api, exceptions, fields, models, _, modules

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, values):
        order = super(StockPicking, self).create(values)
        if order.picking_type_id.code in ['outgoing', 'incoming']:
            self.create_auto_mail_activity(order)
        return order
    
    @api.multi
    def create_auto_mail_activity(self, order):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menu_id = self.env['ir.model.data'].get_object_reference('stock', 'all_picking')[1]
        action_id =  self.env['ir.model.data'].get_object_reference('stock','action_picking_tree_all')[1]
        url = base_url + "/web?#id="+ str(order.id) +"&view_type=form&model=stock.picking&menu_id="+str(menu_id)+"&action=" + str(action_id)
        if order.picking_type_id.code =='outgoing':
            name = 'Delivery Order'
            activity_type_id = self.env['mail.activity.type'].search([('name','=','Delivery Order')])
            if not activity_type_id:
                activity_type_id = self.env['mail.activity.type'].create({'name':'Delivery Order','summary':'Follow up Delivery Order Entries'})
        else:
            name = 'Shipment Receipt'
            activity_type_id = self.env['mail.activity.type'].search([('name','=','Shipment Receipt')])
            if not activity_type_id:
                activity_type_id = self.env['mail.activity.type'].create({'name':'Shipment Receipt','summary':'Follow up Shipment Receipt Entries'})

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
        model_id = self.env['ir.model'].search([('model', '=', 'stock.picking')])
        activity_vals = {
            'user_id':self._uid,
            'date_deadline':datetime.today(),
            'activity_type_id':activity_type_id and activity_type_id[0].id,
            'note': note,
            'res_id':order.id,
            'res_model':'stock.picking',
            'res_model_id':model_id.id,
            'summary':activity_type_id.summary
        }
        self.env['mail.activity'].create(activity_vals)
        return True