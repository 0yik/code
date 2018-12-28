from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class HrTimeSheet(http.Controller):

    @http.route('/hr/sheet/leave/data', type='json', auth='user', website=True)
    def get_sheet_leave_data(self, data, id):
        sheet_id = request.env['hr_timesheet_sheet.sheet'].browse(id)
        tz = pytz.timezone(request.env.user.partner_id.tz) or pytz.utc
        date_sheet = pytz.utc.localize(datetime.strptime(data, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
        date_sheet = date_sheet.strftime("%Y-%m-%d")
        flag = False
        for leave in sheet_id.employee_leave_ids:
            if leave.state == 'validate':
                leave_from = pytz.utc.localize(datetime.strptime(leave.date_from, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
                leave_to = pytz.utc.localize(datetime.strptime(leave.date_to, "%Y-%m-%d %H:%M:%S")).astimezone(tz)
                leave_from = leave_from.strftime("%Y-%m-%d")
                leave_to = leave_to.strftime("%Y-%m-%d")
                if date_sheet >= leave_from and date_sheet <= leave_to:
                    flag =  True
        return flag
