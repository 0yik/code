# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    #378401
##############################################################################

from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        sale_team = self.env['crm.team'].search([])
        for team in sale_team:
            for member in team.member_ids:
                if member.id == self._context.get('uid'):
                    vals.update({'team_id': team.id})
        vals.update({'user_id': self._context.get('uid')})
        res = super(SaleOrder, self).create(vals)
        return res


class TargetGroup(models.Model):
    _name = 'target.group'

    name = fields.Char('Name')
    commission_type = fields.Selection([('amount','Amount'), ('percentage','Percentage')], 'Commission Type', default='amount')
    target_lines = fields.One2many('target.lines', 'target_group_id')


class TargetLine(models.Model):
    _name = 'target.lines'

    target_group_id = fields.Many2one('target.group')
    min_target = fields.Float('Min Target')
    max_target = fields.Float('Max Target')
    amount = fields.Float('Commission Amount')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: