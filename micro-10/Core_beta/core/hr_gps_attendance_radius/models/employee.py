from odoo import models, fields, api, _
from math import sin, cos, sqrt, atan2, radians
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def check_in_out_radius(self, lat, lng, employee_id):
        employee_id = self.env['hr.employee'].browse(employee_id)
        if employee_id.attendance_state != 'checked_in' and employee_id.check_in_verification:

            R = 6373.0
            lat1 = lon1 = lat2 = lon2 = 0.0
            location_type = ''
            if employee_id.check_in_selection == 'branch' and not employee_id.checkin_branch_id.allow_boundary_check_in:
                lat1 = radians(employee_id.checkin_branch_id.lat)
                lon1 = radians(employee_id.checkin_branch_id.lng)
                lat2 = radians(float(lat))
                lon2 = radians(float(lng))
                location_type = 'branch'
            elif employee_id.check_in_selection == 'company' and not employee_id.checkin_company_id.allow_boundary_check_in == False:
                lat1 = radians(employee_id.checkin_company_id.lat_comapny)
                lon1 = radians(employee_id.checkin_company_id.lng_company)
                lat2 = radians(float(lat))
                lon2 = radians(float(lng))
                location_type = 'company'

            if lat1 and lon1 and lat2 and lon2:
                dlon = lon2 - lon1
                dlat = lat2 - lat1

                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))

                distance = R * c
                if distance and location_type == 'branch':
                    if employee_id.checkin_branch_id.checkin_radius_selection == 'km':
                        if distance > employee_id.checkin_branch_id.checkin_radius:
                            return {'check': False, 'attendance_state': 'in'}

                    elif employee_id.checkin_branch_id.checkin_radius_selection == 'meter':
                        distance = distance * 1000
                        if distance > employee_id.checkin_branch_id.checkin_radius:
                            return {'check': False, 'attendance_state': 'in'}

                elif distance and location_type == 'company':
                    if employee_id.checkin_company_id.checkin_radius_selection == 'km':
                        if distance > employee_id.checkin_company_id.checkin_radius:
                            return {'check': False, 'attendance_state': 'in'}

                    elif employee_id.checkin_company_id.checkin_radius_selection == 'meter':
                        distance = distance * 1000
                        if distance > employee_id.checkin_company_id.checkin_radius:
                            return {'check': False, 'attendance_state': 'in'}

        elif employee_id.attendance_state == 'checked_in' and employee_id.check_out_verification:
            R = 6373.0
            lat1 = lon1 = lat2 = lon2 = 0.0
            location_type = ''
            if employee_id.check_out_selection == 'branch' and not employee_id.checkout_branch_id.allow_boundary_check_out:
                lat1 = radians(employee_id.checkout_branch_id.lat)
                lon1 = radians(employee_id.checkout_branch_id.lng)
                lat2 = radians(float(lat))
                lon2 = radians(float(lng))
                location_type = 'branch'
            elif employee_id.check_out_selection == 'company' and not employee_id.checkout_company_id.allow_boundary_check_out:
                lat1 = radians(employee_id.checkout_company_id.lat_comapny)
                lon1 = radians(employee_id.checkout_company_id.lng_company)
                lat2 = radians(float(lat))
                lon2 = radians(float(lng))
                location_type = 'company'
            if lat1 and lon1 and lat2 and lon2:
                dlon = lon2 - lon1
                dlat = lat2 - lat1

                a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))

                distance = R * c
                if distance and location_type == 'branch':
                    if employee_id.checkout_branch_id.checkout_radius_selection == 'km':
                        if distance > employee_id.checkout_branch_id.checkout_radius:
                            return {'check': False, 'attendance_state': 'out'}
                    elif employee_id.checkout_branch_id.checkout_radius_selection == 'meter':
                        distance = distance * 1000
                        if distance > employee_id.checkout_branch_id.checkout_radius:
                            return {'check': False, 'attendance_state': 'out'}
                elif distance and location_type == 'company':
                    if employee_id.checkout_company_id.checkout_radius_selection == 'km':
                        if distance > employee_id.checkout_company_id.checkout_radius:
                            return {'check': False, 'attendance_state': 'out'}
                    elif employee_id.checkout_company_id.checkout_radius_selection == 'meter':
                        distance = distance * 1000
                        if distance > employee_id.checkout_company_id.checkout_radius:
                            return {'check': False, 'attendance_state': 'out'}

        return {'check': True}

