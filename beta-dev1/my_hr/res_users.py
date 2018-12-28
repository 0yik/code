# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

from odoo import fields, api, models


class res_users(models.Model):
    """ Update of res.users class
        - if adding groups to an user, check if base.group_user is in it
        (member of 'Employee'), create an employee form linked to it.
    """
    _name = 'res.users'
    _inherit = ['res.users']

    display_employees_suggestions = fields.Boolean("Display Employees Suggestions")

    _defaults = {
        'display_employees_suggestions': True,
    }

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on
        display_employees_suggestions fields. Access rights are disabled by
        default, but allowed on some specific fields defined in
        self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super(res_users, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.append('display_employees_suggestions')
        # duplicate list to avoid modifying the original reference
        self.SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        self.SELF_READABLE_FIELDS.append('display_employees_suggestions')
        return init_res

    def stop_showing_employees_suggestions(self):
        """Update display_employees_suggestions value to False"""
        self.write({"display_employees_suggestions": False})

    def _create_welcome_message(self):
        """Do not welcome new users anymore, welcome new employees instead"""
        return True

    def _message_post_get_eid(self, thread_id):
        assert thread_id, "res.users does not support posting global messages"
        if isinstance(thread_id, (list, tuple)):
            thread_id = thread_id[0]
        return self.env['hr.employee'].search([('user_id', '=', thread_id)])

    @api.cr_uid_ids_context
    def message_post(self, thread_id, **kwargs):
        """ Redirect the posting of message on res.users to the related employee.
            This is done because when giving the context of Chatter on the
            various mailboxes, we do not have access to the current partner_id. """
        if kwargs.get('type') == 'email':
            return super(res_users, self).message_post(thread_id, **kwargs)
        res = None
        employee_ids = self._message_post_get_eid(thread_id)
        if not employee_ids:  # no employee: fall back on previous behavior
            return super(res_users, self).message_post(thread_id, **kwargs)
        for employee_id in employee_ids:
            res = self.env['hr.employee'].message_post(employee_id, **kwargs)
        return res
