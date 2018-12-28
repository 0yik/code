# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class CostElementReport(models.Model):
    _name = "project.cost_element.report"
    _description = "Cost Element Report"
    _auto = False

    name = fields.Char('Cost element')
    parent_cost_element = fields.Many2one('project.cost_element', 'Parent')
    level = fields.Char('Level')
    amount = fields.Float('Amount')

    _depends = {
        'account.invoice.line': [
            'price_subtotal',
            'cost_element_id',
        ],
        'project.cost_element': [
            'name',
            'parent_cost_element',
            'level',
        ],
    }

    def _select(self):
        select_str = """
                SELECT sub.id, sub.name, sub.parent_cost_element, sub.level, sub.amount
            """
        return select_str

    def _sub_select(self):
        select_str = """
                    SELECT ail.id AS id,
                        ce.name as name,
                        ce.parent_cost_element as parent_cost_element,
                        ce.level as level,
                        ail.price_subtotal as amount
            """
        return select_str

    def _from(self):
        from_str = """
                    FROM project_cost_element ce
                    JOIN account_invoice_line ail ON ail.cost_element_id = ce.id
            """
        return from_str

    def _group_by(self):
        group_by_str = """
                    GROUP BY ail.id, ce.name, ce.parent_cost_element, ce.level, ail.price_subtotal
            """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql = ("""CREATE or REPLACE VIEW %s as (
                %s
                FROM (
                    %s %s %s
                ) AS sub
            )""" % (
            self._table,
            self._select(), self._sub_select(), self._from(), self._group_by()))
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                %s
                FROM (
                    %s %s %s
                ) AS sub
            )""" % (
            self._table,
            self._select(), self._sub_select(), self._from(), self._group_by()))