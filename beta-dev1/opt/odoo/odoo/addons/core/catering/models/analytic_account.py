# -*- coding: utf-8  -*-

import logging
import time
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class timedata(models.Model):
    _name = 'time.time'
    _order = 'name asc'

    name = fields.Char('Time',)
    time = fields.Integer('Time', required=True)
    am_or_pm = fields.Selection([('am', 'AM'), ('pm', 'PM')], default='am')

    @api.onchange('time')
    def _compute_time(self):
        if self.time:
            if self.time > 12 or self.time < 0:
                raise UserError(_('The time is invalid'))

    @api.model
    def create(self, vals):
        name = str(vals.get('time')) + ' ' + vals.get('am_or_pm')
        count = self.search([('name','=',name)])
        if len(count) >= 1:
            raise UserError(_('Time is already exist'))
        vals.update({'name': name})
        res = super(timedata, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        time = vals.get('time', False) and vals.get('time') or self.time
        am_or_pm = vals.get('am_or_pm', False) and vals.get('am_or_pm') or self.am_or_pm
        name = str(time) + ' ' + am_or_pm
        res = super(timedata, self).write(vals)
        self.name = name
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    date_create = fields.Char('Date Create')
    contract_id = fields.Many2one('account.analytic.account', string='Contract')

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _get_no_of_invoices(self):
        for rec in self:
            inv_line = rec.env['account.invoice.line'].search(
                [('account_analytic_id', '=', rec.id), ('partner_id', '=', rec.partner_id.id)])
        inv = [x.invoice_id.id for x in inv_line]
        self.no_of_invoices = len(inv)

    @api.multi
    def _get_no_of_delivery(self):
        for rec in self:
            picking_obj = rec.env['stock.picking'].search([('partner_id', '=', rec.partner_id.id)])
        picking = [x.id for x in picking_obj]
        self.delivery_count = len(picking)

    no_of_invoices = fields.Integer('No Of Invoices', compute='_get_no_of_invoices')
    delivery_count = fields.Integer('No Of Delivery Orders', compute='_get_no_of_delivery')
    mon = fields.Boolean('Monday', default=True)
    tue = fields.Boolean('Tuesday', default=True)
    wed = fields.Boolean('Wednesday', default=True)
    thu = fields.Boolean('Thursday', default=True)
    fri = fields.Boolean('Friday', default=True)
    sat = fields.Boolean('Saturday', default=False)
    sun = fields.Boolean('Sunday', default=False)
    invoice_type = fields.Selection([('monthly', 'Monthly'), ('per_delivery', 'Per Delivery'), ('upfront', 'Upfront')],
                                    string='Invoicing Type')
    delivery_time_id = fields.Many2one('time.time', "Delivery Time  ")
    is_deliviery_order = fields.Boolean('Create Delivery Order')
    invoice_date = fields.Date('Invoice Date')

    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        if self.invoice_date:
            invoice_date = datetime.strptime(self.invoice_date, "%Y-%m-%d")
            self.recurring_next_date = invoice_date + relativedelta(months=+1)

    @api.multi
    def get_related_invoices(self):
        for rec in self:
            inv_line = rec.env['account.invoice.line'].search(
                [('account_analytic_id', '=', rec.id), ('partner_id', '=', rec.partner_id.id)])
        inv = [x.invoice_id.id for x in inv_line]
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        action['domain'] = [('id', 'in', inv)]
        return action

    @api.multi
    def get_delivery_orders(self):
        for rec in self:
            picking_obj = rec.env['stock.picking'].search([('partner_id', '=', rec.partner_id.id)])
        picking = [x.id for x in picking_obj]
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('id', 'in', picking)]
        return action

    @api.model
    def _cron_job_check_valid_contract(self):
        current_date = time.strftime('%Y-%m-%d "%H:%M:%S')
        contracts = self.env['account.analytic.account'].search(
            [('state', '!=', 'close'), ('date_end', '<=', current_date), ('type', '=', 'contract')])
        for contract in contracts:
            contract.write({'state': 'close'})

    @api.model
    def get_location(self, stock_type):
        if stock_type.default_location_src_id:
            location_id = stock_type.default_location_src_id.id
        elif self.partner_id:
            location_id = self.partner_id.property_stock_supplier.id
        else:
            customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()
            location_id = location_id.id
        if stock_type.default_location_dest_id:
            location_dest_id = stock_type.default_location_dest_id.id
        elif self.partner_id:
            location_dest_id = self.partner_id.property_stock_customer.id
        else:
            location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()
            location_dest_id = location_dest_id.id
        return location_id, location_dest_id

    @api.model
    def check_date_delivery_order(self):
        list_dates = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        dates = [date for date in list_dates if eval('self.'+ date)]
        if dates and len(dates) > 0:
            return list_dates
        else:
            raise UserError(_('You must choose a date for Delivery Date'))

    @api.model
    def _cron_job_confirm_delivery_order(self):
        current_date = datetime.now().strftime("%A")[0:3].lower()
        current_time = datetime.now().strftime("%I %p").lower()
        stock_pickings = self.env['stock.picking'].search([('state', '=', 'draft'),('contract_id.delivery_time_id.name','=',current_time), ('date_create', '=', current_date), ('contract_id.state','=','open')])
        for stock_picking in stock_pickings:
            stock_picking.action_confirm()
            stock_picking.force_assign()
            self.create_mo(stock_picking)
            contract = stock_picking.contract_id
            if contract.invoice_type == 'per_delivery':
                contract.create_invoice()

    @api.model
    def create_mo(self,stock_picking):
        if stock_picking.pack_operation_product_ids:
            for pack in stock_picking.pack_operation_product_ids:
                product_id = pack.product_id
                bom = self.env['mrp.bom']._bom_find(product=product_id, picking_type=stock_picking.picking_type_id,
                                                    company_id=self.company_id.id)
                if bom.type == 'normal':
                    bom = bom
                else:
                    bom= False
                if not bom:
                    continue
                vals={
                    'product_id' : product_id.product_tmpl_id.id,
                    'bom_id' : bom.id,
                    'product_qty' : pack.product_qty,
                    'date_planned_start' : datetime.now(),
                    'product_uom_id' : product_id.product_tmpl_id.uom_id.id
                }
                self.env['mrp.production'].create(vals)

    @api.model
    def confirm_delivery_order(self):
        self._cron_job_confirm_delivery_order()

    @api.model
    def find_stock_picking(self,date_create):
        return self.env['stock.picking'].search(
            [('date_create','=',date_create),('partner_id', '=', self.partner_id.id), ('contract_id', '=', self.id)], limit=1)

    @api.model
    def create_delivery_order(self, stock_type, stock_move, ori_vals):
        if stock_type:
            location_id, location_dest_id = self.get_location(stock_type)
            list_dates = self.check_date_delivery_order()
            for date in list_dates:
                vals = {
                    'partner_id': self.partner_id.id,
                    'move_type': 'direct',
                    'picking_type_id': stock_type.id,
                    'priority': '1',
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'origin': 'Contract-' + self.name,
                    'date_create': date,
                    'contract_id': self.id
                }
                stock_picking = self.find_stock_picking(date)
                if (eval('self.' + date)) == False:
                    if stock_picking:
                        stock_picking.unlink()
                    continue
                if stock_picking:
                    stock_picking.write(vals)
                else:
                    stock_picking = stock_picking.create(vals)
                check_recurring_invoice_line_ids = False
                if ori_vals and ori_vals.get('recurring_invoice_line_ids', False) or ori_vals.get(date,False):
                    check_recurring_invoice_line_ids = True
                if check_recurring_invoice_line_ids:
                    if stock_picking.move_lines:
                        stock_picking.move_lines.write({'state': 'draft'})
                        stock_picking.move_lines.unlink()
                    invoice_lines = self.recurring_invoice_line_ids
                    for invoice_line in invoice_lines:
                        values = {
                            'product_id': invoice_line.product_id.id,
                            'picking_id': stock_picking.id,
                            'product_uom_qty': invoice_line.quantity,
                            'state': 'draft',
                            'product_uom': invoice_line.uom_id.id,
                            'location_id': stock_picking.location_id.id,
                            'location_dest_id': stock_picking.location_dest_id.id,
                            'name': invoice_line.product_id.name,
                        }
                        stock_move.create(values)
                if self.state == 'open':
                    self.confirm_delivery_order()

    @api.model
    def check_null_order_lines(self):
        if not self.recurring_invoice_line_ids:
            raise UserError(_('Invoice Lines must be has least one line'))

    @api.model
    def create(self, vals):
        ori_vals = vals
        res = super(AccountAnalyticAccount, self).create(vals)
        if res.invoice_type == 'upfront':
            res.create_invoice()
        stock_move = self.env['stock.move']
        stock_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
        if res.is_deliviery_order:
            res.check_null_order_lines()
            res.create_delivery_order( stock_type, stock_move, ori_vals)
        return res

    @api.multi
    def write(self, vals):
        ori_vals = vals
        res = super(AccountAnalyticAccount, self).write(vals)
        if self.invoice_type == 'upfront':
            self.create_invoice()
        stock_move = self.env['stock.move']
        stock_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
        if self.is_deliviery_order:
            self.check_null_order_lines()
            self.create_delivery_order( stock_type, stock_move, ori_vals)
        return res

    @api.model
    def create_invoice(self):
        invoice_values = self._prepare_invoice(self)
        self.env['account.invoice'].create(invoice_values)

    @api.model
    def _cron_recurring_create_invoice(self):
        accounts = self.browse([])
        accounts._recurring_create_invoice(automatic=True)

    @api.multi
    def _recurring_create_invoice(self, automatic=False):
        invoice_ids = []
        current_date = time.strftime('%Y-%m-%d')
        if self._ids:
            contract_ids = self._ids
        else:
            contract_ids = self.search(
                [('invoice_date', '=', current_date), ('invoice_tye', '=', 'monthly'), ('state', '=', 'open'),
                 ('recurring_invoices', '=', True),
                 ('type', '=', 'contract')])._ids
        if contract_ids:
            self.env.cr.execute(
                'SELECT company_id, array_agg(id) as ids FROM account_analytic_account WHERE id IN %s GROUP BY company_id',
                (tuple(contract_ids),))
            for company_id, ids in self.env.cr.fetchall():
                for contract in self.with_context({'company_id': company_id, 'force_company': company_id}).browse(ids):
                    try:
                        invoice_values = self._prepare_invoice(contract)
                        invoice_ids.append(self.env['account.invoice'].create(invoice_values))
                        current_date = datetime.strptime(current_date, "%Y-%m-%d")
                        new_date = current_date + relativedelta(months=+1)
                        contract.write({'recurring_next_date': new_date.strftime('%Y-%m-%d')})
                        if automatic:
                            self.env.cr.commit()
                    except Exception:
                        if automatic:
                            self.env.cr.rollback()
                            _logger.exception('Fail to create recurring invoice for contract %s', contract.code)
                        else:
                            raise
        return invoice_ids
