from odoo import models, fields, api
import datetime,pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from calendar import monthrange

class crm_team_popup(models.TransientModel):
    _name = 'crm.team.popup'

    @api.model
    def get_branch_id(self):
        if self.env.context.get('active_ids',False) and self.env.context.get('active_model',False) == 'branch.target':
            return self.env['branch.target'].browse(self.env.context.get('active_ids',False)).branch_id
        else:
            return False

    branch_id       = fields.Many2one('res.branch',string='Branch',default=get_branch_id)
    input_method    = fields.Selection([('mothly','Monthly'),('daily','Daily')])
    year_id         = fields.Selection('get_years', string='Year', default=int(fields.Date.today()[0:4]))
    monthy_id       = fields.Selection([(1, 'January'),     (2, 'February'),    (3, 'March'),       (4, 'April'),
                                        (5, 'May'),         (6, 'June'),        (7, 'July'),       (8, 'August'),
                                        (9, 'September'),   (10, 'October'),    (11, 'November'),   (12, 'December'), ], string='Month')

    @api.model
    def get_years(self):
        year_list = []
        for i in range(1990, 2100):
            year_list.append((i, str(i)))
        return year_list

    #change date_order datetime to timezone
    @api.model
    def change_datetime(self,date_order):
        timezone_tz = 'Singapore'
        if self._context.get('tz', 'False'):
            timezone_tz = self._context.get('tz', 'utc')
        local = pytz.timezone(timezone_tz)
        date_order = pytz.utc.localize(
            datetime.datetime.strptime(str(date_order), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local)
        return date_order

    @api.multi
    def print_crm_team(self):
        list = []
        target = []
        achievement = []
        result = {}
        if self.env.context.get('active_id', False) and self.env.context.get('active_model', False) == 'branch.target':
            branch_target_id = self.env['branch.target'].browse(self.env.context.get('active_id', False))
            if self.input_method == 'mothly':
                for i in range(1, 13):
                    month = str(self.year_id) + '-' + str(i)
                    list.append(datetime.datetime.strptime(month, '%Y-%m').strftime('%Y %B'))
                    #Calculate target per day
                    count_day = monthrange(int(self.year_id), i)[1]
                    target_id = self.env['target.achievement'].search(
                        [('date_from', '<=', month + '-1'), ('date_to', '>=', month + '-1')])

                    if target_id:
                        count = 0
                        target_amount = 0
                        for line in target_id:
                            count = (datetime.datetime.strptime(line.date_to,
                                                                DEFAULT_SERVER_DATE_FORMAT) - datetime.datetime.strptime(
                                line.date_from, DEFAULT_SERVER_DATE_FORMAT)).days + 1
                            target_amount += line.target
                        target.append(target_amount / count * count_day)
                    else:
                        target.append(0)
                    #Calculate achievement from SO and POS
                    achievement_amount = 0
                    arguments = [
                        ('state', 'in', ('sale', 'done')),
                        ('state', 'not in', ('draft', 'cancel', 'waiting')),
                    ]
                    sales = self.env['sale.order'].search(arguments).filtered(lambda record:
                         self.change_datetime(record.date_order).year == int(self.year_id) and
                         self.change_datetime(record.date_order).month == i)
                    if sales:
                        sale_order_ids = sales.filtered(lambda record: record.user_id in branch_target_id.member_ids and record.user_id.branch_id.id == self.branch_id.id)
                        if sale_order_ids:
                            for order in sale_order_ids:
                                achievement_amount += order.amount_total

                    args = [('state', 'in', ['paid', 'done', 'invoiced'])]
                    pos = self.env['pos.order'].search(args).filtered(lambda record:
                         self.change_datetime(record.date_order).year == int(self.year_id) and
                         self.change_datetime(record.date_order).month == i)
                    if pos:
                        pos_order_ids = pos.filtered(lambda record: record.user_id in branch_target_id.member_ids and record.user_id.branch_id.id == self.branch_id.id)
                        if pos_order_ids:
                            for order in pos_order_ids:
                                achievement_amount += order.amount_total
                        achievement.append(achievement_amount)
                    else:
                        achievement.append(achievement_amount)


            else:
                count_day = monthrange(int(self.year_id), self.monthy_id)[1]
                for i in range(1, count_day + 1):
                    days = ""
                    days = str(i) + '/' + str(self.monthy_id) + '/' + str(self.year_id)
                    list.append(datetime.datetime.strptime(days,'%d/%m/%Y').strftime('%d/%m/%Y %A'))
                    #calculate target per day
                    target_id = self.env['target.achievement'].search(
                        [('date_from', '<=', datetime.datetime.strptime(days,'%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT)), ('date_to', '>=',datetime.datetime.strptime(days,'%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT))])

                    if target_id:
                        count = 0
                        target_amount = 0
                        for line in target_id:
                            count = (datetime.datetime.strptime(line.date_to,DEFAULT_SERVER_DATE_FORMAT) - datetime.datetime.strptime(
                                line.date_from, DEFAULT_SERVER_DATE_FORMAT)).days + 1
                            target_amount += line.target
                        target.append(target_amount / count)
                    else:
                        target.append(0)

                    #Calculate achievement
                    achievement_amount = 0
                    arguments = [
                        ('state', 'in', ('sale', 'done')),
                        ('state', 'not in', ('draft', 'cancel', 'waiting')),
                    ]
                    sales = self.env['sale.order'].search(arguments).filtered(lambda record:
                          self.change_datetime(record.date_order).strftime(DEFAULT_SERVER_DATE_FORMAT) == datetime.datetime.strptime(days,'%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT))
                    if sales:
                        sale_order_ids = sales.filtered(lambda record: record.user_id in branch_target_id.member_ids and record.user_id.branch_id.id == self.branch_id.id)
                        if sale_order_ids:
                            for order in sale_order_ids:
                                achievement_amount += order.amount_total

                    args = [('state', 'in', ['paid', 'done', 'invoiced'])]
                    pos = self.env['pos.order'].search(args).filtered(lambda record:self.change_datetime(record.date_order).strftime(DEFAULT_SERVER_DATE_FORMAT) == datetime.datetime.strptime(days,'%d/%m/%Y').strftime(DEFAULT_SERVER_DATE_FORMAT))
                    if pos:
                        pos_order_ids = pos.filtered(lambda record: record.user_id in branch_target_id.member_ids and record.user_id.branch_id.id == self.branch_id.id)
                        if pos_order_ids:
                            for order in pos_order_ids:
                                achievement_amount += order.amount_total
                        achievement.append(achievement_amount)
                    else:
                        achievement.append(achievement_amount)

        read_res = self.read()[0]
        read_res.update({'list':list})
        read_res.update({'target':target})
        read_res.update({'achievement':achievement})
        datas = {
            'doc_ids': self.ids,
            'doc_model': 'crm.team.popup',
            'docs': read_res,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pdp_sales_target_achievement.target_achievement_report',
            'datas': datas
        }

class render_report_target(models.AbstractModel):
    _name = 'report.pdp_sales_target_achievement.target_achievement_report'

    @api.model
    def render_html(self, docids, data=None):


        docargs = {
            'doc_ids': docids,
            'doc_model': 'crm.team.popup',
            'docs': self.env['crm.team.popup'].browse(docids),
            'list_date':  data.get('docs').get('list'),
            'target':  data.get('docs').get('target'),
            'achievement':  data.get('docs').get('achievement'),
        }
        return self.env['report'].render('pdp_sales_target_achievement.target_achievement_report', docargs)