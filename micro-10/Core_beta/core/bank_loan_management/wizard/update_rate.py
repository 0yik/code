# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, time, timedelta
from odoo.exceptions import Warning

class UpdateRateLoanWizard(models.TransientModel):
    _name = "update.rate.loan.wizard"

    rate            = fields.Float('Rate', required=True)
    installment_id  = fields.Many2one('loan.computation', string='Installment')
    loan_id         = fields.Many2one('bank.loan', string='Loan')
    
    @api.model
    def default_get(self, fields):
        rec = super(UpdateRateLoanWizard, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        
        rec.update({
            'loan_id': active_ids[0]})
        return rec
    
    @api.multi
    def update_rate(self):
        self.ensure_one()
        context = self._context
        active_ids = self._context.get('active_ids', False)
        
        loan_obj = self.env['bank.loan']
        loan = loan_obj.browse(active_ids)
        loan.write({'interest' : self.rate})
        loan.with_context({'installment_change_rate_id' : self.installment_id}).compute_installment()
        
        #raise UserError(_('Please check Your Period and Terms'))