# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    @api.depends('advance_expense_id', 'advance_expense_id.total_amount')
    def _compute_advance_expense_id(self):
        for rec in self:
            amount = 0.0
            amount = rec.advance_expense_id.total_amount
            rec.advance_amount = amount

    @api.depends('advance_expense_id', 'advance_expense_id.total_amount')
    def _compute_advance_expense_balance(self):
        for rec in self:
            balance = 0.0
            total_spent = 0.0
            if rec.advance_expense_id:
                self_ids = self.search([('advance_expense_id', '=', rec.advance_expense_id.id)])
                for adv in self_ids:
                    total_spent += adv.total_amount
                balance = rec.advance_expense_id.total_amount - total_spent
                rec.advance_amount_balance = balance
            else:
                rec.advance_amount_balance = balance
    
    advance_expense_id = fields.Many2one(
        'advance.expense.line', 
        string='Expense Advance', 
        copy=False
    )
    advance_amount = fields.Float(
        string='Advance Amount', 
        compute='_compute_advance_expense_id', 
        store=True
    )
    advance_currency_id = fields.Many2one(
        'res.currency', 
        string='Expense Advance Currency', 
        related='advance_expense_id.currency_id',
        store=True,
    )
    advance_amount_balance = fields.Float(
        string='Advance Amount Balance', 
        compute='_compute_advance_expense_balance', 
        store=True
    )
    
    @api.multi
    def submit_expenses(self): # Override Odoo method.
        result = super(HrExpense, self).submit_expenses()
        for rec in self:
            if rec.advance_expense_id:
                self_ids = self.search([('advance_expense_id', '=', rec.advance_expense_id.id)])
                total_advance = rec.advance_expense_id.total_amount or 0.0
                selected_advance_sum = 0.0
                for adv in self_ids:
                    selected_advance_sum += adv.total_amount
                if selected_advance_sum == total_advance:
                    rec.advance_expense_id.reambursment = True
        return result
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
