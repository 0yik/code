# -*- coding: utf-8 -*-
# Part of eComBucket. See LICENSE file for full copyright and licensing details
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.addons import decimal_precision as dp
_logger = logging.getLogger(__name__)



class sale_order(models.Model):
    _inherit = 'sale.order'

    approver_ids = fields.Many2many(comodel_name='res.users', string='Approved By', copy=False)
    state = fields.Selection(selection_add=[('approved','Approved')])

    @api.multi
    def approved_by_user(self):
        Matrix = self.env['sale.order.approval.matrix']
        for rec in self.filtered('amount_total'):
            margin = float(self.margin)*100/self.amount_total
            matrix = Matrix.search([('crm_team_id','=', self.team_id.id)], limit=1)
            if not(matrix):
                raise UserError(_('No Approval Matrix match with %s.'%(self.team_id.name)))

            limit_matrix_line = self.env['sale.order.approval.matrix.line']
            for matrix_line in matrix.matrix_line_ids.filtered(lambda line:line.margin<= margin):
                if matrix_line.margin>limit_matrix_line.margin:
                    limit_matrix_line = matrix_line
            approver_ids =  limit_matrix_line.mapped('approver_ids')
            if not(limit_matrix_line):
                raise UserError(_('No Approval Matrix line match with the margin of %r(%r)'%(self.margin, margin)))
            if matrix and self.env.user in approver_ids:
                rec.approver_ids+=self.env.user
                if len(set(rec.approver_ids)) >= limit_matrix_line.approver_count:
                    self.state='approved'


class sale_order_approval_matrix_line(models.Model):
    _name = 'sale.order.approval.matrix.line'

    margin = fields.Float(string='Margin(%)', digits=dp.get_precision('Product Price'))
    approver_ids = fields.Many2many(comodel_name='res.users', string='Approval') 
    approver_count = fields.Integer(string='No. of approvers needed', default='1')
    matrix_id = fields.Many2one(comodel_name='sale.order.approval.matrix', string='Matrix')
    
    @api.constrains('approver_count','approver_ids')
    def _check_employee_related_user(self):
        for record in self:
            len_approver = len(record.approver_ids)
            approver_count = record.approver_count
            if approver_count > len_approver:
                raise UserError(_('No. of approvers %r should be less than total approvers %r.'%(approver_count, len_approver)))


class sale_order_approval_matrix(models.Model):

    _name = 'sale.order.approval.matrix'
    name = fields.Char(string='Name')
    crm_team_id = fields.Many2one(comodel_name='crm.team', string='Sale Team')
    matrix_line_ids = fields.One2many(
                          comodel_name='sale.order.approval.matrix.line',
                          inverse_name='matrix_id', string='Matrix Line') 

