# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintelle.com/>).
#
##############################################################################
from openerp import api, fields, models, _
from openerp.exceptions import UserError

class sale_order_line(models.Model):
    _inherit = "sale.order.line"
    
    requested_date = fields.Date('Requested Date')
    commitment_date = fields.Date('Commitment Date')
    
class stock_move(models.Model):
    _inherit = "stock.move"
    
    requested_date = fields.Date('Requested Date')
    commitment_date = fields.Date('Commitment Date')
    
class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    client_order_ref = fields.Char('Customer Ref')
    
    # this method set the origin of the stock.picking
    @api.model
    def create(self,vals):
        if vals.get('origin'):
            sale = self.env['sale.order'].search([('name','=',vals.get('origin'))])
            if sale:
                if sale.origin:
                    vals.update({'client_order_ref':sale.client_order_ref})
                    return super(stock_picking, self).create(vals)
        return super(stock_picking, self).create(vals)
    
    
class ProcurementOrder(models.Model): 
    _inherit = "procurement.order" 

    # set the requested date and commitment date in move line from sale order line 
    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        if procurement.sale_line_id:
            res.update({
                'requested_date':procurement.sale_line_id.requested_date or False,
                'commitment_date':procurement.sale_line_id.commitment_date or False
            })
        return res
        
class sale_order(models.Model):
    _inherit = "sale.order"
    
    @api.multi
    def set_first_sale_data(self,active_ids):
        res={}
        sale=self.browse(active_ids)[0]
        if sale.state != 'draft':
            raise UserError(_('Sales Order State Must be in Draft !'))
        res={
            'warehouse_id':sale.warehouse_id.id,
            'pricelist_id':sale.pricelist_id.id,
            'partner_id':sale.partner_id.id,
        }
        return res
        
    def check_same_data(self,sale,res):
        if sale.state != 'draft':
            raise UserError(_('All the order must have state in draft !'))
        if sale.partner_id.id != res['partner_id']:
            raise UserError(_('All the order must have same Customer !'))
        if sale.warehouse_id.id != res['warehouse_id']:
            raise UserError(_('All the order must have same Warehouse !'))
        if sale.pricelist_id.id != res['pricelist_id']:
            raise UserError(_('All the order must have same Pricelist !'))
        return True
            
    @api.multi
    def create_sale_order(self,active_ids):
        res=self.set_first_sale_data(active_ids)
        origin=''
        order_ref=''
        for sale in self.browse(active_ids):
            if not origin:
                origin=sale.name
            else:
                origin +=','+sale.name
            
            if not order_ref:
                order_ref = sale.client_order_ref
            else:
                order_ref += ','+sale.client_order_ref
                
            self.check_same_data(sale,res)
            
        vals={'origin':origin,'client_order_ref':order_ref,'partner_id':res['partner_id'],'warehouse_id':res['warehouse_id'],
        'pricelist_id':res['pricelist_id']}
        if vals:
            sale_id=self.create(vals)
            return sale_id
        return False
            
    @api.multi
    def create_sale_line(self,sale_id,active_ids):
        for sale in self.browse(active_ids):
            for line in sale.order_line:
                vals={
                    'product_id':line.product_id and line.product_id.id or False,
                    'name':line.name or '',
                    'product_uom_qty':line.product_uom_qty,
                    'product_uom':line.product_uom and line.product_uom.id or '',
                    'price_unit':line.price_unit or '',
                    'requested_date':line.requested_date or False,
                    'commitment_date':line.commitment_date or False,
                    'tax_id':[(6, 0, map(lambda x:x.id, line.tax_id))],
                    'order_id':sale_id.id or False,
                }
                self.env['sale.order.line'].create(vals)
        return True
    
    @api.multi
    def set_sale_cancle(self,active_ids):
        for sale in self.browse(active_ids):
            sale.write({'state':'cancel'})
        return True        
        
    @api.multi
    def do_sale_merge(self,active_ids):
        sale_id=self.create_sale_order(active_ids)
        self.create_sale_line(sale_id,active_ids)
        self.set_sale_cancle(active_ids)
        return sale_id
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:  
