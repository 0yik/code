from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.tools import float_is_zero
class PosOrderCategory(models.Model):
    _name = 'pos.order.category'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    notes = fields.Text(string="Notes")
    card_color = fields.Selection([
        ('0', 'White'),
        ('1', 'Grey'),
        ('2', 'Pink'),
        ('3', 'Yellow'),
        ('4', 'Green'),
        ('5', 'Blue'),
        ('6', 'Cyan'),
        ('7', 'Cream'),
        ('8', 'Magenta'),
        ('9', 'Purple'),
        ], 'Card Color in Kitchen')

    @api.model
    def get_current_category(self, category_name , fields , pricelist_id):
        print ">>>>>>>>>>>>>",category_name ,pricelist_id
        category_ids = []
        if category_name == 'din_in_takeAway':
            category_ids = self.search([('name','in',['Dine In','Take Away'])]).ids
        else:
            category_ids.append(self.search([('name', '=', str(category_name))]).id)
        if category_ids:
            domain = [('sale_ok','=',True),('available_in_pos','=',True),('product_order_category_ids','in',category_ids)]
            product_ids = self.env['product.product'].with_context({'pricelist':pricelist_id}).search_read(domain, fields)
            print "SSSSSSSSSS",product_ids
            if product_ids:
                return product_ids
            else:
                return 1
        return 0 

class productProduct(models.Model):
    _inherit = 'product.product'

    product_order_category_ids = fields.Many2many('pos.order.category', 'product_id', 'category_id', string='Product Order Category')

    @api.multi
    def set_all_product_order_category(self):
        product_categories = self.env['pos.order.category'].search([])
        product_categorie_ids = product_categories.mapped(lambda x : x.id)
        for record in self:
            record.write({'product_order_category_ids': [(6, 0, product_categorie_ids)]})

class PosOrder(models.Model):
    _inherit= "pos.order"

    product_order_category_ids = fields.Many2one('pos.order.category', string='Product Order Category')

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        print "EEEEEEEEEEEEEEEEEEEEE" , ui_order, self
        categ_obj = self.env['pos.order.category'].search([('name','=',ui_order.get('popup_option'))], limit=1)
        if categ_obj:
            ui_order['product_order_category_ids'] = categ_obj.id
        default_lines = []
        dive_in_take_lines = []
        if ui_order.get('lines'):
            for line in ui_order.get('lines'):
                if line[2].get('popup_option') and line[2].get('popup_option') == 'dine_in_take_away':
                    dive_in_take_lines.append(line)
                else:
                    default_lines.append(line)
            #create separate order
            vals_new = ui_order
            vals_new['lines'] = dive_in_take_lines
            categ_obj_take = self.env['pos.order.category'].search([('name','=','Take Away')], limit=1)
            if categ_obj_take:
                vals_new['product_order_category_ids'] = categ_obj_take.id
            vals_new['name'] = self.env['ir.sequence'].next_by_code('pos.order')
            prec_acc = self.env['decimal.precision'].precision_get('Account')
            pos_session = self.env['pos.session'].browse(vals_new['pos_session_id'])
            if pos_session.state == 'closing_control' or pos_session.state == 'closed':
                vals_new['pos_session_id'] = self._get_valid_session(vals_new).id
            if dive_in_take_lines:
                pos_order = self.create(vals_new)

                journal_ids = set()
                for payments in pos_order.statement_ids:
                    payments.write({'amount':pos_order.amount_total})

                if pos_session.sequence_number <= vals_new['sequence_number']:
                    pos_session.write({'sequence_number': vals_new['sequence_number'] + 1})
                    pos_session.refresh()
                pos_order.action_pos_order_paid()
        res.update({'lines':default_lines,'product_order_category_ids':categ_obj.id})
        return res

    @api.model
    def _process_order(self, pos_order):
        order = super(PosOrder, self)._process_order(pos_order)
        total_amount = order.amount_total
        change_amount = 0
        if order.statement_ids:
            for payment in order.statement_ids:
                if payment.amount <= 0:
                    change_amount = payment.amount
            for payment in order.statement_ids:
                if payment.amount >= 0:
                    if pos_order.get('popup_option') == 'Staff Meal':
                        if not total_amount:
                            total_amount = pos_order.get('amount_total')
                    if total_amount - change_amount != 0:
                        payment.write({'amount':total_amount - change_amount})
            order.write({'state':'paid'})
        return order