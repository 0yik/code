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


class purchase_request_line(models.Model):
    _inherit = 'purchase.request.line'

    asset_id = fields.Many2one('account.asset.asset', 'Asset')
    product_code = fields.Char(related='product_id.product_tmpl_id.default_code', string='Product Code')