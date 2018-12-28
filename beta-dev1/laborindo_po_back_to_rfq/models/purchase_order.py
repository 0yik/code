from odoo import models, fields, api

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def write(self,vals):
        if self.order_id.state == 'purchase':
            if vals.get('product_qty',False) or vals.get('price_unit',False) or vals.get('disocunt_po',False) or vals.get('taxes_id',False):
                self.order_id.write({'state':'draft'})
                self.order_id.change_po_name()
        res =super(purchase_order_line, self).write(vals)
        return res

    @api.model
    def create(self,vals):
        res = super(purchase_order_line, self).create(vals)
        if res.order_id and res.order_id.state == 'purchase':
            if not res.product_id.name == 'Down payment':
                if vals.get('product_qty', False) or vals.get('price_unit', False) or vals.get('disocunt_po',False) or vals.get('taxes_id', False):
                    res.order_id.write({'state': 'draft'})
                    res.order_id.change_po_name()
        return res


class additional_charges_po(models.Model):
    _inherit = 'additional.charges.po'

    @api.multi
    def write(self,vals):
        if vals.get('name',False) or vals.get('amount',False):
            if self.purchase_id and self.purchase_id.state == 'purchase':
                self.purchase_id.write({'state':'draft'})
                self.purchase_id.change_po_name()
        res = super(additional_charges_po, self).write(vals)
        return res

    @api.model
    def create(self,vals):
        res = super(additional_charges_po, self).create(vals)
        if res.purchase_id and res.purchase_id.state == 'purchase':
            if vals.get('name', False) or vals.get('amount', False):
                res.purchase_id.write({'state': 'draft'})
                res.purchase_id.change_po_name()
        return res

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def change_po_name(self):
        name_list = self.name.split('-')
        if len(name_list) == 2:
            count = int(name_list[1]) + 1
            rfq_name = name_list[0].split('/')
            self.name = rfq_name[0] + '/RFQ/'+rfq_name[2]+'/'+rfq_name[3]+'/'+rfq_name[4] + '-' + str(count)
        elif len(name_list) == 1:
            rfq_name  = name_list[0].split('/')
            if len(rfq_name) == 5:
                self.name = rfq_name[0] + '/RFQ/'+rfq_name[2]+'/'+rfq_name[3]+'/'+rfq_name[4] +  '-1'
