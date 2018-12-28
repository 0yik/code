from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo import api, fields, models, SUPERUSER_ID, _


class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create(self, vals):
        res = super(pos_order, self).create(vals)
        res['name'] = vals['name']
        return res

class pos_config(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch','Branch',required=True)

    @api.model
    def create(self, values):
        res = super(pos_config, self).create(values)
        IrSequence = self.env['ir.sequence'].sudo()
        year = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).year
        month = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).month
        val = {
            'name': _('POS Order %s') % res['name'],
            'padding': 5,
            'prefix': "CS/TM/%s/%s%s" % (res['branch_id'].branch, year, month),
            'code': "pos.order",
            'company_id': self.env.user.company_id.id,
        }
        # force sequence_id field to new pos.order sequence
        res['sequence_id'] = IrSequence.create(val).id
        return res

class PosSalesOrder(models.Model):
    _inherit = "pos.sales.order"
    _description = "Create a sale order through point of sale for home delivery"

    @api.model
    def create_pos_sale_order(self, ui_order, note, cashier, client_fields, exp_date):
        wk_exp_date = False
        if exp_date:
            wk_exp_date = (datetime.strptime(exp_date, '%m/%d/%Y')).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if ui_order.get('pos_session_id',False):
            session_obj = self.env['pos.session'].browse(ui_order.get('pos_session_id'))
            ui_order.update({'branch_id':session_obj.branch_id.id})

        vals = {'partner_id':   ui_order['partner_id'] or False,
                'pos_notes': note,
                'user_id': cashier,
                'branch_id':ui_order['branch_id'] or False,
                'client_order_ref': 'Point of sale',
                'validity_date': wk_exp_date,
                }
        if client_fields:
            partner_id = self.env['res.partner'].create(client_fields)
            vals['partner_shipping_id'] = partner_id.id
        order_id = self.env['sale.order'].create(vals)
        for ui_order_line in ui_order['lines']:
            product = self.env['product.product'].browse(int(ui_order_line[2]['product_id']))
            values = {
                'order_id': order_id.id,
                'product_id': ui_order_line[2]['product_id'],
                'product_uom_qty': ui_order_line[2]['qty'],
                'price_unit': ui_order_line[2]['price_unit'],
                'name': product.name,
                'product_uom': product.uom_id.id,
                'discount': ui_order_line[2]['discount'],
            }
            if product.description_sale:
                values['name'] += '\n' + product.description_sale
            order_line = self.env['sale.order.line'].create(values)
            order_line._compute_tax_id()
        return {'name': order_id.name, 'id': order_id.id}

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        year = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).year
        month = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).month
        if vals.get('name', _('New')) == _('New') and vals.get('branch_id'):
            code = self.env['ir.sequence'].next_by_code('sale.order')
            branch_obj = self.env['res.branch'].browse(vals.get('branch_id'))
            vals['name'] = 'QT/TM/'+ str(branch_obj.branch) +'/'+''+ str(year)+''+str(month)+''+ str(code)
        result = super(sale_order, self).create(vals)
        return result

    @api.multi
    def action_confirm(self):
        result = super(sale_order, self).action_confirm()
        year = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).year
        month = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).month
        for order in self: 
            if order.name != _('New'):
                order.write({'name':order.name.replace('QT','SO')})
            else:
                code = self.env['ir.sequence'].next_by_code('sale.order')
                order.write({'name':'SO/TM/'+ str(order.branch_id.branch) +'/'+''+ str(year)+''+str(month)+''+ str(code)})
        for order in self:
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            order.order_line._action_procurement_create()
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return result

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        year = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).year
        month = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).month
        if vals.get('name', _('New')) == _('New'):
            code = self.env['ir.sequence'].next_by_code('purchase.order')
            branch_obj = self.env['res.branch'].browse(vals.get('branch_id'))
            vals['name'] = 'PR/TM/'+ str(branch_obj.branch) +'/'+''+ str(year)+''+str(month)+''+ str(code).replace('PO','')
        return super(purchase_order, self).create(vals)

    @api.multi
    def button_confirm(self):
        result = super(purchase_order,self).button_confirm()
        year = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).year
        month = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).month
        for order in self: 
            if order.name != _('New'):
                order.write({'name':order.name.replace('PR','PO')})
            else:
                code = self.env['ir.sequence'].next_by_code('purchase.order')
                order.write({'name':'SO/TM/'+ str(order.branch_id.branch) +'/'+''+ str(year)+''+str(month)+''+ str(code).replace('PO','')})
        return result


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def create(self, vals):
        year = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).year
        month = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).month
        branch_id = ''
        print "SSSSSSSSSSSSSSSS",vals, self
        if 'origin' in vals.keys():
            branch_id = self.env['sale.order'].search([('name','=',vals['origin'])],limit=1).branch_id.branch
        defaults = self.default_get(['name', 'picking_type_id'])
        if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
            picking_type_id = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id')))
            code = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
            if 'branch_id' in vals.keys():
                branch_obj = self.env['res.branch'].browse(vals.get('branch_id'))
                if picking_type_id.code == 'outgoing':
                    vals['name'] = 'DO/TM/'+ str(branch_obj.branch or '') +'/'+''+ str(year)+''+str(month)+''+ str(code).replace('WH/OUT/','')
                if picking_type_id.code == 'internal':
                    vals['name'] = 'TR/TM/'+ str(branch_obj.branch or '') +'/'+''+ str(year)+''+str(month)+''+ str(code).replace('WH/INT/','')
                if picking_type_id.code == 'incoming':
                    vals['name'] = 'IC/TM/'+ str(branch_obj.branch or '') +'/'+''+ str(year)+''+str(month)+''+ str(code).replace('WH/IN/','')
            else:
                if picking_type_id.code == 'outgoing':
                    vals['name'] = 'DO/TM/'+ str(branch_id) +'/'+''+ str(year)+''+str(month)+''+ str(code).replace('WH/OUT/','')
                if picking_type_id.code == 'internal':
                    vals['name'] = 'TR/TM/'+ str(branch_id) +'/'+''+ str(year)+''+str(month)+''+ str(code).replace('WH/INT/','')
                if picking_type_id.code == 'incoming':
                    vals['name'] = 'IC/TM/'+ str(branch_id) +'/'+''+ str(year)+''+str(month)+''+ str(code).replace('WH/IN/','')
        return super(Picking, self).create(vals)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        year = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).year
        month = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).month
        values = super(AccountMove, self).post()
        new_name = False
        invoice = self._context.get('invoice', False)
        credit_note = self._context.get('voucher_type',False)
        for move in self:
            if move.name == '/':
                new_name = False
            if invoice and invoice.type == 'in_invoice' and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('account.invoice.supplier')
                move.name = 'INV/TM/'+ str(self.branch_id.branch) +'/'+''+ str(year)+''+str(month)+''+ str(new_name)
            if invoice and invoice.type == 'out_invoice' and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('account.invoice')
                move.name = 'CP/TM/'+ str(self.branch_id.branch) +'/'+''+ str(year)+''+str(month)+''+ str(new_name)
            if invoice and invoice.type == 'out_refund' and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('invocie.credit.note')
                move.name = 'CN/TM/'+ str(self.branch_id.branch) +'/'+''+ str(year)+''+str(month)+''+ str(new_name)
            if invoice and invoice.debit_note and invoice.move_name != '/':
                new_name = self.env['ir.sequence'].next_by_code('invocie.debit.note')
                move.name = 'DN/TM/'+ str(self.branch_id.branch) +'/'+''+ str(year)+''+str(month)+''+ str(new_name)
        return values

class PosDeliveryOrder(models.Model):
    _inherit = "pos.delivery.order"

    @api.model
    def create(self, vals):
        response = super(PosDeliveryOrder, self).create(vals)
        year = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).year
        month = datetime.strptime(date.today().strftime('%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT).month
        code = self.env['ir.sequence'].next_by_code('pos.delivery.order')
        response.update({'order_no' : 'DO/TM/POS/'+''+ str(year)+''+str(month)+''+ str(code)})
        return response