from odoo import fields, models


class DiscountSaleReport(models.Model):
    _inherit = 'sale.report'

    branch_id = fields.Many2one('res.branch',string='Branch',readonly=True)

    def _select(self):
        res = super(DiscountSaleReport,self)._select()
        select_str = res+""",s.branch_id as branch_id"""
        return select_str

    def _group_by(self):
        res = super(DiscountSaleReport, self)._group_by()
        group_by_str = res + """,s.branch_id"""
        return group_by_str