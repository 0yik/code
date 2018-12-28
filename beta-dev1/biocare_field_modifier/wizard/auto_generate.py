# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import datetime
import time


class AutoGenerate(models.TransientModel):
    _name = 'auto.generate.workorder'
    _description = 'Auto Generate Workorder'

    options = fields.Selection(
        selection=[
            ('weekly', 'Weekly'),
            ('day_15', 'Next 15 Days'),
            ('monthly', 'Monthly'),
        ],
        string='Interval', help='Options: \n \
        If you select Weekly then it will generate workorder for upcoming 7 days.\
        If you select Next 15 Days then it will generate workorder for upcoming 15 days.\
        If you select Monthly then it will generate workorder for whole month.')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
        ], default='draft', string='State',
        help='Identify stage technical field')
    counter = fields.Integer(
        string='Generated Booking Orders', help='Total Generated', readonly=True, )
    date_start = fields.Date(string='Start Date', help='Date Start')
    date_end = fields.Date(string='End Date', help='Date End')

    @api.multi
    def act_close(self):
        return  {'type': 'ir.actions.act_window_close'}

    '''
    @api.multi
    def generate_wo(self):
        """docstring for generate_wo"""
        book_order_pool = self.env['sale.order']
        today_day = fields.Datetime.from_string(fields.Datetime.now())
        for obj in self:
            if obj.options == 'weekly':
                updated_date = (today_day + timedelta(
                    days=7)).replace(hour=23,minute=59,second=59)
                orders = book_order_pool.search([
                    ('date_order', '<=', fields.Datetime.to_string(updated_date)),
                    ('state_booking', 'in', ['draft']),
                    ('is_booking', '=', True),
                ])
                for order in orders:
                    order.action_todo()
            elif obj.options == 'day_15':
                updated_date = (today_day + timedelta(
                    days=15)).replace(hour=23,minute=59,second=59)
                orders = book_order_pool.search([
                    ('date_order', '<=', fields.Datetime.to_string(updated_date)),
                    ('state_booking', 'in', ['draft']),
                    ('is_booking', '=', True),
                ])
                for order in orders:
                    orders.action_todo()
            elif obj.options == 'monthly':
                updated_date = (today_day + relativedelta(months=1)).replace(
                    hour=23,minute=59,second=59)
                orders = book_order_pool.search([
                    ('date_order', '<=', fields.Datetime.to_string(updated_date)),
                    ('state_booking', 'in', ['draft']),
                    ('is_booking', '=', True),
                ])
                for order in orders:
                    order.action_todo()
            else:
                exception.UserError(_("Wrong Interval Selected."))
            obj.state = 'done'
            obj.counter = len(orders)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'auto.generate.workorder',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': obj.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    '''
    @api.multi
    def generate_wo(self):
        """docstring for generate_wo"""
        book_order_pool = self.env['sale.order']
        today_day = fields.Datetime.from_string(fields.Datetime.now())
        #book_contract = self.env['account.analytic.account']
        book_contract_line = self.env['bo.account.analytic.line']
        current_date =  time.strftime('%Y-%m-%d')
        for obj in self:
            if obj.date_start >= obj.date_end:
                raise exceptions.UserError(_('End date can not be same or less than Start Date.'))
            contract_line_ids = book_contract_line.search(
                [('recurring_bo_next_date', '>=', obj.date_start),
                 ('recurring_bo_next_date', '<=', obj.date_end),
                 ('state', '=', 'open'),
                 ('analytic_new_id.recurring_booking_order', '=', True),
                 ('analytic_new_id.type', '=', 'contract'),
                 ('analytic_new_id.book_type', '=', 'booking_order'),
                 ])
            booking_ids = []
            for contract_line in contract_line_ids:
                while (contract_line.recurring_bo_next_date <= obj.date_end):
                    bo_values = contract_line.analytic_new_id._prepare_booking_order(contract_line.analytic_new_id, contract_line)
                    booking_ids.append(self.env['sale.order'].create(bo_values))
                    next_date = datetime.datetime.strptime(contract_line.recurring_bo_next_date or current_date, "%Y-%m-%d")
                    if contract_line.book_interval == 'weekly':
                        interval = 7
                        new_date = next_date + relativedelta(days=+interval)
                        contract_line.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
                    elif contract_line.book_interval == 'twice_weekly':
                        interval = 3
                        new_date = next_date + relativedelta(days=+interval)
                        contract_line.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
                    elif contract_line.book_interval == 'fortnightly':
                        interval = 15
                        new_date = next_date + relativedelta(days=+interval)
                        contract_line.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
                    elif contract_line.book_interval == 'monthly':
                        interval = 1
                        new_date = next_date + relativedelta(months=+interval)
                        contract_line.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
                    elif contract_line.book_interval == 'bi_mothly':
                        interval = 2
                        new_date = next_date + relativedelta(months=+interval)
                        contract_line.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
                    elif contract_line.book_interval == 'quarterly':
                        interval = 3
                        new_date = next_date + relativedelta(months=+interval)
                        contract_line.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
                    else:
                        interval = 6
                        new_date = next_date + relativedelta(months=+interval)
                        contract_line.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
                    self.env.cr.commit()


            obj.state = 'done'
            obj.counter = len(booking_ids)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'auto.generate.workorder',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': obj.id,
            'views': [(False, 'form')],
            'target': 'new',
        }


AutoGenerate()
