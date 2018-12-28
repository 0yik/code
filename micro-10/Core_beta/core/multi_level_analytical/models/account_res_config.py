from odoo import fields, models,api

class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    group_analytic_distribution_for_purchases = fields.Boolean('Analytic distribution for purchases', help="Allows you to specify an analytic distribution on purchase order lines.")
    group_analytic_account_for_sales = fields.Boolean('Analytic account for sales', help="Allows you to specify an analytic account on sale order lines.")
    group_analytic_distribution_for_sale = fields.Boolean('Analytic distribution for sales', help="Allows you to specify an analytic distribution on sale order lines.")
    group_analytic_account_for_inventory = fields.Boolean('Analytic account for inventory', help="Allows you to specify an analytic account on inventory.")
    group_analytic_distribution_for_inventory = fields.Boolean('Analytic distribution for inventory', help="Allows you to specify an analytic distribution on inventory.")
    group_analytic_distribution_for_pos= fields.Boolean('Analytic distribution for point of sale', help="Allows you to specify an analytic distribution on point of sale.")
    group_analytic_account_for_human_resource = fields.Boolean('Analytic account for human resource', help="Allows you to specify an analytic account on human resource.")
    group_analytic_distribution_for_human_resource= fields.Boolean('Analytic distribution for human resource', help="Allows you to specify an analytic distribution on human resource.")
    group_analytic_account_for_companies = fields.Boolean('Analytic account for companies', help="Allows you to specify an analytic account on companies.")
    group_analytic_distribution_for_companies= fields.Boolean('Analytic distribution for companies', help="Allows you to specify an analytic distribution on companies.")
    group_analytic_account_for_branches = fields.Boolean('Analytic account for branches', help="Allows you to specify an analytic account on branches.")
    group_analytic_distribution_for_branches = fields.Boolean('Analytic distribution for branches', help="Allows you to specify an analytic distribution on branches.")
    group_analytic_distribution_for_project = fields.Boolean('Analytic distribution for project', help="Allows you to specify an analytic distribution on project.")

    @api.model
    def create(self, vals):
        res = super(AccountConfigSettings, self).create(vals)
        model_ids = []
        IrModel = self.env['ir.model']
        AnalyticCategoryModel = self.env['account.analytic.level']
        PrioritizationModel = self.env['analytic.account.prioritisation']
        invoice_model = IrModel.search([('model', '=', 'account.invoice')], limit = 1).id
        sale_model = IrModel.search([('model', '=', 'sale.order')], limit = 1).id
        point_of_sale_model = IrModel.search([('model', '=', 'pos.order')], limit = 1).id
        purchase_model = IrModel.search([('model', '=', 'purchase.order')], limit = 1).id
        hr_emp_model = IrModel.search([('model', '=', 'hr.employee')], limit = 1).id
        hr_exp_model = IrModel.search([('model', '=', 'hr.expense')], limit = 1).id
        inventory_model = IrModel.search([('model', '=', 'stock.move')], limit = 1).id
        project_model = IrModel.search([('model', '=', 'project.project')], limit = 1).id
        contract_model = IrModel.search([('model', '=', 'hr.contract')], limit = 1).id
        ### ACCOUNTING MODEL
        if res.group_analytic_accounting:
            model_ids.append(invoice_model)
        else:
            index = (invoice_model in model_ids) and model_ids.index(invoice_model) or False
            if index:
                model_ids.remove(index)
        ### SALES MODEL
        if res.group_analytic_distribution_for_sale:
                model_ids.append(sale_model)
        else:
            index = (sale_model in model_ids) and model_ids.index(sale_model) or False
            if index:
                model_ids.remove(index)
        ### POINT OF SALES MODEL
        if res.group_analytic_distribution_for_pos:
            model_ids.append(point_of_sale_model)
        else:
            index = (point_of_sale_model in model_ids) and model_ids.index(point_of_sale_model) or False
            if index:
                model_ids.remove(index)
        ### PURCHASE MODEL
        if res.group_analytic_distribution_for_purchases:
            model_ids.append(purchase_model)
        else:
            index = (purchase_model in model_ids) and model_ids.index(purchase_model) or False
            if index:
                model_ids.remove(index)
        ### INVENTORY MODEL
        if res.group_analytic_distribution_for_inventory:
            model_ids.append(inventory_model)
        else:
            index = (inventory_model in model_ids) and model_ids.index(inventory_model) or False
            if index:
                model_ids.remove(index)
        # ### ACCOUNTING MODEL
        # if res.group_analytic_accounting:
        #     model_ids.append(point_of_sale_model)
        # else:
        #     index = (point_of_sale_model in model_ids) and model_ids.index(point_of_sale_model) or False
        #     if index:
        #         model_ids.remove(index)
        ### HUMAN RESOURCE EMP MODEL
        if res.group_analytic_distribution_for_human_resource:
            model_ids.append(hr_emp_model)
            model_ids.append(hr_exp_model)
        else:
            index = (hr_emp_model in model_ids) and model_ids.index(hr_emp_model) or False
            index_1 = (hr_exp_model in model_ids) and model_ids.index(hr_exp_model) or False
            if index:
                model_ids.remove(index)
            if index_1:
                model_ids.remove(index_1)
        AccountCategorySearch = self.env['account.analytic.level'].search([])
        for analytic_category in AccountCategorySearch:
            analytic_category.model_id = [(6, 0, model_ids)]

        ### ADD THE COMPANY MODEL INTO THE PRIORITIZATION
        category_search = self.env['account.analytic.level'].search([('name', '=', 'Companies')], limit=1)
        company_search = PrioritizationModel.search(
            [('model_list', '=', 'res.company'), ('analytic_level_id', '=', category_search.id)], limit=1)

        if res.group_analytic_distribution_for_companies:
            company_model_search = IrModel.search([('model', '=', 'res.company')], limit=1).id
            partner_field_search = self.env['ir.model.fields'].search(
                [('model_id', '=', company_model_search), ('name', '=', 'partner_id')])

            if not company_search:
                PrioritizationModel.create({
                    'analytic_level_id': category_search.id, 'model_list': 'res.company',
                    'fields_id': partner_field_search.id})
        else:
            if company_search:
                company_search.unlink()

        ### ADD THE BRANCH MODEL INTO THE PRIORITIZATION
        category_search = self.env['account.analytic.level'].search([('name', '=', 'Branches')], limit=1)
        branch_search = PrioritizationModel.search(
            [('model_list', '=', 'res.branch'), ('analytic_level_id', '=', category_search.id)], limit=1)

        if res.group_analytic_distribution_for_branches:
            company_model_search = IrModel.search([('model', '=', 'res.branch')], limit=1).id
            partner_field_search = self.env['ir.model.fields'].search(
                [('model_id', '=', company_model_search), ('name', '=', 'name')])

            if not branch_search:
                PrioritizationModel.create({
                    'analytic_level_id': category_search.id, 'model_list': 'res.branch',
                    'fields_id': partner_field_search.id})
        else:
            if branch_search:
                branch_search.unlink()

        ### BRANCH DISTRIBUTION CHANGES
        category_search = AnalyticCategoryModel.search([('name', '=', 'Project')], limit=1)
        project_search = PrioritizationModel.search(
            [('model_list', '=', 'project.project'), ('analytic_level_id', '=', category_search.id)], limit=1)
        if res.group_analytic_distribution_for_project:
            model_ids.append(project_model)
            if not category_search:
                AnalyticCategoryModel.create({
                    'name' : 'Project',
                    'model_id' : [(6, 0, model_ids)],
                })
            else:
                category_search.model_id = [(6, 0, model_ids)]
            project_model_search = IrModel.search([('model', '=', 'project.project')], limit=1).id
            name_field_search = self.env['ir.model.fields'].search(
                [('model_id', '=', project_model_search), ('name', '=', 'name')])
            if not project_search:
                PrioritizationModel.create({
                    'analytic_level_id': category_search.id,
                    'model_list': 'project.project',
                    'fields_id': name_field_search.id})
        else:
            index = (project_model in model_ids) and model_ids.index(project_model) or False
            if index:
                model_ids.remove(index)
            project_search.unlink()

        ### BRANCH DISTRIBUTION CHANGES
        category_search = AnalyticCategoryModel.search([('name', '=', 'Department')], limit=1)
        contract_search = PrioritizationModel.search(
            [('model_list', '=', 'hr.contract'), ('analytic_level_id', '=', category_search.id)], limit=1)
        if res.group_analytic_distribution_for_human_resource:
            model_ids.append(contract_model)
            if not category_search:
                AnalyticCategoryModel.create({
                    'name': 'Department',
                    'model_id': [(6, 0, set(model_ids))],
                })
            else:
                category_search.model_id = [(6, 0, set(model_ids))]
        else:
            index = (project_model in model_ids) and model_ids.index(project_model) or False
            if index:
                model_ids.remove(index)
            contract_search.unlink()
        return res

    @api.model
    def get_default_analytic_distribution_for_purchases(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        group_analytic_distribution_for_purchases = False
        group_analytic_distribution_for_sale = False
        group_analytic_account_for_sales= False
        group_analytic_account_for_inventory = False
        group_analytic_distribution_for_inventory = False
        group_analytic_distribution_for_pos = False
        group_analytic_account_for_human_resource = False
        group_analytic_distribution_for_human_resource = False
        group_analytic_account_for_companies = False
        group_analytic_distribution_for_companies = False
        group_analytic_account_for_branches = False
        group_analytic_distribution_for_branches = False
        group_analytic_distribution_for_project = False
        if fields:
            group_analytic_distribution_for_purchases = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_distribution_for_purchases')
            group_analytic_distribution_for_sale = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_distribution_for_sale')
            group_analytic_account_for_sales = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_account_for_sales')
            group_analytic_account_for_inventory = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_account_for_inventory')
            group_analytic_distribution_for_inventory = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_distribution_for_inventory')
            group_analytic_distribution_for_pos = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_distribution_for_pos')
            group_analytic_account_for_human_resource = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_account_for_human_resource')
            group_analytic_distribution_for_human_resource = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_distribution_for_human_resource')
            group_analytic_account_for_companies = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_account_for_companies')
            group_analytic_distribution_for_companies = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_distribution_for_companies')
            group_analytic_account_for_branches = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_account_for_branches')
            group_analytic_distribution_for_branches = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_distribution_for_branches')
            group_analytic_distribution_for_project = IrConfigParam.sudo().get_param('multi_level_analytical.analytic_distribution_for_project')

        return {
            'group_analytic_distribution_for_purchases': group_analytic_distribution_for_purchases,
            'group_analytic_distribution_for_sale': group_analytic_distribution_for_sale,
            'group_analytic_account_for_sales': group_analytic_account_for_sales,
            'group_analytic_account_for_inventory': group_analytic_account_for_inventory,
            'group_analytic_distribution_for_inventory': group_analytic_distribution_for_inventory,
            'group_analytic_distribution_for_pos': group_analytic_distribution_for_pos,
            'group_analytic_account_for_human_resource': group_analytic_account_for_human_resource,
            'group_analytic_distribution_for_human_resource': group_analytic_distribution_for_human_resource,
            'group_analytic_account_for_companies': group_analytic_account_for_companies,
            'group_analytic_distribution_for_companies': group_analytic_distribution_for_companies,
            'group_analytic_account_for_branches': group_analytic_account_for_branches,
            'group_analytic_distribution_for_branches': group_analytic_distribution_for_branches,
            'group_analytic_distribution_for_project': group_analytic_distribution_for_project
        }

    @api.multi
    def set_default_analytic_distribution_for_purchases(self):
        IrConfigParam = self.env['ir.config_parameter']
        for model in self:
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_distribution_for_purchases', model.group_analytic_distribution_for_purchases)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_distribution_for_sale', model.group_analytic_distribution_for_sale)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_account_for_sales', model.group_analytic_account_for_sales)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_account_for_inventory', model.group_analytic_account_for_inventory)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_distribution_for_inventory', model.group_analytic_distribution_for_inventory)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_distribution_for_pos', model.group_analytic_distribution_for_pos)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_account_for_human_resource', model.group_analytic_account_for_human_resource)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_distribution_for_human_resource', model.group_analytic_distribution_for_human_resource)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_account_for_companies', model.group_analytic_account_for_companies)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_distribution_for_companies', model.group_analytic_distribution_for_companies)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_account_for_branches', model.group_analytic_account_for_branches)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_distribution_for_branches', model.group_analytic_distribution_for_branches)
            IrConfigParam.sudo().set_param('multi_level_analytical.analytic_distribution_for_project', model.group_analytic_distribution_for_project)
