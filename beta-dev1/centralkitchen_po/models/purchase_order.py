    # -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import xmlrpclib
import xlrd
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    is_send = fields.Boolean('Is Send')

    @api.multi
    def send_order(self):
        for res in self:
            ck_partner_id = self.env.ref('centralkitchen_po.partner_central_kitchen')
            if res.partner_id.id == ck_partner_id.id:
                try:
                    url = 'http://centralkitchen.equiperp.com/'
                    dbname =  'centralkitchen'
                    username =  'admin'
                    pwd = 'admin'
                   
                    sock_common = xmlrpclib.ServerProxy (url + '/xmlrpc/common')
                    uid = sock_common.login(dbname, username, pwd)
                    sock = xmlrpclib.ServerProxy(url + '/xmlrpc/object')
                    partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('name', '=', res.partner_id.company_id.name), ('customer', '=', True)])
                    if partner_id:
                        partner_id = partner_id[0]
                    if not partner_id:
                        partner_id = sock.execute(dbname, uid, pwd, 'res.partner', 'create', {
                            'name': res.partner_id.company_id.name,
                            'customer': True,
                            'is_company': True,
                            })
                    sale_order_vals= {
                        'partner_id': partner_id,
                        'date_order': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'order_line' : []
                        }
                    for line_id in res.order_line:
                        order_line_vals = {}
                        product_id = sock.execute(dbname, uid, pwd, 'product.product', 'search', [('default_code', '=', line_id.product_id.default_code)])
                        if product_id:
                            product_id = product_id[0]
                        if not product_id:
                            product_vals = {
                                'name': line_id.product_id.name,
                                'default_code': line_id.product_id.default_code,
                                'type': line_id.product_id.type,
                                'sale_ok': line_id.product_id.sale_ok,
                                'purchase_ok': line_id.product_id.purchase_ok,
                                'lst_price': line_id.product_id.lst_price,
                                'standard_price': line_id.product_id.standard_price,
                                'purchase_ok': line_id.product_id.purchase_ok,
                            }
                            product_id = sock.execute(dbname, uid, pwd, 'product.product', 'create', product_vals)
                        order_line_vals.update({
                            'product_id': product_id,
                            'product_uom_qty': line_id.product_qty,
                            })
                        sale_order_vals['order_line'].append((0,0, order_line_vals))
                    
                    sale_id = sock.execute(dbname, uid, pwd, 'sale.order', 'create', sale_order_vals)
                    res.is_send = True
                except Exception, e:
                    raise UserError(_(e.faultCode))


