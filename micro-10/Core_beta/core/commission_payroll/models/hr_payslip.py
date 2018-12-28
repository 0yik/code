#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def get_emp_comm(self):
        start_date = self.date_from
        end_date = self.date_to
        # ---------------------------------------------

        sale_order_ids = self.env['sale.order'].search(
            [('user_id', '=', self.employee_id.user_id.id),
             ('state', 'in', ('sale', 'done')),
             ('confirmation_date', '>=', start_date),
             ('confirmation_date', '<=', end_date)])
        member_sale = 0
        for order in sale_order_ids:
            member_sale += order.amount_untaxed
        print
        print "Member Sale : ", member_sale
        print
        # ---------------------------------------------

        member_commission = 0
        if self.employee_id.emp_sale_target.commission_type == 'amount':
            for target_line in self.employee_id.emp_sale_target.target_lines:
                if member_sale >= target_line.min_target and member_sale <= target_line.max_target:
                    member_commission = target_line.amount

        if self.employee_id.emp_sale_target.commission_type == 'percentage':
            for target_line in self.employee_id.emp_sale_target.target_lines:
                if member_sale >= target_line.min_target and member_sale <= target_line.max_target:
                    member_commission = (member_sale * target_line.amount) / 100
        print
        print "Member Commission : ", member_commission
        print
        # ---------------------------------------------

        sale_teams = self.env['crm.team'].search([('user_id', '=', self.employee_id.user_id.id)])
        leader_commission = 0
        for team in sale_teams:
            sale_order_ids = self.env['sale.order'].search(
                [('team_id', '=', team.id), ('state', 'in', ('sale', 'done')),
                 ('confirmation_date', '>=', start_date),
                 ('confirmation_date', '<=', end_date)])
            team_sale = 0
            for order in sale_order_ids:
                team_sale += order.amount_untaxed

            print
            print "Team Sale : ", team_sale
            print

            print
            print "Commission Type : ", self.employee_id.emp_sale_target.commission_type
            print

            if self.employee_id.emp_sale_target.commission_type == 'amount':
                for target_line in self.employee_id.emp_sale_target.target_lines:
                    if team_sale >= target_line.min_target and team_sale <= target_line.max_target:
                        leader_commission += target_line.amount

            if self.employee_id.emp_sale_target.commission_type == 'percentage':
                for target_line in self.employee_id.emp_sale_target.target_lines:
                    if team_sale >= target_line.min_target and team_sale <= target_line.max_target:
                        leader_commission += (team_sale * target_line.amount) / 100
        print
        print "Leader Commission : ", leader_commission
        print
        # ---------------------------------------------

        self.update({'emp_commission': member_commission + leader_commission})
        print
        print "Employee Commission : ", member_commission + leader_commission
        print
        return True

    emp_commission = fields.Float('Commission', compute='get_emp_comm')

class TargetGroup(models.Model):
    _inherit = 'target.group'

    sales_people = fields.One2many('hr.employee', 'emp_sale_target')