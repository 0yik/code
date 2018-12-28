# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ArkcoModifierApprovingMatrixRFQ(models.Model):
    _inherit = 'purchase.order'

    
    @api.depends('amount_total','approving_matrix_id')
    def _get_approval_matrix_line(self):
        for rec in self:
            rec.approving_matrix_line_ids = False
            approval_matrix_lines = []
            if rec.approving_matrix_id:
                if rec.approving_matrix_id.matrix_type == 'amount':
                    max_amount_list = []
                    matrix = self.env['pr.approving.matrix'].search([('id', '=', rec.approving_matrix_id.id)])
                    for line in matrix.line_ids:
                        max_amount_list.append(line.max_amount)
                    for line in matrix.line_ids:
                        if (rec.amount_total <= line.max_amount) and (rec.amount_total >= line.min_amount):
                            approval_lines = line
                        elif (rec.amount_total >= line.max_amount) and (max(max_amount_list) == line.max_amount):
                            approval_lines = line
                else:
                    approval_lines = rec.approving_matrix_id.line_ids

                for line in approval_lines:
                    approval_matrix_lines.append([0, 0, {
                        'employee_ids': [(6,0, line.employee_ids.ids)],
                        'name': line.name,
                        'min_amount': line.min_amount,
                        'max_amount':line.max_amount,
                        'approved': False,
                        }
                    ])
            if approval_matrix_lines:
                rec.approving_matrix_line_ids = approval_matrix_lines