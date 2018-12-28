from odoo import models, fields, api
import datetime,pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class crm_team(models.Model):
    _inherit = 'crm.team'

    target_id = fields.One2many('target.achievement','crm_team_id',string='Target & Achivement')

class target_achivement(models.Model):
    _name = 'target.achievement'

    date_from   = fields.Date('Date From',required=True)
    date_to     = fields.Date('Date To',required=True)
    target      = fields.Float('Target')
    achievement  = fields.Float('Achivement',compute='get_achivement_branch')
    branch_id   = fields.Many2many('res.branch',string='Branch',required=True)
    crm_team_id = fields.Many2one('crm.team')

    @api.model
    def change_datetime(self,date_order):
        timezone_tz = 'Singapore'
        if self._context.get('tz', 'False'):
            timezone_tz = self._context.get('tz', 'utc')
        local = pytz.timezone(timezone_tz)
        date_order = pytz.utc.localize(
            datetime.datetime.strptime(str(date_order), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).strftime(DEFAULT_SERVER_DATE_FORMAT)
        return date_order

    @api.depends('date_from','date_to','branch_id')
    def get_achivement_branch(self):
        for record in self:
            if record.date_from and record.date_to and record.branch_id:
                achievement = 0.0
                # date_from = datetime.datetime.strptime(record.date_from, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
                # date_to = datetime.datetime.strptime(record.date_to, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
                arguments = [
                    ('state', 'in', ('sale', 'done')),
                    ('state', 'not in', ('draft', 'cancel', 'waiting')),
                ]
                sales = self.env['sale.order'].search(arguments).filtered(lambda so: self.change_datetime(so.date_order) >= record.date_from and self.change_datetime(so.date_order) <= record.date_to)
                if sales and self.env.context.get('crm_team_id',False):
                    sale_order_ids = sales.filtered(lambda so: so.user_id in self.env['crm.team'].browse(self.env.context.get('crm_team_id',False)).member_ids and so.user_id.branch_id in record.branch_id)
                    if sale_order_ids:
                        for order in sale_order_ids:
                            achievement += order.amount_total
                    record.achievement = achievement
                args = [('state','in',['paid','done','invoiced'])]
                pos = self.env['pos.order'].search(args).filtered(lambda po: self.change_datetime(po.date_order) >= record.date_from and self.change_datetime(po.date_order) <= record.date_to)
                if pos and self.env.context.get('crm_team_id',False):
                    pos_order_ids = pos.filtered(lambda pos_order: pos_order.user_id in self.env['crm.team'].browse(self.env.context.get('crm_team_id',False)).member_ids and pos_order.user_id.branch_id in record.branch_id)
                    if pos_order_ids:
                        for order in pos_order_ids:
                            achievement += order.amount_total
                    record.achievement = achievement

