from odoo import models, fields, api
import datetime,pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class branch_target(models.Model):
    _name    = 'branch.target'

    branch_id       = fields.Many2one('res.branch',string='Branch')
    user_id         = fields.Many2one('res.users','Team Leader')
    member_ids      = fields.Many2many('res.users',string='Members')
    target_id       = fields.One2many('target.achievement','branch_target_id',string='Target & Achivement')
    target          = fields.Float('Target',compute='get_target_current')
    achievement     = fields.Float('Achievement',compute='get_achievement_current')
    active          = fields.Boolean('Active',default=True)

    @api.multi
    def get_target_current(self):
        today = fields.Date.today()
        for record in self:
            if record.target_id:
                line = self.env['target.achievement'].search([('date_from','<=',today),('date_to','>=',today),('branch_target_id','=',record.id)])
                if line:
                    record.target = line[0].target
                else:
                    record.target = 0
            else:
                record.target = 0

    @api.model
    def change_datetime(self,date_order):
        timezone_tz = 'Singapore'
        if self._context.get('tz', 'False'):
            timezone_tz = self._context.get('tz', 'utc')
        local = pytz.timezone(timezone_tz)
        date_order = pytz.utc.localize(
            datetime.datetime.strptime(str(date_order), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).strftime(DEFAULT_SERVER_DATE_FORMAT)
        return date_order

    @api.multi
    def get_achievement_current(self):
        today = fields.Date.today()
        for record in self:
            if record.target_id:
                line = self.env['target.achievement'].search([('date_from', '<=', today), ('date_to', '>=', today),('branch_target_id','=',record.id)])
                if line:
                    line = line[0]
                    achievement = 0.0
                    # date_from = datetime.datetime.strptime(record.date_from, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
                    # date_to = datetime.datetime.strptime(record.date_to, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
                    arguments = [
                        ('state', 'in', ('sale', 'done')),
                        ('state', 'not in', ('draft', 'cancel', 'waiting')),
                    ]
                    sales = self.env['sale.order'].search(arguments).filtered(lambda so: record.change_datetime(so.date_order) >= line.date_from and record.change_datetime(so.date_order) <= line.date_to)
                    if sales:
                        sale_order_ids = sales.filtered(lambda so: so.branch_id.id == record.branch_id.id)
                        if sale_order_ids:
                            for order in sale_order_ids:
                                achievement += order.amount_total
                        record.achievement = achievement
                    args = [('state', 'in', ['paid', 'done', 'invoiced'])]
                    pos = self.env['pos.order'].search(args).filtered(lambda po: record.change_datetime(po.date_order) >= line.date_from and record.change_datetime(po.date_order) <= line.date_to)
                    if pos:
                        pos_order_ids = pos.filtered(
                            lambda pos_order: pos_order.branch_id.id == record.branch_id.id)
                        if pos_order_ids:
                            for order in pos_order_ids:
                                achievement += order.amount_total
                        record.achievement = achievement
                    other_income = self.env['account.voucher'].search([('state', '=', 'posted'), ('date', '>=', line.date_from), ('date', '<=', line.date_to),('branch_id', '=', record.branch_id.id)])
                    if other_income:
                        for voucher in other_income:
                            achievement += voucher.amount
                    record.achievement = achievement
                else:
                    record.achievement = 0
            else:
                record.achievement = 0

class target_achivement(models.Model):
    _name = 'target.achievement'

    date_from   = fields.Date('Date From',required=True)
    date_to     = fields.Date('Date To',required=True)
    target      = fields.Float('Target')
    achievement  = fields.Float('Achivement',compute='get_achivement_branch')
    branch_target_id = fields.Many2one('branch.target')

    @api.model
    def change_datetime(self,date_order):
        timezone_tz = 'Singapore'
        if self._context.get('tz', 'False'):
            timezone_tz = self._context.get('tz', 'utc')
        local = pytz.timezone(timezone_tz)
        date_order = pytz.utc.localize(
            datetime.datetime.strptime(str(date_order), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).strftime(DEFAULT_SERVER_DATE_FORMAT)
        return date_order

    @api.depends('date_from','date_to')
    def get_achivement_branch(self):
        for record in self:
            if record.date_from and record.date_to:
                achievement = 0.0
                # date_from = datetime.datetime.strptime(record.date_from, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
                # date_to = datetime.datetime.strptime(record.date_to, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
                arguments = [
                    ('state', 'in', ('sale', 'done')),
                    ('state', 'not in', ('draft', 'cancel', 'waiting')),
                ]
                sales = self.env['sale.order'].search(arguments).filtered(lambda so: self.change_datetime(so.date_order) >= record.date_from and self.change_datetime(so.date_order) <= record.date_to)
                if sales and self.env.context.get('branch_target_id',False):
                    sale_order_ids = sales.filtered(lambda so: so.branch_id.id == self.env['branch.target'].browse(self.env.context.get('branch_target_id',False)).branch_id.id)
                    if sale_order_ids:
                        for order in sale_order_ids:
                            achievement += order.amount_total
                    record.achievement = achievement
                args = [('state','in',['paid','done','invoiced'])]
                pos = self.env['pos.order'].search(args).filtered(lambda po: self.change_datetime(po.date_order) >= record.date_from and self.change_datetime(po.date_order) <= record.date_to)
                if pos and self.env.context.get('branch_target_id',False):
                    pos_order_ids = pos.filtered(lambda pos_order: pos_order.branch_id.id == self.env['branch.target'].browse(self.env.context.get('branch_target_id',False)).branch_id.id)
                    if pos_order_ids:
                        for order in pos_order_ids:
                            achievement += order.amount_total
                    record.achievement = achievement
                if self.env.context.get('branch_target_id',False):
                    other_income = self.env['account.voucher'].search([('state','=','posted'),('date','>=',record.date_from),('date','<=',record.date_to),('branch_id','=',self.env['branch.target'].browse(self.env.context.get('branch_target_id',False)).branch_id.id)])
                    if other_income:
                        for voucher in other_income:
                            achievement += voucher.amount
                    record.achievement = achievement

class res_users(models.Model):
    _inherit = 'res.users'

    user_target_id  = fields.One2many('user.target','user_id',string='User Target')
    total_target    = fields.Float('Target',compute='get_target')
    total_achievement = fields.Float('Achievement',compute='get_achievement')

    @api.multi
    def get_target(self):
        for record in self:
            total_target = 0
            if record.user_target_id:
                for line in record.user_target_id:
                    total_target += line.target
            record.total_target = total_target

    @api.model
    def change_datetime(self, date_order):
        timezone_tz = 'Singapore'
        if self._context.get('tz', 'False'):
            timezone_tz = self._context.get('tz', 'utc')
        local = pytz.timezone(timezone_tz)
        date_order = pytz.utc.localize(
            datetime.datetime.strptime(str(date_order), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        return date_order

    @api.multi
    def get_achievement(self):
        for record in self:
            total_achievement = 0
            if record.user_target_id:
                for line in record.user_target_id:
                    if line.date_from and line.date_to:
                        achievement = 0.0
                        # date_from = datetime.datetime.strptime(record.date_from, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
                        # date_to = datetime.datetime.strptime(record.date_to, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
                        arguments = [
                            ('state', 'in', ('sale', 'done')),
                            ('state', 'not in', ('draft', 'cancel', 'waiting')),
                        ]
                        sales = self.env['sale.order'].search(arguments).filtered(lambda so: self.change_datetime(so.date_order) >= line.date_from and self.change_datetime(so.date_order) <= line.date_to)
                        if sales:
                            sale_order_ids = sales.filtered(lambda so: so.user_id and so.user_id.id == record.id)
                            if sale_order_ids:
                                for order in sale_order_ids:
                                    achievement += order.amount_total
                            total_achievement = achievement
                        args = [('state', 'in', ['paid', 'done', 'invoiced'])]
                        pos = self.env['pos.order'].search(args).filtered(lambda po: self.change_datetime(po.date_order) >= line.date_from and self.change_datetime(po.date_order) <= line.date_to)
                        if pos:
                            pos_order_ids = pos.filtered(lambda pos_order: pos_order.user_id and pos_order.user_id.id == record.id)
                            if pos_order_ids:
                                for order in pos_order_ids:
                                    achievement += order.amount_total
                            total_achievement = achievement
            record.total_achievement = total_achievement


class user_target(models.Model):
    _name = 'user.target'

    date_from       = fields.Date('Date From')
    date_to         = fields.Date('Date To')
    target          = fields.Float('Target')
    achievement     = fields.Float('Achievement',compute='get_achievement_user')
    user_id         = fields.Many2one('res.users','User')

    @api.model
    def change_datetime(self, date_order):
        timezone_tz = 'Singapore'
        if self._context.get('tz', 'False'):
            timezone_tz = self._context.get('tz', 'utc')
        local = pytz.timezone(timezone_tz)
        date_order = pytz.utc.localize(
            datetime.datetime.strptime(str(date_order), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).strftime(
            DEFAULT_SERVER_DATE_FORMAT)
        return date_order

    def get_achievement_user(self):
        for record in self:
            if record.date_from and record.date_to:
                achievement = 0.0
                # date_from = datetime.datetime.strptime(record.date_from, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
                # date_to = datetime.datetime.strptime(record.date_to, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
                arguments = [
                    ('state', 'in', ('sale', 'done')),
                    ('state', 'not in', ('draft', 'cancel', 'waiting')),
                ]
                sales = self.env['sale.order'].search(arguments).filtered(lambda so: self.change_datetime(so.date_order) >= record.date_from and self.change_datetime(so.date_order) <= record.date_to)
                if sales and self.env.context.get('active_id',False) and self.env.context.get('active_model',False) == 'res.users':
                    sale_order_ids = sales.filtered(lambda so: so.user_id and so.user_id.id  == self.env.context.get('active_id',False))
                    if sale_order_ids:
                        for order in sale_order_ids:
                            achievement += order.amount_total
                    record.achievement = achievement
                args = [('state','in',['paid','done','invoiced'])]
                pos = self.env['pos.order'].search(args).filtered(lambda po: self.change_datetime(po.date_order) >= record.date_from and self.change_datetime(po.date_order) <= record.date_to)
                if pos and self.env.context.get('active_id',False) and self.env.context.get('active_model',False) == 'res.users':
                    pos_order_ids = pos.filtered(lambda pos_order: pos_order.user_id and pos_order.user_id.id == self.env.context.get('active_id',False))
                    if pos_order_ids:
                        for order in pos_order_ids:
                            achievement += order.amount_total
                    record.achievement = achievement

