# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    wip_account = fields.Many2one('account.account',string='Manufacturing WIP Account')

    @api.model
    def default_get(self, fields):
        res = super(MrpConfigSettings, self).default_get(fields)
        if res:
            mrp = self.search([],order="id desc",limit=1)
            if mrp:
                res['wip_account'] = mrp.wip_account.id
        return res

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def get_debit_move_line(self,amount):
        ManuSetting = self.env['mrp.config.settings'].search([], order="id desc", limit=1)
        move_line_dict = {
            'type': 'src',
            'name': self.name,
            'price': amount * -1,
            'account_id': ManuSetting.wip_account.id,
            'date_maturity' : self.date_start
        }
        return move_line_dict

    def get_credit_move_line(self,amount):
        move_line_dict = {
            'type': 'src',
            'name': self.product_id.name,
            'price_unit': self.product_id.standard_price,
            'quantity': self.product_qty,
            'price': amount * 1,
            'account_id': self.product_id.categ_id.property_stock_valuation_account_id.id,
            'product_id': self.product_id.id,
            'uom_id': self.product_id.uom_id.id,
            'date_maturity': self.date_start
        }
        return move_line_dict

    @api.model
    def line_get_convert(self, line):
        return {
            'date_maturity': line.get('date_maturity', False),
            'name': line['name'],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uom_id', False),
        }

    def button_mark_done(self):
        amount = 0
        self =self.with_context(from_mo=True)
        for line in self.move_raw_ids:
            amount += line.product_id.standard_price * line.product_uom_qty
        super(MrpProduction, self).button_mark_done()
        ManuSetting = self.env['mrp.config.settings'].search([], order="id desc", limit=1)
        if ManuSetting.wip_account:
            iml=[]
            iml.append(self.get_credit_move_line(amount))
            iml.append(self.get_debit_move_line(amount))
            line = [(0, 0, self.line_get_convert(l)) for l in iml]
            journal = self.env['product.category'].search([]).mapped('property_stock_journal').ids
            if not journal:
                raise UserError(_('Please set Journal Account for Product Category'))
            journal_id = journal[0]
            date = self.date_start
            move_vals = {
                'ref': self.name,
                'line_ids': line,
                'journal_id': journal_id,
                'date': date,
                'currency_id': self.company_id.currency_id.id,
            }
            account_move = self.env['account.move']
            move = account_move.create(move_vals)
            move.post()
        else:
            raise UserError(_('Please set Manufacturing WIP Account in Manufacturing Setting'))

class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    def get_credit_move_line(self, line):
        sign = self.state == 'progress' and 1 or -1
        move_line_dict = {
            'type': 'src',
            'name': line.product_id.name,
            'price_unit': line.product_id.standard_price,
            'quantity': self.qty_production * line.product_qty,
            'price': - self.qty_production * line.product_qty * line.product_id.standard_price * sign,
            'account_id': line.product_id.categ_id.property_stock_valuation_account_id.id,
            'product_id': line.product_id.id,
            'uom_id': line.product_id.uom_id.id,
            'date_maturity' : self.date_start
        }
        return move_line_dict

    def get_debit_move_line(self,amount):
        sign = self.state == 'progress' and 1 or -1
        ManuSetting = self.env['mrp.config.settings'].search([],order="id desc",limit=1)
        move_line_dict = {
            'type': 'src',
            'name': 'WO(%s)/%s' % (self.production_id.name, self.display_name),
            'price': amount * sign,
            'account_id': ManuSetting.wip_account.id,
            'date_maturity': self.date_start
        }
        return move_line_dict

    @api.model
    def line_get_convert(self, line):
        return {
            'date_maturity': line.get('date_maturity', False),
            'name': line['name'],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uom_id', False),
        }

    def button_start(self):
        res = super(MrpWorkOrder,self).button_start()
        self.create_account_move_line()
        return res

    def create_account_move_line(self):
        ManuSetting = self.env['mrp.config.settings'].search([], order="id desc", limit=1)
        if ManuSetting.wip_account:
            account_move = self.env['account.move']
            iml =[]
            manu_order = self.production_id
            bom = manu_order.bom_id
            amount = 0
            amount1 = 0
            for line in bom.bom_line_ids:
                product_bom = line.product_id
                operation = line.operation_id
                if operation.name == self.name:
                    if product_bom.categ_id and product_bom.categ_id.property_valuation == 'real_time':
                        amount += self.qty_production * line.product_qty * product_bom.standard_price
                        # iml.append(self.get_credit_move_line(line))
                        #####################
                        for line1 in manu_order.move_raw_ids:
                            if product_bom == line1.product_id:
                                amount1 += line1.product_id.standard_price * line1.product_uom_qty
                        iml.append(manu_order.get_credit_move_line(amount1))

            if iml:
                # iml.append(self.get_debit_move_line(amount))
                #################
                iml.append(manu_order.get_debit_move_line(amount1))
                #################
                line = [(0, 0, self.line_get_convert(l)) for l in iml]
                journal = self.env['product.category'].search([]).mapped('property_stock_journal').ids
                if not journal:
                    raise UserError(_('Please set Journal Account for Product Category'))
                journal_id = journal[0]
                date = self.date_start
                move_vals = {
                    'ref': self.production_id.name,
                    'line_ids': line,
                    'journal_id': journal_id,
                    'date': date,
                }
                move = account_move.create(move_vals)
                move.post()
        else:
            raise UserError(_('Please set Manufacturing WIP Account in Manufacturing Setting'))

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _create_account_move_line(self, move, credit_account_id, debit_account_id, journal_id):
        context = self._context
        if context.get('from_mo', False):
            return True
        super(StockQuant, self)._create_account_move_line(move, credit_account_id, debit_account_id, journal_id)