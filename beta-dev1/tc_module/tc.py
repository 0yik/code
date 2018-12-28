# -*- encoding: utf-8 -*-


from odoo.osv import fields,models
from odoo import netsvc,api
from odoo.exceptions import ValidationError
from odoo.osv.orm import browse_record_list, browse_record, browse_null
from odoo.tools.translate import _


class terms_condition(osv.osv):
    _name= 'tc.module'


    @api.depends('terms','sale_ord','purchase_ord','accnt_ord','active')
    def sale_ord_confirm(self):
        cr=self._cr
        print "entered into sale ord Push function(module:tc_module)"
        print self.sale_ord
        tc=self.terms
        print self.terms
        if self.sale_ord:
            cr.execute("select * from tc_module where sale_ord='True' and active='True'")
            rec=cr.fetchall()
            print "passed ids"
            if len(rec) > 1:
                raise ValidationError("Already an Record with Sale order exists")
            cr.execute("update sale_order set note='%s' where state='draft'"%tc)
        else:
            cr.execute("update sale_order set note=' ' where state='draft'")
        if self.purchase_ord:
            cr.execute("select * from tc_module where purchase_ord='True' and active='True'")
            rec1=cr.fetchall()
            if len(rec1) > 1:
                raise ValidationError("Already an Record with Purchase order exists")
            cr.execute("update purchase_order set notes='%s' where state='draft'"%tc)
        else:
            cr.execute("update purchase_order set notes=' ' where state='draft'")
        if self.accnt_ord:
            cr.execute("select * from tc_module where accnt_ord='True' and active='True'")
            rec2=cr.fetchall()
            if len(rec2) > 1:
                raise ValidationError("Already an Record with invoice  exists")
            cr.execute("update account_invoice set comment='%s' where state='draft'"%tc)
        else:
            cr.execute("update account_invoice set comment=' ' where state='draft'")



    _columns = {
        'name':fields.char('Name'),
        'terms':fields.text(string='Terms & Condtions'),
        'active':fields.boolean('Active'),
        'sale_ord':fields.boolean('Sale Order & Quotations'),
        'purchase_ord':fields.boolean('Purchase RFQ & Purchase Orders'),
        'accnt_ord':fields.boolean('Invoices'),
        'new_field':fields.char(compute=sale_ord_confirm)
    }


    # _constraints = [(_check_ean_key, 'Error: Already an active record exist', ['active'])]

class sale_rprt(osv.osv):
    _inherit ='sale.order'
    def get_default_note(self,cr,uid,ids):
        print "get default note"
        tc_obj=self.pool.get('tc.module')
        tc_ids=tc_obj.search(cr,uid,[('active','=',True),('sale_ord','=',True)])
        t_id=tc_obj.browse(cr,uid,tc_ids)
        if t_id.sale_ord:
            note=t_id.terms
        else:
            note=None
        return note

    _defaults = {
        'note':get_default_note,
    }



class purchase_rprt(osv.osv):
    _inherit ='purchase.order'
    def get_default_notes(self,cr,uid,ids):
        print "get default note"
        tc_obj=self.pool.get('tc.module')
        tc_ids=tc_obj.search(cr,uid,[('active','=',True),('purchase_ord','=',True)])
        t_id=tc_obj.browse(cr,uid,tc_ids)
        if t_id.purchase_ord:
            note=t_id.terms
        else:
            note=None
        return note

    _defaults = {
        'notes':get_default_notes,
    }



class accnt_rprt(osv.osv):
    _inherit ='account.invoice'

    def get_default_comment(self,cr,uid,ids):
        print "get default note"
        tc_obj=self.pool.get('tc.module')
        tc_ids=tc_obj.search(cr,uid,[('active','=',True),('accnt_ord','=',True)])
        t_id=tc_obj.browse(cr,uid,tc_ids)
        if t_id.accnt_ord:
            note=t_id.terms
        else:
            note=None
        return note

    _defaults = {
        'comment':get_default_comment,
    }

