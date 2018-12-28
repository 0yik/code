# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class ArkcoSalesIncentive(models.Model):
    _name = 'sales.incentive'

    name = fields.Char(string='Name')
    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, default=_get_default_team)
    target_group_id = fields.Many2one('target.group', 'Target Group', change_default=True)
    incentive_amount = fields.Float(string='Incentive Amount', compute="_get_incentive_amount", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    status_target = fields.Char(string='Status Target', compute="_get_incentive_amount")
    incentive_line = fields.One2many('sales.incentive.line', 'incentive_id', copy=True)

    @api.multi
    def action_button_confirm(self):
        for rec in self:
    	    rec.write({'state': 'pending'})

    @api.multi
    def action_button_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    @api.onchange('team_id')
    def get_sales_executive(self):
        if self.team_id:
            # import pdb; pdb.set_trace()
            r = []
            for person in self.team_id.member_ids:
                r.append({'user_id':person.id})
            self.update({'incentive_line':r})


    @api.multi
    @api.depends('team_id', 'target_group_id','incentive_line.incentive')
    def _get_incentive_amount(self):
        for rec in self:
            if rec.team_id:
                # import pdb; pdb.set_trace()
                total_sale = 0
                sale_ids = self.env['sale.order'].search([('team_id','=',rec.team_id.id),('state','=','sale')])

                for sale in sale_ids:
                    total_sale += sale.amount_untaxed
                price_list = []

                for line in rec.target_group_id.target_lines:
                    price_list.append(line.max_target)
                    price_list.append(line.min_target)

                if price_list:
                    for line in rec.target_group_id.target_lines:
                        if (total_sale<=line.max_target) and (total_sale>=line.min_target):
                            rec.incentive_amount = line.amount
                        elif (total_sale>max(price_list)) and (max(price_list)==line.max_target):
                            rec.incentive_amount = line.amount
                    if total_sale < min(price_list):
                        rec.status_target = 'Not Achieved'
                    else:
                        rec.status_target = 'Achieved'
            for line in rec.incentive_line:
                if (line.incentive>0) and (line.incentive <= rec.incentive_amount):
                    rec.incentive_amount -= line.incentive

            # if rec.incentive_line.incentive > 0:
            #     import pdb; pdb.set_trace()
            #     incentive = rec.incentive_line.incentive
            #     if rec.incentive_amount > incentive:
            #         rec.incentive_amount -= rec.incentive_amount - incentive



class ArkcoSalesIncentiveLine(models.Model):
    _name = 'sales.incentive.line'
    
    incentive_id = fields.Many2one('sales.incentive', string='Incentive Reference', 
        ondelete='cascade', index=True, copy=False)
    line_team_id = fields.Integer('Sales Team', index=True, related="incentive_id.team_id.id")
    line_status_target = fields.Char('Status Target', index=True, related="incentive_id.status_target")
    user_id = fields.Many2one('res.users', string='Sales Executive', index=True, 
        track_visibility='onchange')    
    total_sales = fields.Float(string='Total Sales', compute="_get_total_sale", store=True)
    incentive = fields.Float(string='Incentive')

    @api.multi
    @api.depends('user_id')
    def _get_total_sale(self):
        for line in self:
            sale_order = self.env['sale.order'].search([('user_id','=',line.user_id.id),('state', '=', 'sale')])
            total_sale_amt = 0.0
            for order in sale_order:
                total_sale_amt += order.amount_untaxed
            line.total_sales = total_sale_amt

    @api.multi
    @api.onchange('incentive')
    def check_incentive_amount(self):
        for rec in self:
            if rec.incentive > 0:
                # import pdb; pdb.set_trace()
                total_incentive_amt = rec.incentive_id.incentive_amount
                if rec.incentive > total_incentive_amt:
                    record = rec
                    raise UserError(
                        _("Applied incentive %s has been reached its Total Incentive Amount %s." %(
                            record.incentive, record.incentive_id.incentive_amount)))
                # else:
                #     if (rec.incentive > 0) and (total_incentive_amt >= rec.incentive):
                #         total_incentive_amt = total_incentive_amt - rec.incentive
                #         rec.incentive_id.update({'incentive_amount': total_incentive_amt})

    @api.model
    def create(self, vals):
        res = super(ArkcoSalesIncentiveLine, self).create(vals)
        for rec in res:
            if rec.incentive > 0:
                # import pdb; pdb.set_trace()
                total_incentive_amt = rec.incentive_id.incentive_amount
                if rec.incentive > total_incentive_amt:
                    raise UserError(
                        _("Applied incentive %s has been reached its Total Incentive Amount %s." %(
                            rec.incentive, rec.incentive_id.incentive_amount)))
                else:
                    if (rec.incentive > 0) and (total_incentive_amt >= rec.incentive):
                        total_incentive_amt = total_incentive_amt - rec.incentive
                        rec.incentive_id.incentive_amount = total_incentive_amt
        return res


    @api.multi
    def write(self, values):
        res = super(ArkcoSalesIncentiveLine, self).write(values)
        for rec in self:
            if 'incentive' in values and (rec.incentive > 0):
                total_incentive_amt = rec.incentive_id.incentive_amount
                if rec.incentive > total_incentive_amt:
                    raise UserError(
                        _("Applied incentive %s has been reached its Total Incentive Amount %s." %(
                            rec.incentive, rec.incentive_id.incentive_amount)))
                else:
                    if (rec.incentive > 0) and (total_incentive_amt >= rec.incentive):
                        total_incentive_amt = total_incentive_amt - rec.incentive
                        rec.incentive_id.incentive_amount = total_incentive_amt
        return res
