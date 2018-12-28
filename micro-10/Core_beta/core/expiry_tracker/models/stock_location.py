# -*- coding: utf-8 -*-

from odoo import models,api,fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict

class stock_location(models.Model):
    _inherit = 'stock.location'
    
    expiry_days = fields.Integer("Expiry Days Alert",default=-1)
    notification_recipients = fields.Many2many("res.users",'production_lot_res_users_rel','lot_id','user_id','Expiry Notification Recipients')
    product_expiry_line = fields.One2many("stock.product.expiry.line",'location_id','Special Alerts')
    
    @api.model
    def _cron_get_expiry_product(self):
        expiring_products = self.env['expiring.product'].search([])
        
        locations = defaultdict(self.env['expiring.product'].browse)
        for product in expiring_products:
            locations[product.location_id] |= product
        expiry_line_obj = self.env['stock.product.expiry.line']
        location_product_dict = {}
        special_alert_lines = expiry_line_obj.browse()
        
        for location, e_products in locations.iteritems():
            special_alert_products = location.product_expiry_line.mapped('product_id')
            location_product_dict.update({location:{}})
            
            for expiry_product in e_products:
                product = expiry_product.product_id
                if product in special_alert_products:
                    special_alert_lines += location.product_expiry_line.filtered(lambda x:x.product_id.id==product.id)
                else:
                    life_date = expiry_product.expiry_date
                    if (product,life_date) not in location_product_dict[location]:
                        location_product_dict[location].update({(product,life_date):[expiry_product.qty,[expiry_product.lot_id.name]]})
                    else:
                        location_product_dict[location][(product,life_date)][0] = location_product_dict[location][(product,life_date)][0]+expiry_product.qty
                        location_product_dict[location][(product,life_date)][1].append(expiry_product.lot_id.name)   
        
        subject = self.env['ir.config_parameter'].get_param('expiration.product.subject')
        if not subject:
            subject = 'EQUIP Notification for Expiring Products'    
        if location_product_dict:
            expiry_line_obj = self.env['stock.product.expiry.line']
                
            for location,products in location_product_dict.iteritems():
                body_content = "<p>&nbsp;</p><p>Expiring Products for Location "+location.name+' : </p>'
                body_content += "<p>&nbsp;</p><table class='table table-bordered' style='border:1pxsolid'><tbody>"
                for product,content in products.iteritems():
                    serial_no = ', '.join(content[1])
                    recipients = [(6,0,location.notification_recipients.mapped('partner_id').ids)]
#                     recipient_users = [(6,0,location.notification_recipients.ids)]
#                     expiry_line_obj.create({'location_id':location.id,
#                                             'product_id':product[0].id,
#                                             'expiry_days':location.expiry_days,
#                                             'notification_recipients':recipient_users,
#                                             'serial_number':serial_no})
                    body_content += """<tr>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            </tr>
                            <tr>"""%(product[0].name,product[1],content[0],serial_no)
                
                body_content += "</tbody></table><p>&nbsp;</p>"
                mail = self.env['mail.mail'].create({'subject':subject,
                                              'body_html':body_content,
                                              'recipient_ids':recipients,
                                              'email_from':self.env.user.email,
                                              })
                mail.send()
        today = datetime.today()
                
        for line in special_alert_lines:
            if not line.notification_recipients or not line.expiry_days or line.expiry_days==-1:
                continue
            
            location_expiry_start = today.strftime("%Y-%m-%d 00:00:00")
            location_expiry_date = today + relativedelta(days=line.expiry_days)
            location_expiry_date = location_expiry_date.strftime("%Y-%m-%d 23:59:59")
            
            quants = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('lot_id.life_date','>=',location_expiry_start),('lot_id.life_date','<=',location_expiry_date),('location_id','=',line.location_id.id)])
            if not quants:
                continue
            body_content = "<p>&nbsp;</p><p>Expiring Products for Location "+line.location_id.name+' : </p>'
            body_content += "<p>&nbsp;</p><table class='table table-bordered' style='border:1pxsolid'><tbody>"
            recipients = [(6,0,line.notification_recipients.mapped('partner_id').ids)]
            for quant in quants:
                body_content += """<tr>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                <td>%s</td>
                                </tr>
                                <tr>"""%(quant.product_id.name,quant.lot_id.life_date,quant.qty,quant.lot_id.name)
                    
            body_content += "</tbody></table><p>&nbsp;</p>"
            mail = self.env['mail.mail'].create({'subject':subject,
                                          'body_html':body_content,
                                          'recipient_ids':recipients,
                                          'email_from':self.env.user.email,
                                          })
            mail.send()

#         locations = self.search([('expiry_days','!=',-1)])
#         today = datetime.today()
#         location_product_dict = {}
#         
#         for location in locations:
#             if not location.notification_recipients:
#                 continue
#             location_expiry_date = today + relativedelta(days=location.expiry_days)
#             location_expiry_date = location_expiry_date.strftime("%Y-%m-%d")
#             location_expiry_start = location_expiry_date+' 00:00:00'
#             location_expiry_end = location_expiry_date+' 23:59:59'
#         
#             quants = self.env['stock.quant'].search([('lot_id.life_date','>=',location_expiry_start),('lot_id.life_date','<=',location_expiry_end),('location_id','=',location.id)])
#             if not quants:
#                 continue
#             location_product_dict.update({location:{}})
#             for quant in quants:
#                 if quant.lot_id.life_date:
#                     life_date = datetime.strptime(quant.lot_id.life_date,'%Y-%m-%d %H:%M:%S')
#                     life_date = life_date.strftime("%d/%m/%Y")
#                 else:
#                     life_date = ''    
#                 if (quant.product_id,life_date) not in location_product_dict[location]:
#                     location_product_dict[location].update({(quant.product_id,life_date):[quant.qty,[quant.lot_id.name]]})
#                 else:
#                     location_product_dict[location][(quant.product_id,life_date)][0] = location_product_dict[location][(quant.product_id,life_date)][0]+quant.qty
#                     location_product_dict[location][(quant.product_id,life_date)][1].append(quant.lot_id.name)
                    
    
                
        return True
    