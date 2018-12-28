# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintelle.com/>).
#
##############################################################################
from openerp import api, fields, models, _
from openerp.exceptions import UserError


class sale_order_group(models.TransientModel):
    _name = "sale.order.group"
    _description = "Sale Order Merge"


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        context = self._context or {}
        res = super(sale_order_group, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                       toolbar=toolbar, submenu=submenu)
        print "res======",res  
        print "res======",self                                             
        if self._context.get('active_model','') == 'sale.order' and len(self._context.get('active_ids'))<2:
            raise UserError(_('Please select multiple order to merge in the list view !'))
        return res  
        

    @api.multi
    def merge_orders(self):
        sale_obj=self.env['sale.order']
        mod_obj =self.env['ir.model.data']
        if self._context is None:
            self._context = {}
        order_id = sale_obj.do_sale_merge(self._context.get('active_ids'))
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_quotations')
        form_view_id=imd.xmlid_to_res_id('sale.view_order_form')
                
        return  {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [(form_view_id, 'form')],
            'view_id': form_view_id,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'res_id':order_id.id,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
