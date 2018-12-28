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

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class AccountSubscriptionGenerate(models.TransientModel):

    _name = "account.subscription.generate"
    _description = "Subscription Compute"
    
    date    = fields.Date(string='Generate Entries Before', required=True, default=fields.Date.context_today)
    
    @api.multi
    def action_generate(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        sub_line_obj = self.env['account.subscription.line']
        
        moves_created=[]
        for data in  self:
            line_ids = sub_line_obj.search([('date', '<=', data['date']), ('move_id', '=', False)])
            #moves = sub_line_obj.move_create(line_ids)
            moves = line_ids.move_create()
            moves_created.extend(moves)
        model, action_id = mod_obj.get_object_reference('account', 'action_move_line_form')
        [action] = self.env[model].browse(action_id).read()
        action['domain'] = str([('id','in',moves_created)])
        
        return action
    


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
