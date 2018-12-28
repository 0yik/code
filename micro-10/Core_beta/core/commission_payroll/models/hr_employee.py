# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def _get_total_sale(self):
        current_date = datetime.today()
        start_date = current_date + relativedelta(day=1)
        end_date = datetime(current_date.year, current_date.month, 1) + relativedelta(months=1, days=-1)
        # ---------------------------------------------

        sale_order_ids = self.env['sale.order'].search(
            [('user_id', '=', self.user_id.id), ('state', 'in', ('sale', 'done')),
             ('confirmation_date', '>=', start_date.strftime("%Y-%m-%d")),
             ('confirmation_date', '<=', end_date.strftime("%Y-%m-%d"))])
        member_sale = 0
        for order in sale_order_ids:
            member_sale += order.amount_untaxed
        #---------------------------------------------

        sale_teams = self.env['crm.team'].search([('user_id', '=', self.user_id.id)])
        leader_sale = 0
        for team in sale_teams:
            sale_order_ids = self.env['sale.order'].search(
                [('team_id', '=', team.id), ('state', 'in', ('sale', 'done')),
                 ('confirmation_date', '>=', start_date.strftime("%Y-%m-%d")),
                 ('confirmation_date', '<=', end_date.strftime("%Y-%m-%d"))])
            team_sale = 0
            for order in sale_order_ids:
                team_sale += order.amount_untaxed
            leader_sale += team_sale
        # ---------------------------------------------

        self.update({'total_sale': member_sale + leader_sale})
        return True

    @api.one
    def _get_emp_commission(self):
        current_date = datetime.today()
        start_date = current_date + relativedelta(day=1)
        end_date = datetime(current_date.year, current_date.month, 1) + relativedelta(months=1, days=-1)
        # ---------------------------------------------

        sale_order_ids = self.env['sale.order'].search(
            [('user_id', '=', self.user_id.id), ('state', 'in', ('sale', 'done')),
             ('confirmation_date', '>=', start_date.strftime("%Y-%m-%d")),
             ('confirmation_date', '<=', end_date.strftime("%Y-%m-%d"))])
        member_sale = 0
        for order in sale_order_ids:
            member_sale += order.amount_untaxed
        print
        print "Member Sale : ", member_sale
        print
        # ---------------------------------------------

        print
        print "Commission Type : ", self.emp_sale_target.commission_type
        print

        member_commission = 0
        if self.emp_sale_target.commission_type == 'amount':
            for target_line in self.emp_sale_target.target_lines:
                if member_sale >= target_line.min_target and member_sale <= target_line.max_target:
                    member_commission = target_line.amount

        if self.emp_sale_target.commission_type == 'percentage':
            for target_line in self.emp_sale_target.target_lines:
                if member_sale >= target_line.min_target and member_sale <= target_line.max_target:
                    member_commission = (member_sale * target_line.amount)/100
        print
        print "Member Commission : ", member_commission
        print
        # ---------------------------------------------

        sale_teams = self.env['crm.team'].search([('user_id', '=', self.user_id.id)])
        leader_commission = 0
        for team in sale_teams:
            sale_order_ids = self.env['sale.order'].search(
                [('team_id', '=', team.id), ('state', 'in', ('sale', 'done')),
                 ('confirmation_date', '>=', start_date.strftime("%Y-%m-%d")),
                 ('confirmation_date', '<=', end_date.strftime("%Y-%m-%d"))])
            team_sale = 0
            for order in sale_order_ids:
                team_sale += order.amount_untaxed
            print
            print "Team Sale : ", team_sale
            print

            print
            print "Commission Type : ", self.emp_sale_target.commission_type
            print

            if self.emp_sale_target.commission_type == 'amount':
                for target_line in self.emp_sale_target.target_lines:
                    if team_sale >= target_line.min_target and team_sale <= target_line.max_target:
                        leader_commission += target_line.amount

            if self.emp_sale_target.commission_type == 'percentage':
                for target_line in self.emp_sale_target.target_lines:
                    if team_sale >= target_line.min_target and team_sale <= target_line.max_target:
                        leader_commission += (team_sale * target_line.amount)/100
        print
        print "Leader Sale : ", leader_commission
        print
        # ---------------------------------------------

        self.update({'emp_commission': member_commission + leader_commission})
        print
        print "Total Employee Commission : ", member_commission + leader_commission
        print
        return True


    emp_sale_target = fields.Many2one('target.group', 'Sales Target')
    total_sale = fields.Float('Total Sale', compute='_get_total_sale')
    emp_commission = fields.Float('Sales Commission', compute='_get_emp_commission')


    @api.multi
    def total_sale_order(self):
        current_date = datetime.today()
        start_date = current_date + relativedelta(day=1)
        end_date = datetime(current_date.year, current_date.month, 1) + relativedelta(months=1, days=-1)
        # ---------------------------------------------

        team_ids = self.env['crm.team'].search([('user_id', '=', self.user_id.id)])
        print
        print "Team List : ", team_ids
        print

        team_so_list = []
        for team_id in team_ids:
            team_sale_order = self.env['sale.order'].search(
                [('team_id', '=', team_id.id),
                 ('state', 'in', ('sale', 'done')),
                 ('confirmation_date', '>=', start_date.strftime("%Y-%m-%d")),
                 ('confirmation_date', '<=', end_date.strftime("%Y-%m-%d"))])
            team_so_list = list(team_sale_order.ids)
        print
        print "Team's SOs : ", team_so_list
        print

        person_sale_order = self.env['sale.order'].search(
            [('user_id', '=', self.user_id.id), ('state', 'in', ('sale', 'done')),
             ('confirmation_date', '>=', start_date.strftime("%Y-%m-%d")),
             ('confirmation_date', '<=', end_date.strftime("%Y-%m-%d"))])
        so_list = list(person_sale_order.ids) + list(team_so_list)
        print
        print "Employee's SOs : ", so_list
        print
        action = self.env.ref('sale.action_orders').read()[0]
        action['views'] = [(self.env.ref('sale.view_order_tree').id, 'tree')]
        action['domain'] = str([('id', 'in', so_list)])
        return action
