# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from dateutil.relativedelta import relativedelta
import datetime
import logging
import time

from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning
from odoo import tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'
    
    
    @api.multi
    def action_validate(self):
        res = super(account_analytic_account, self).action_validate()
        crm_lead_pool = self.env['crm.lead']
        if self.partner_id:
            opportunity_ids = crm_lead_pool.search([('partner_id','=',self.partner_id.id)])
            if opportunity_ids:
                for opportunity_id in opportunity_ids:
                    opportunity_id.action_set_won()
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
