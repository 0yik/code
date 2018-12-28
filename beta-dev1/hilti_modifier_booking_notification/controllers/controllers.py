from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
import werkzeug
import json
import base64
import os
from random import randint
import datetime
import time
import pytz
from dateutil import tz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT


class HiltiNotification(http.Controller):

    @http.route(['/notification'], type='http', auth="user", website=True)
    def notification(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_booking_notification', 'menu_notification_notification_customer_tester')[1]
        action_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_booking_notification', 'action_notification_notification_view')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=notification.notification&menu_id=" + str(menu_id) + "&action=" + str(action_id))
                                  #/web#min=1&limit=80&view_type=list&model=notification.notification&menu_id=240&action=338

    @http.route(['/notification_customer'], type='http', auth="user", website=True)
    def notification_customer(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_booking_notification', 'menu_notification_notification_customer')[1]
        action_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_booking_notification', 'action_notification_notification_view')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=notification.notification&menu_id=" + str(menu_id) + "&action=" + str(action_id))
    
    @http.route(['/notification_staff'], type='http', auth="user", website=True)
    def notification_staff(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_booking_notification', 'menu_notification_notification_customer_account_manager')[1]
        action_id = request.env['ir.model.data'].get_object_reference('hilti_modifier_booking_notification', 'action_notification_notification_view')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=notification.notification&menu_id=" + str(menu_id) + "&action=" + str(action_id))
