# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    contract_id = fields.Many2one('account.invoice', string="Project")
    cost_element_id1 = fields.Many2one('project.cost_element', domain=[('level', '=', '1')], string='Cost Element 1')
    cost_element_id2 = fields.Many2one('project.cost_element', domain=[('level', '=', '2')], string='Cost Element 2')
    cost_element_id3 = fields.Many2one('project.cost_element', domain=[('level', '=', '3')], string='Cost Element 3')
    cost_element_code_sub = fields.Char(string='Cost Element Code', compute='_onchange_element_code', store=True)

    @api.multi
    @api.depends('cost_element_id1', 'cost_element_id2', 'cost_element_id3')
    def _onchange_element_code(self):
        for record in self:
            result = ''
            if record.cost_element_id1 and record.cost_element_id1.cost_element_code:
                result += record.cost_element_id1.cost_element_code + "-"
            if record.cost_element_id2 and record.cost_element_id2.cost_element_code:
                result += record.cost_element_id2.cost_element_code + "-"
            if record.cost_element_id3 and record.cost_element_id3.cost_element_code:
                result += record.cost_element_id3.cost_element_code
            record.cost_element_code_sub = result

    @api.onchange('cost_element_id1')
    def onchanger_cost_element_id1(self):
        domain2 = []
        domain3 = []

        if self.cost_element_id1.id:
            domain2.append(('id', 'in', [line.id for line in self.env['project.cost_element'].search(
                [('parent_cost_element', '=', self.cost_element_id1.id)])]))
            domain3.append(('level', '=', '3'))
            return {'domain': {'cost_element_id2': domain2, 'cost_element_id3': domain3}}

    @api.onchange('cost_element_id2')
    def onchanger_cost_element_id2(self):
        domain1 = []
        domain3 = []

        if self.cost_element_id2.id:
            domain1.append(('id', 'in', [line.id for line in self.env['project.cost_element'].search(
                [('id', '=', self.cost_element_id2.parent_cost_element.id)])]))
            domain3.append(('id', 'in', [line.id for line in self.env['project.cost_element'].search(
                [('parent_cost_element', '=', self.cost_element_id2.id)])]))
            return {'domain': {'cost_element_id1': domain1, 'cost_element_id3': domain3}}

    @api.onchange('cost_element_id3')
    def onchanger_cost_element_id3(self):
        domain2 = []
        domain1 = []

        if self.cost_element_id3.id:
            domain2.append(('id', 'in', [line.id for line in self.env['project.cost_element'].search(
                [('id', '=', self.cost_element_id3.parent_cost_element.id)])]))
            domain1.append(('level', '=', '1'))
            return {'domain': {'cost_element_id2': domain2, 'cost_element_id1': domain1}}


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    name = fields.Char(string='Description', required=True)
    analytic_distribution_bank_id = fields.Many2one('account.analytic.distribution', 'Analytic Distribution')

    @api.multi
    def create_analytic(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.distribution',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.analytic_distribution_bank_id.id,
            'target': 'new',

        }
