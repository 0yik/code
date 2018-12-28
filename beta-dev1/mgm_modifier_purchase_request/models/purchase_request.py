from odoo import api, fields, models

class SubDeptMaster(models.Model):
    _name = 'sub.dept.master'

    name = fields.Char('Name')


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    pr_number = fields.Char('PR Number', size=30)
    request_date = fields.Date('Request date')
    due_date = fields.Date('Due date')
    department_id = fields.Many2one('hr.department', 'Department')
    sub_department_id = fields.Many2one('sub.dept.master', 'Sub Department')
    asset_id = fields.Many2one('account.asset.asset', 'Asset')

    @api.onchange('requested_by')
    def onchange_requested_by(self):
        if self.requested_by:
            employee_id = self.env['hr.employee'].search([('user_id', '=', self.requested_by.id)], limit=1)
            if employee_id and employee_id.department_id:
                self.department_id = employee_id.department_id.id



class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'

    def get_product_code(self):
        lst = []
        product_ids = self.env['product.product'].search([])
        for product in product_ids.filtered(lambda r: r.default_code):
            lst.append((product.id, product.default_code))
        return lst


    product_code = fields.Selection(get_product_code, string='Product Code')
    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    # product_code_id = fields.Many2one('purchase.product.code', string='Product Code')

    @api.onchange('product_code_id')
    def onchange_product_code_id(self):
        if self.product_code_id:
            product_id = self.env['product.product'].search([('default_code', '=', self.product_code_id.name)], limit=1)
            if product_id:
                self.product_id = product_id.id

    @api.onchange('product_code')
    def onchange_product_code(self):
        self.product_id = False
        if self.product_code:
            self.product_id = self.product_code


class PurchaseProductCode(models.Model):
    _name = 'purchase.product.code'


    name = fields.Char('Product Code')




