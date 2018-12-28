# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
import datetime
import logging
import time
from odoo.exceptions import except_orm
import pytz

from openerp import api, exceptions, fields, models, _
from ast import literal_eval

_logger = logging.getLogger(__name__)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _get_total_bo(self):
        bo_pool = self.env['sale.order']
        for obj in self:
            bo_ids = bo_pool.search([
                ('is_booking', '=', True),
                ('project_id', '=', obj.id),
            ])
            if bo_ids:
                obj.total_bo_count = len(bo_ids)
            else:
                obj.total_bo_count = 0

    book_type = fields.Selection(
        selection=[('booking_order', 'Booking Order')],
        string=' Type Of Order', help='Type Of order')
    book_interval = fields.Selection(
        selection=[
            ('weekly', 'Weekly - Once a week'),
            ('twice_weekly', 'Twice weekly - 2 times a week'),
            ('fortnightly', 'Fortnightly - Every 2 weeks'),
            ('monthly', 'Monthly - Once a month'),
            ('bi_mothly', 'Bi-Monthly - Every 2 months'),
            ('quarterly', 'Quarterly - Every 3 months'),
            ('half_yearly', 'Half Yearly - Every 6 months'),
        ], string='Interval Period',
        help='Create booking order on the basis of interval time')
    total_bo_count = fields.Integer(
        string='Total', compute='_get_total_bo',
        help='Total booking order generated for particlular contract.')
    interval_date = fields.Date(string='Weekly Date', help='Weekly Date')
    twice_week_first_date = fields.Date('First Weekly Date')
    twice_week_second_date = fields.Date('Second Weekly Date')
    fort_nightly_date = fields.Date('Fortnightly Date')
    monthly_date = fields.Date('Monthly Date')
    bi_monthly_date = fields.Date('Bi-Monthly Date')
    quarterly_month_date = fields.Date('Quarterly Date')
    half_month_date = fields.Date('Half Yearly Date')
    recurring_booking_order = fields.Boolean(
        'Generate recurring booking order automatically')
    recurring_bo_next_date = fields.Date('Date of Next Booking Order')
    bo_line_ids = fields.One2many(
        comodel_name='bo.account.analytic.line',
        inverse_name='analytic_new_id', string='List of Services',
        help='Add list of services for various interval.')

    @api.onchange('recurring_booking_order', 'book_interval', 'interval_date',
                  'twice_week_first_date', 'twice_week_second_date',
                  'fort_nightly_date', 'monthly_date', 'bi_monthly_date',
                  'quarterly_month_date', 'half_month_date')
    def onchange_recurring_bo(self):
        # if self.date_start and self.recurring_booking_order:
        if self.recurring_booking_order and self.book_interval == 'weekly':
            self.recurring_bo_next_date = self.interval_date
        elif self.recurring_booking_order and self.book_interval == 'twice_weekly':
            self.recurring_bo_next_date = self.twice_week_first_date
        elif self.recurring_booking_order and self.book_interval == 'fortnightly':
            self.recurring_bo_next_date = self.fort_nightly_date
        elif self.recurring_booking_order and self.book_interval == 'monthly':
            self.recurring_bo_next_date = self.monthly_date
        elif self.recurring_booking_order and self.book_interval == 'bi_mothly':
            self.recurring_bo_next_date = self.bi_monthly_date
        elif self.recurring_booking_order and self.book_interval == 'quarterly':
            self.recurring_bo_next_date = self.quarterly_month_date
        elif self.recurring_booking_order and self.book_interval == 'half_yearly':
            self.recurring_bo_next_date = self.half_month_date

    @api.constrains('twice_week_first_date', 'twice_week_second_date')
    def _check_date(self):
        if self.book_interval == 'twice_weekly':
            if self.twice_week_second_date <= self.twice_week_first_date:
                raise exceptions.ValidationError(
                    _("Week Second Date can not less than or equal to Week First Date."))

    def action_bo_history(self):
        action = self.env.ref('booking_service_V2.booking_order_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        if not self.partner_id:
            raise exceptions.UserError(_('Please add partner first.'))
        # action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        action['domain'].append(('project_id', 'child_of', self.id))
        return action

    @api.model
    def _prepare_order_line(self, line, fiscal_position):
        res = line.product_id
        account_id = res.property_account_income_id.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ_id.id
        account_id = fiscal_position.map_account(account_id)

        # tax = line.product_id.taxes_id.filtered(lambda r: r.company_id == line.analytic_account_id.company_id)
        # tax = fiscal_position.map_tax(tax)
        values = {
            # 'name': line.name,
            # 'account_id': account_id,
            # 'account_analytic_id': line.analytic_account_id.id,
            # 'price_unit': line.price_unit or 0.0,
            # 'quantity': line.quantity,
            'product_uom_qty': 1.0,  # line.quantity,
            # 'uos_id': line.uom_id.id or False,
            'product_id': line.product_id.id or False,
            # 'tax_id': [(6, 0, tax.ids)],
        }
        return values

    @api.model
    def _prepare_order_lines(self, contract_line_obj, fiscal_position_id):
        fiscal_position = self.env['account.fiscal.position'].browse(fiscal_position_id)
        order_lines = []
        values = self._prepare_order_line(contract_line_obj, fiscal_position)
        order_lines.append((0, 0, values))
        return order_lines
       # for line in contract_line_obj.recurring_invoice_line_ids:
       #    values = self._prepare_order_line(line, fiscal_position)
       #    order_lines.append((0, 0, values))
       #    return order_lines

    @api.model
    def _prepare_booking_order_data(self, contract, contract_line_obj):

        partner = contract.partner_id

        if not partner:
            raise except_orm(_('No Customer Defined!'), _(
                "You must first select a Customer for Contract %s!") % contract.name)

        bo_obj = self.env['sale.order']

        fpos_id = self.env['account.fiscal.position'].with_context(
            force_company=contract.company_id.id).get_fiscal_position(partner.id)
        partner_payment_term = partner.property_payment_term_id and partner.property_payment_term_id.id or False
        currency_id = False
        if contract.pricelist_id:
            currency_id = contract.pricelist_id.currency_id.id
        elif partner.property_product_pricelist:
            currency_id = partner.property_product_pricelist.currency_id.id
        elif contract.company_id:
            currency_id = contract.company_id.currency_id.id

        st_date = ''
        end_date = ''
        #<t t-esc="'%02d:%02d' % (int(str(o.event_time).split('.')[0]),
        # int(float(str('%.2f' % o.event_time).split('.')[1])/100*60))" />

        local = pytz.timezone (self._context.get('tz') or self.env.user.tz)
        if not contract_line_obj.st_time:
            # st_date = contract_line_obj.recurring_bo_next_date + ' 03:30:00'
            # end_date = contract_line_obj.recurring_bo_next_date + ' 04:30:00'
            st_date = contract_line_obj.recurring_bo_next_date + ' 09:00:00'
            end_date = contract_line_obj.recurring_bo_next_date + ' 10:00:00'
            #convetting time from user zone to UTC
            st_date = fields.Datetime.to_string(
                local.localize(datetime.datetime.strptime(
                    st_date, "%Y-%m-%d %H:%M:%S"), is_dst=None).astimezone (pytz.utc))
            end_date = fields.Datetime.to_string(
                local.localize(datetime.datetime.strptime (
                    end_date, "%Y-%m-%d %H:%M:%S"), is_dst=None).astimezone (pytz.utc))
        else:
            st_date = contract_line_obj.recurring_bo_next_date + ' %02d:%02d:00' %(
                (int(str(contract_line_obj.st_time).split('.')[0])),
                int(float(str('%.2f' % contract_line_obj.st_time).split('.')[1])/100*60))
            end_time_temp = contract_line_obj.st_time + 1
            end_date = contract_line_obj.recurring_bo_next_date + ' %02d:%02d:00' %(
                (int(str(end_time_temp).split('.')[0])),
                int(float(str('%.2f' % end_time_temp).split('.')[1])/100*60))
            # converting time from user timezone to UTC
            st_date = fields.Datetime.to_string(
                local.localize(datetime.datetime.strptime(
                    st_date, "%Y-%m-%d %H:%M:%S"), is_dst=None).astimezone (pytz.utc))
            end_date = fields.Datetime.to_string(
                local.localize(datetime.datetime.strptime (
                    end_date, "%Y-%m-%d %H:%M:%S"), is_dst=None).astimezone (pytz.utc))

        bo = {
            'partner_id': partner.id,
            'currency_id': currency_id,
            'date_order': contract_line_obj.recurring_bo_next_date,
            'analytic_line_id': contract_line_obj.id,
            'origin': contract.code,
            'fiscal_position_id': fpos_id,
            'payment_term_id': partner_payment_term,
            'company_id': contract.company_id.id or False,
            'user_id': contract.manager_id.id or self.env._uid,
            'note': contract.description,
            'is_booking': True,
            'start_date': st_date,
            'end_date': end_date,
            'project_id': contract.id,
        }
        return bo

    @api.model
    def _prepare_booking_order(self, contract_obj, contract_line_obj):
        """docstring for _prepare_booking_order"""
        booking_order = self._prepare_booking_order_data(contract_obj, contract_line_obj)
        booking_order['order_line'] = self._prepare_order_lines(
            contract_line_obj, booking_order['fiscal_position_id'])
        return booking_order

    @api.model
    def _cron_recurring_create_boking_order(self):
        """docstring for _cron_recurring_create_boking_order"""
        accounts = self.browse([])
        accounts._recurring_create_booking_order(automatic=True)

    @api.multi
    def _recurring_create_booking_order(self, automatic=False):
        booking_ids = []
        current_date = time.strftime('%Y-%m-%d')
        contract_line_ids = self.env['bo.account.analytic.line'].search([
            ('recurring_bo_next_date', '<=', current_date),
            ('state', '=', 'open'),
            ('analytic_new_id.recurring_booking_order', '=', True),
            ('analytic_new_id.type', '=', 'contract'),
            ('analytic_new_id.book_type', '=', 'booking_order'),
            ])

        try:
            for contract_line in contract_line_ids:
                bo_values = self._prepare_booking_order(
                    contract_line.analytic_new_id, contract_line)
                booking_ids.append(self.env['sale.order'].create(
                    bo_values))
                next_date = datetime.datetime.strptime(
                    contract_line.recurring_bo_next_date or current_date, "%Y-%m-%d")
                if contract_line.book_interval == 'weekly':
                    interval = 7
                    new_date = next_date + relativedelta(days=+interval)
                    contract_line.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
                elif contract_line.book_interval == 'twice_weekly':
                    interval = 3
                    diff = fields.Date.from_string(
                        contract_line.tree_interval_date2) - fields.Date.from_string(contract_line.tree_interval_date1)
                    interval = diff.days
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

        except Exception:
            if automatic:
                self.env.cr.rollback()
                _logger.exception('Fail to create recurring invoice for contract %s', contract.code)
            else:
                raise

        return booking_ids

       #if self._ids:
       #    contract_ids = self._ids
       #else:
       #    contract_ids = self.search([
       #        ('recurring_bo_next_date', '<=', current_date),
       #        ('state', '=', 'open'),
       #        ('recurring_booking_order', '=', True),
       #        ('type', '=', 'contract'),
       #        ('book_type', '=', 'booking_order'),

       #    ])._ids
       #if contract_ids:
       #    self.env.cr.execute('SELECT company_id, array_agg(id) as ids \
       #                        FROM account_analytic_account WHERE id IN \
       #                        %s GROUP BY company_id', (tuple(contract_ids),))
          # for company_id, ids in self.env.cr.fetchall():
          #     for contract in self.with_context({
          #             'company_id': company_id,
          #             'force_company': company_id}).browse(ids):
          #         # commented due to multiple service in booking order
          #        #try:
          #        #    bo_values = self._prepare_booking_order(contract)
          #        #    booking_ids.append(self.env['sale.order'].create(bo_values))
          #        #    next_date = datetime.datetime.strptime(contract.recurring_bo_next_date or current_date, "%Y-%m-%d")
          #        #    if contract.book_interval == 'weekly':
          #        #        interval = 7
          #        #        new_date = next_date + relativedelta(days=+interval)
          #        #        contract.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
          #        #    elif contract.book_interval == 'twice_weekly':
          #        #        interval = 3
          #        #        diff = fields.Date.from_string(contract.twice_week_second_date) - fields.Date.from_string(contract.twice_week_first_date)
          #        #        interval = diff.days
          #        #        new_date = next_date + relativedelta(days=+interval)
          #        #        contract.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
          #        #    elif contract.book_interval == 'fortnightly':
          #        #        interval = 15
          #        #        new_date = next_date + relativedelta(days=+interval)
          #        #        contract.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
          #        #    elif contract.book_interval == 'monthly':
          #        #        interval = 1
          #        #        new_date = next_date + relativedelta(months=+interval)
          #        #        contract.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
          #        #    elif contract.book_interval == 'bi_mothly':
          #        #        interval = 2
          #        #        new_date = next_date + relativedelta(months=+interval)
          #        #        contract.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
          #        #    elif contract.book_interval == 'quarterly':
          #        #        interval = 3
          #        #        new_date = next_date + relativedelta(months=+interval)
          #        #        contract.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
          #        #    else:
          #        #        interval = 6
          #        #        new_date = next_date + relativedelta(months=+interval)
          #        #        contract.write({'recurring_bo_next_date': new_date.strftime('%Y-%m-%d')})
          #        #    # contract.write({'recurring_next_date': new_date.strftime('%Y-%m-%d')})
          #        #    if automatic:
          #        #        self.env.cr.commit()
          #        #except Exception:
          #        #    if automatic:
          #        #        self.env.cr.rollback()
          #        #        _logger.exception('Fail to create recurring invoice for contract %s', contract.code)
          #        #    else:
          #        #        raise


AccountAnalyticAccount()

class bo_account_analytic_line(models.Model):
    _name = 'bo.account.analytic.line'
    _description = 'Booking Account analytic.line'

    analytic_new_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Ref.', help='Analytic Ref.')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Service', help='Select service from the list.')
   #state = fields.Selection([('template', 'Template'),
   #                          ('draft', 'New'),
   #                          ('open', 'In Progress'),
   #                          ('pending', 'To Renew'),
   #                          ('close', 'Close'),
   #                          ('cancelled', 'Cancelled'),
   #                          ],
   #    realted='analytic_new_id.state', string='State', store=True,
   #    help='Status based on contract', readonly=True, )
    state = fields.Selection(related='analytic_new_id.state',
                             string='State', store=True,
        help='Status based on contract', readonly=True, )

    book_interval = fields.Selection(
        selection=[
            ('weekly', 'Weekly - Once a week'),
            ('twice_weekly', 'Twice weekly - 2 times a week'),
            ('fortnightly', 'Fortnightly - Every 2 weeks'),
            ('monthly', 'Monthly - Once a month'),
            ('bi_mothly', 'Bi-Monthly - Every 2 months'),
            ('quarterly', 'Quarterly - Every 3 months'),
            ('half_yearly', 'Half Yearly - Every 6 months'),
        ], string='Frequency',
        help='Create booking order on the basis of interval time.')
    recurring_bo_next_date = fields.Date(string='Date of Next Booking Order')
    tree_interval_date1 = fields.Date(
        string='Recurring Date', help='Add recurring date')
    tree_interval_date2 = fields.Date(
        string='Recurring Date 2',
        help='This is only applicable if we have frequency is twice weekly.')
    st_time = fields.Float(
        string='Time',
        help='Enter the start time in 24 hr format. \n Eg. 15:30')
    remarks = fields.Char(string='Location', help='Add location')

    @api.onchange('book_interval', 'tree_interval_date1', 'tree_interval_date2')
    def onchange_recurring_bo(self):
        if self.tree_interval_date1:
            self.recurring_bo_next_date = self.tree_interval_date1
        if self.book_interval != 'twice_weekly':
            self.tree_interval_date2 = False

    def view_booking_order(self):
        action = self.env.ref('booking_service_V2.booking_order_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        if not self.analytic_new_id.partner_id:
            raise exceptions.UserError(_('Please add partner first.'))
        #action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        action['domain'].append(('analytic_line_id', '=', self.id))
        return action


    @api.constrains('tree_interval_date1', 'tree_interval_date2', 'book_interval')
    def _check_date(self):
        if self.book_interval == 'twice_weekly':
            if self.book_interval == 'twice_weekly' and not self.tree_interval_date2:
                raise exceptions.ValidationError(
                    _("You must have to enter Recurring Date2 in %s." %(self.product_id.name)))
            if self.tree_interval_date2 <= self.tree_interval_date1:
                raise exceptions.ValidationError(
                    _("Week Recurring Date2 can not less than or equal to Recurring Date."))




bo_account_analytic_line()
