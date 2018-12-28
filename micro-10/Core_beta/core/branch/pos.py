# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class pos_session(models.Model):
    _inherit = 'pos.session'

    # @api.model
    # def _get_session_default_branch(self):
    #     user_pool = self.env['res.users']
    #     branch_id = user_pool.browse(self.env.user.id).branch_id and  user_pool.browse(self.env.user.id).branch_id.id
    #     return branch_id

    branch_id = fields.Many2one('res.branch', 'Branch', related='config_id.branch_id')


class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _get_pos_order_default_branch(self):
        user_pool = self.env['res.users']
        branch_id = user_pool.browse(self.env.user.id).branch_id and  user_pool.browse(self.env.user.id).branch_id.id
        return branch_id
        
    branch_id = fields.Many2one('res.branch', 'Branch', related='session_id.config_id.branch_id')

class PosConfig(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch', 'Branch', required=1)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
