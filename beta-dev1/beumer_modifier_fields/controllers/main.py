import odoo
import odoo.modules.registry
import ast

from odoo import http, _
from odoo.http import request
from odoo import SUPERUSER_ID

import datetime
import json
import pytz
import os
import logging
import json

_logger = logging.getLogger(__name__)


class check_hide_action(http.Controller):
    @http.route(['/api/check_hide_action'], auth='public', csrf=False)
    def check_hide_action(self, **post):
        data = json.loads(post.items()[0][0])
        uid = int(data['uid'])
        accsess_accounting_manager_group = request.env.ref('beumer_modifier_access_right.accsess_accounting_manager')
        accsess_ap_ar_manager_group = request.env.ref('beumer_modifier_access_right.accsess_ap_ar_manager')
        check_hide_action = False
        if uid != SUPERUSER_ID:
            for user in accsess_accounting_manager_group.users:
                if user.id == uid:
                    check_hide_action = True
                    break
            if not check_hide_action:
                for user in accsess_ap_ar_manager_group.users:
                    if user.id == uid:
                        check_hide_action = True
                        break

        res = []
        res.append({
            'check_hide_action': check_hide_action,
        })
        return json.dumps(res);

class check_hide_export(http.Controller):
    @http.route(['/api/check_hide_export'], auth='public', csrf=False)
    def check_hide_action(self, **post):
        data = json.loads(post.items()[0][0])
        uid = None
        if 'uid' in data:
            uid = int(data['uid'])

        accsess_all_employee_group = request.env.ref('beumer_modifier_access_right.all_employee_group')
        check_hide_export = False
        if uid != SUPERUSER_ID:
            for user in accsess_all_employee_group.users:
                if user.id == uid:
                    check_hide_export = True
                    break

        res = []
        res.append({
            'check_hide_export': check_hide_export,
        })
        return json.dumps(res);


class check_hide_edit(http.Controller):
    @http.route(['/api/check_hide_edit'], auth='public', csrf=False)
    def check_hide_action(self, **post):
        data = json.loads(post.items()[0][0])
        uid = int(data['uid'])
        accsess_accounting_manager_group = request.env.ref('beumer_modifier_access_right.edit_hr_expense')
        check_hide_action = False
        if uid != SUPERUSER_ID:
            for user in accsess_accounting_manager_group.users:
                if user.id == uid:
                    check_hide_action = True
                    break

        res = []
        res.append({
            'check_hide_action': check_hide_action,
        })
        return json.dumps(res);