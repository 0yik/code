# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountAnalyticLevel(models.Model):
    _name = 'account.analytic.level'

    @api.multi
    def compute_analytic_count(self):
        for record in self:
            record.analytic_account_count = len(self.env['account.analytic.account'].search([('level_id','=',record.id)]))

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    analytic_account_count = fields.Integer(compute='compute_analytic_count', string='# of Analytic Accounts')
    model_id = fields.Many2many('ir.model','account_level_rel', 'account_level_id', 'model_id', 'Applicable on Form')
    analytic_account_prioritization_line = fields.One2many('analytic.account.prioritisation','analytic_level_id', 'Prioritization')

    @api.multi
    def open_analytic_account(self):
        action = self.env.ref('analytic.action_account_analytic_account_form').read()[0]
        action['domain'] = [('level_id', 'in', self.ids)]
        return action

    @api.model
    def default_get(self, fields_list):
        res = super(AccountAnalyticLevel, self).default_get(fields_list)
        IrModel = self.env['ir.model']
        IrValues = self.env['ir.config_parameter']
        model_ids = []
        invoice_model = IrModel.search([('model', '=', 'account.invoice')], limit=1).id
        sale_model = IrModel.search([('model', '=', 'sale.order')], limit=1).id
        point_of_sale_model = IrModel.search([('model', '=', 'pos.order')], limit=1).id
        purchase_model = IrModel.search([('model', '=', 'purchase.order')], limit=1).id
        hr_emp_model = IrModel.search([('model', '=', 'hr.employee')], limit=1).id
        hr_exp_model = IrModel.search([('model', '=', 'hr.expense')], limit=1).id
        inventory_model = IrModel.search([('model', '=', 'stock.move')], limit=1).id
        project_model = IrModel.search([('model', '=', 'project.project')], limit=1).id
        sale_distribution = IrValues.sudo().get_param('multi_level_analytical.analytic_distribution_for_sale')
        purchase_distribution = IrValues.sudo().get_param('multi_level_analytical.analytic_distribution_for_purchases')
        pos_distribution = IrValues.sudo().get_param('multi_level_analytical.analytic_distribution_for_pos')
        hr_distribution = IrValues.sudo().get_param('multi_level_analytical.analytic_distribution_for_human_resource')
        inventory_distribution = IrValues.sudo().get_param('multi_level_analytical.analytic_distribution_for_inventory')
        project_distribution = IrValues.sudo().get_param('multi_level_analytical.analytic_distribution_for_project')
        analytic_account = self.user_has_groups('analytic.group_analytic_accounting')
        if analytic_account:
            model_ids.append(invoice_model)
        if sale_distribution:
            model_ids.append(sale_model)
        if purchase_distribution:
            model_ids.append(purchase_model)
        if hr_distribution:
            model_ids.append(hr_exp_model)
            model_ids.append(hr_emp_model)
        if inventory_distribution:
            model_ids.append(inventory_model)
        if project_distribution:
            model_ids.append(project_model)
        if pos_distribution:
            model_ids.append(point_of_sale_model)
        res['model_id'] = [(6,0, model_ids)]
        return res

AccountAnalyticLevel()

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    level_id = fields.Many2one('account.analytic.level', 'Analytic Category')
    parent_id = fields.Many2one('account.analytic.account', 'Parent Analytic Account')



AccountAnalyticAccount()

class Project(models.Model):
    _inherit = "project.project"

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        project_distribution = self.env['ir.config_parameter'].sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_project')
        if project_distribution:
            analytic_category_search = self.env['account.analytic.level'].search([('name', '=', 'Project')], limit=1)
            project = self.env['project.project'].with_context(active_test=False).search(
                [('analytic_account_id', '=', self.id)])
            if res.analytic_account_id:
                res.analytic_account_id.level_id = analytic_category_search
        return res


class AnalyticAccountPrioritisation(models.Model):
    _name= 'analytic.account.prioritisation'

    analytic_level_id = fields.Many2one('account.analytic.level', 'Analytic Category')
    fields_id = fields.Many2one('ir.model.fields', 'Related Field')
    model_list = fields.Selection([('res.users', 'Users'), ('hr.employee', 'Employee'), ('res.branch', 'Branches'), ('res.company', 'Companies'), ('project.project', 'Project')], 'Models')
    sequence = fields.Integer('Sequence')