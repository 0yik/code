# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api

class salestarget_achievement__ipt_custom_sales_team(models.Model):
    _inherit = 'crm.team'

    start_date          = fields.Date('Start Date')
    end_date            = fields.Date('End Date')
    team_target         = fields.Float('Sales Team Target', compute='_compute_team')
    team_achievement    = fields.Float('Sales Team Achievement', compute='_compute_team')

    @api.multi
    def _compute_team(self):
        for record in self:
            team_achievement = 0.0
            team_target      = 0.0
            for member in record.member_ids:
                team_achievement += member.achievement
                team_target      += member.sale_target
            record.team_achievement = team_achievement
            record.team_target      = team_target


class salestarget_achievement__ipt_custom_user(models.Model):
    _inherit = 'res.users'

    sale_target     = fields.Float('Sales Target')
    achievement     = fields.Float('Achievement', compute='_compute_achievement', default=0.0)

    @api.multi
    def _compute_achievement(self):
        for record in self:
            achievement = 0.0
            arguments = [
                ('state', '=', 'sale'),
                ('user_id', '=', record.id),
            ]
            if record.sale_team_id and record.sale_team_id.id:
                if record.sale_team_id.start_date:
                    start_date = datetime.strptime(record.sale_team_id.start_date, '%Y-%m-%d')
                    arguments.append(('date_order', '>=', start_date.strftime('%Y-%m-%d 00:00:00')))
                if record.sale_team_id.end_date:
                    end_date = datetime.strptime(record.sale_team_id.end_date, '%Y-%m-%d')
                    arguments.append(('date_order', '<=', end_date.strftime('%Y-%m-%d 23:59:59')))
            orders = self.env['sale.order'].search(arguments)
            for order in orders:
                achievement += order.amount_total
            record.achievement = achievement