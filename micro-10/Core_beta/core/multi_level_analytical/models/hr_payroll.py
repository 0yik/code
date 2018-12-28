from odoo import fields, models,api
from odoo.exceptions import ValidationError


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_human_resource')
        res = super(HrSalaryRule, self).default_get(fields)
        if ('check_distribution' and 'check_analytic_account') in fields:
            res['check_analytic_account'] = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_account_for_human_resource')
            res['check_distribution'] = distribution_check
        if distribution_check:
            if not res.get('analytic_distribution_id'):
                search_analytic_level = self.env['account.analytic.level'].search([('model_id', 'ilike', 'hr')])
                analytical_distribution_line = []
                for analytical_level in search_analytic_level:
                    search_analytic_account = self.env['account.analytic.account'].search(
                        [('level_id', '=', analytical_level.id)], limit=1)
                    search_analytic_account_distribution = self.env['account.analytic.distribution.line'].search(
                        [('salary_rule_id', '=', self.id)], limit=1)
                    analytical_distribution_line.append((0, 0, {
                        'rate': 100,
                        'analytic_level_id': analytical_level.id,
                        'analytic_account_id': search_analytic_account and search_analytic_account.id or ''
                    }))
                res['analytic_distribution_id'] = analytical_distribution_line
        return res

    def _check_distribution_account(self):
        for line in self:
            line.check_analytic_account = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_account_for_human_resource')
            line.check_distribution = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_human_resource')

    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'salary_rule_id', string='Analytic Distribution')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account",
                                                     string='Analytic Account Check Purchase')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')

    def check_lines(self, res):
        for line_item in res.analytic_distribution_id:
            if line_item.rate:
                line_rate = res.analytic_distribution_id.search([('salary_rule_id', '=', res.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
                amount = [a.rate for a in line_rate ]
                if sum(amount) != 100:
                    raise ValidationError(
                        ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

    @api.model
    def create(self, values):
        line = super(HrSalaryRule, self).create(values)
        self.check_lines(line)
        return line

    @api.multi
    def write(self, values):
        result = super(HrSalaryRule, self).write(values)
        self.check_lines(self)
        return result

class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_human_resource')
        res = super(HrContract, self).default_get(fields)
        if ('check_distribution' and 'check_analytic_account') in fields:
            res['check_analytic_account'] = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_account_for_human_resource')
            res['check_distribution'] = distribution_check
        if distribution_check:
            search_analytic_level = self.env['account.analytic.level'].search([('model_id', 'ilike', 'hr')])
            analytical_distribution_line = []
            for analytical_level in search_analytic_level:
                search_analytic_account = self.env['account.analytic.account'].search(
                    [('level_id', '=', analytical_level.id)], limit=1)
                analytical_distribution_line.append((0, 0, {
                    'rate': 100,
                    'analytic_level_id': analytical_level.id,
                    'analytic_account_id': search_analytic_account and search_analytic_account.id or ''
                }))
            res['analytic_distribution_id'] = analytical_distribution_line
        return res

    def _check_distribution_account(self):
        for line in self:
            line.check_analytic_account = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_account_for_human_resource')
            line.check_distribution = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_human_resource')

    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'hr_contract_id', string='Analytic Distribution')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account",
                                                     string='Analytic Account Check Purchase')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')

    def check_lines(self, res):
        for line_item in res.analytic_distribution_id:
            if line_item.rate:
                line_rate = res.analytic_distribution_id.search([('hr_contract_id', '=', res.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
                amount = [a.rate for a in line_rate ]
                if sum(amount) != 100:
                    raise ValidationError(
                        ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

    @api.model
    def create(self, values):
        line = super(HrContract, self).create(values)
        self.check_lines(line)
        return line

    @api.multi
    def write(self, values):
        result = super(HrContract, self).write(values)
        self.check_lines(self)
        return result

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.model
    def default_get(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        distribution_check = IrConfigParam.sudo().get_param(
            'multi_level_analytical.analytic_distribution_for_human_resource')
        res = super(HrExpense, self).default_get(fields)
        if ('check_distribution' and 'check_analytic_account') in fields:
            res['check_analytic_account'] = IrConfigParam.sudo().get_param(
                'multi_level_analytical.analytic_account_for_human_resource')
            res['check_distribution'] = distribution_check
        if distribution_check:
            search_analytic_level = self.env['account.analytic.level'].search([('model_id', '=', 'hr.expense')])
            analytical_distribution_line = []
            for analytical_level in search_analytic_level:
                search_analytic_account = self.env['account.analytic.account'].search(
                    [('level_id', '=', analytical_level.id)], limit=1)
                analytical_distribution_line.append((0, 0, {
                    'rate': 100,
                    'analytic_level_id': analytical_level.id,
                    'analytic_account_id': search_analytic_account and search_analytic_account.id or ''
                }))
            res['analytic_distribution_id'] = analytical_distribution_line
        return res

    def _check_distribution_account(self):
        for line in self:
            line.check_analytic_account = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_account_for_human_resource')
            line.check_distribution = self.env['ir.config_parameter'].sudo().get_param(
                'multi_level_analytical.analytic_distribution_for_human_resource')

    analytic_distribution_id = fields.One2many('account.analytic.distribution.line', 'expense_id', string='Analytic Distribution')
    check_analytic_account = fields.Boolean(compute="_check_distribution_account",
                                                     string='Analytic Account Check Purchase')
    check_distribution = fields.Boolean(compute="_check_distribution_account", string='Distribution Check')

    def check_lines(self, res):
        for line_item in res.analytic_distribution_id:
            if line_item.rate:
                line_rate = res.analytic_distribution_id.search([('expense_id', '=', res.id),('analytic_level_id', '=', line_item.analytic_level_id.id)])
                amount = [a.rate for a in line_rate ]
                if sum(amount) != 100:
                    raise ValidationError(
                        ("Sum of the rate should be 100 for analytic account level and related anlytic account"))

    @api.model
    def create(self, values):
        line = super(HrExpense, self).create(values)
        self.check_lines(line)
        return line

    @api.multi
    def write(self, values):
        result = super(HrExpense, self).write(values)
        self.check_lines(self)
        return result