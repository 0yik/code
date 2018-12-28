# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _

import datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_bo_info(self, obj):
        sale_obj = False
        if not obj.origin:
            return sale_obj
        sale_obj = self.env['sale.order'].sudo().search([('name', '=', obj.origin)])
        if sale_obj:
            return sale_obj[0]
        return sale_obj

    def time_return_format(self, date_to_timezone):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        return datetime.datetime.strftime(pytz.utc.localize(datetime.datetime.strptime(
                    date_to_timezone,
                    DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%H:%M")

    def get_time_format_schedule_start(self, obj):
        formated_time = ''
        if not obj.env.user.tz:
            raise exceptions.UserError(
                _('Please add time zone in user. You can set Timezone under Preferences menu.'))
        if not obj.sudo().scheduled_start:
            return formated_time
        user_tz = obj.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        formated_time = self.time_return_format(obj.sudo().scheduled_start)
        return formated_time

    def get_time_format_start(self, obj):
        formated_time = ''
        if not obj.env.user.tz:
            raise exceptions.UserError(
                _('Please add time zone in user. You can set Timezone under Preferences menu.'))
        if not obj.sudo().actual_start:
            return formated_time
        user_tz = obj.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        formated_time = self.time_return_format(obj.sudo().actual_start)
        return formated_time

    def get_time_format_end(self, obj):
        formated_time = ''
        if not obj.env.user.tz:
            raise exceptions.UserError(
                _('Please add time zone in user. You can set Timezone under Preferences menu.'))
        if not obj.sudo().actual_end:
            return formated_time
        user_tz = obj.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        formated_time = datetime.datetime.strftime(pytz.utc.localize(datetime.datetime.strptime(
                        obj.sudo().actual_end,
                        DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%H:%M")
        formated_time = self.time_return_format(obj.sudo().actual_end)
        #formated_time = datetime.datetime.strftime(fields.Datetime.from_string(obj.sudo().actual_end), ("%H:%M"))
        return formated_time

    @api.multi
    def do_print_picking(self):
        if not self.is_booking:
            return super(StockPicking, self).do_print_picking()
        self.write({'printed': True})
        return self.env["report"].get_action(self, 'biocare_reports_modifier.report_workorder')


StockPicking()
