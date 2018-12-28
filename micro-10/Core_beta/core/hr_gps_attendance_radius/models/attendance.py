import json
from odoo.addons.base_geolocalize.models.res_partner import geo_find, geo_query_address
from odoo import models, fields, api, _
import re
import json
from urllib2 import urlopen
import time
import string
from math import sin, cos, sqrt, atan2, radians
from odoo.exceptions import UserError

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_location = fields.Char('Check In Location')
    check_out_location = fields.Char('Check Out Location')

    @api.multi
    def write(self, vals):
        if vals.get('sign_in_location', False) or vals.get('sign_out_location', False):
            if self.sign_in_lat and self.sign_in_lng:
                if self.employee_id.checkin_branch_id and self.employee_id.check_in_selection == 'branch':
                    maps_loc = {u'position': {u'lat': float(self.sign_in_lat), u'lng': float(self.sign_in_lng)},
                                u'zoom': 16,
                                u'branchposition': {u'lat': float(self.employee_id.checkin_branch_id.lat),
                                                    u'lng': float(self.employee_id.checkin_branch_id.lng)}}
                elif self.employee_id.checkin_company_id and self.employee_id.check_in_selection == 'company':
                    maps_loc = {u'position': {u'lat': float(self.sign_in_lat), u'lng': float(self.sign_in_lng)},
                                u'zoom': 16,
                                u'branchposition': {u'lat': float(self.employee_id.checkin_company_id.lat_comapny),
                                                    u'lng': float(self.employee_id.checkin_company_id.lng_company)}}

                else:
                    maps_loc = {u'position': {u'lat': float(self.sign_in_lat), u'lng': float(self.sign_in_lng)},
                                u'zoom': 16}
                json_map = json.dumps(maps_loc)
                vals.update({'sign_in_location': json_map})
            if self.sign_out_lat and self.sign_out_lng:
                if self.employee_id.checkout_branch_id  and self.employee_id.check_out_selection == 'branch':
                    maps_loc_out = {u'position': {u'lat': float(self.sign_out_lat), u'lng': float(self.sign_out_lng)},
                                u'zoom': 16,
                                u'branchposition': {u'lat': float(self.employee_id.checkout_branch_id.lat),
                                                    u'lng': float(self.employee_id.checkout_branch_id.lng)}}
                elif self.employee_id.checkout_company_id and self.employee_id.check_out_selection == 'company':
                    maps_loc_out = {u'position': {u'lat': float(self.sign_in_lat), u'lng': float(self.sign_in_lng)},
                                u'zoom': 16,
                                u'branchposition': {u'lat': float(self.employee_id.checkout_company_id.lat_comapny),
                                                    u'lng': float(self.employee_id.checkout_company_id.lng_company)}}
                else:
                    maps_loc_out = {u'position': {u'lat': float(self.sign_out_lat), u'lng': float(self.sign_out_lng)},
                                    u'zoom': 16}
                json_map_out = json.dumps(maps_loc_out)
                vals.update({'sign_out_location': json_map_out})
        res = super(HrAttendance, self).write(vals)
        return res

    @api.model
    def get_sign_in_out_location(self, lat, long, att_id):
        att_rec = self.env['hr.attendance'].browse(att_id)
        if att_rec.employee_id.attendance_state != 'checked_in':
            if att_rec.employee_id.checkout_branch_id and att_rec.employee_id.check_out_selection == 'branch':
                maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 16,
                            u'branchposition': {u'lat': float(att_rec.employee_id.checkout_branch_id.lat),
                                                u'lng': float(att_rec.employee_id.checkout_branch_id.lng)}}
            elif att_rec.employee_id.checkout_company_id and att_rec.employee_id.check_out_selection == 'company':
                maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 16,
                            u'branchposition': {u'lat': float(att_rec.employee_id.checkout_company_id.lat_comapny),
                                                u'lng': float(att_rec.employee_id.checkout_company_id.lng_company)}}

            else:
                maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 16}

            json_map = json.dumps(maps_loc)
            att_rec.write({'sign_out_location': json_map,
                       'sign_out_lat': lat,
                       'sign_out_lng': long})
        else:
            if att_rec.employee_id.checkin_branch_id and att_rec.employee_id.check_in_selection == 'branch':
                maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 16,
                            u'branchposition': {u'lat': float(att_rec.employee_id.checkin_branch_id.lat),
                                                u'lng': float(att_rec.employee_id.checkin_branch_id.lng)}}
            elif att_rec.employee_id.checkin_company_id and att_rec.employee_id.check_in_selection == 'company':
                maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 16,
                            u'branchposition': {u'lat': float(att_rec.employee_id.checkin_company_id.lat_comapny),
                                                u'lng': float(att_rec.employee_id.checkin_company_id.lng_company)}}

            else:
                maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 16}

            json_map = json.dumps(maps_loc)
            att_rec.write({'sign_in_location': json_map,
                           'sign_in_lat': lat,
                           'sign_in_lng': long})
        for rec in att_rec:
            if rec.employee_id.check_in_verification:
                R = 6373.0
                lat1 = lon1 = lat2 = lon2 = 0.0
                location_type = ''
                if rec.employee_id.check_in_selection == 'branch':
                    lat1 = radians(rec.employee_id.checkin_branch_id.lat)
                    lon1 = radians(rec.employee_id.checkin_branch_id.lng)
                    lat2 = radians(float(rec.sign_in_lat))
                    lon2 = radians(float(rec.sign_in_lng))
                    location_type = 'branch'
                elif rec.employee_id.check_in_selection == 'company':
                    lat1 = radians(rec.employee_id.checkin_company_id.lat_comapny)
                    lon1 = radians(rec.employee_id.checkin_company_id.lng_company)
                    lat2 = radians(float(rec.sign_in_lat))
                    lon2 = radians(float(rec.sign_in_lng))
                    location_type = 'company'

                if lat1 and lon1 and lat2 and lon2:
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1

                    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                    c = 2 * atan2(sqrt(a), sqrt(1 - a))

                    distance = R * c
                    if distance and location_type == 'branch':
                        if rec.employee_id.checkin_branch_id.checkin_radius_selection == 'km':
                            if distance > rec.employee_id.checkin_branch_id.checkin_radius:
                                rec.check_in_location = 'Out Of Boundary ' + '( ' + rec.employee_id.checkin_branch_id.name + ' )'
                            else:
                                rec.check_in_location = 'Within Boundary ' + '( ' + rec.employee_id.checkin_branch_id.name + ' )'
                        elif rec.employee_id.checkin_branch_id.checkin_radius_selection == 'meter':
                            distance = distance * 1000
                            if distance > rec.employee_id.checkin_branch_id.checkin_radius:
                                rec.check_in_location = 'Out Of Boundary ' + '( ' + rec.employee_id.checkin_branch_id.name + ' )'
                            else:
                                rec.check_in_location = 'Within Boundary ' + '( ' + rec.employee_id.checkin_branch_id.name + ' )'
                    elif distance and location_type == 'company':
                        if rec.employee_id.checkin_company_id.checkin_radius_selection == 'km':
                            if distance > rec.employee_id.checkin_company_id.checkin_radius:
                                rec.check_in_location = 'Out Of Boundary ' + '( ' + rec.employee_id.checkin_company_id.name + ' )'
                            else:
                                rec.check_in_location = 'Within Boundary ' + '( ' + rec.employee_id.checkin_company_id.name + ' )'
                        elif rec.employee_id.checkin_company_id.checkin_radius_selection == 'meter':
                            distance = distance * 1000
                            if distance > rec.employee_id.checkin_company_id.checkin_radius:
                                    rec.check_in_location = 'Out Of Boundary ' + '( ' + rec.employee_id.checkin_company_id.name + ' )'
                            else:
                                rec.check_in_location = 'Within Boundary ' + '( ' + rec.employee_id.checkin_company_id.name + ' )'

            if rec.employee_id.check_out_verification:
                R = 6373.0
                lat1 = lon1 = lat2 = lon2 = 0.0
                location_type = ''
                if rec.employee_id.check_out_selection == 'branch':
                    lat1 = radians(rec.employee_id.checkout_branch_id.lat)
                    lon1 = radians(rec.employee_id.checkout_branch_id.lng)
                    lat2 = radians(float(rec.sign_out_lat))
                    lon2 = radians(float(rec.sign_out_lng))
                    location_type = 'branch'
                elif rec.employee_id.check_out_selection == 'company':
                    lat1 = radians(rec.employee_id.checkout_company_id.lat_comapny)
                    lon1 = radians(rec.employee_id.checkout_company_id.lng_company)
                    lat2 = radians(float(rec.sign_out_lat))
                    lon2 = radians(float(rec.sign_out_lng))
                    location_type = 'company'
                if lat1 and lon1 and lat2 and lon2:
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1

                    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                    c = 2 * atan2(sqrt(a), sqrt(1 - a))

                    distance = R * c
                    if distance and location_type == 'branch':
                        if rec.employee_id.checkout_branch_id.checkout_radius_selection == 'km':
                            if distance > rec.employee_id.checkout_branch_id.checkout_radius:
                                rec.check_out_location = 'Out Of Boundary ' + '( ' + rec.employee_id.checkout_branch_id.name + ' )'
                            else:
                                rec.check_out_location = 'Within Boundary ' + '( ' + rec.employee_id.checkout_branch_id.name + ' )'
                        elif rec.employee_id.checkout_branch_id.checkout_radius_selection == 'meter':
                            distance = distance * 1000
                            if distance > rec.employee_id.checkout_branch_id.checkout_radius:
                                rec.check_out_location = 'Out Of Boundary ' + '( ' + rec.employee_id.checkout_branch_id.name + ' )'
                            else:
                                rec.check_out_location = 'Within Boundary ' + '( ' + rec.employee_id.checkout_branch_id.name + ' )'

                    elif distance and location_type == 'company':
                        if rec.employee_id.checkout_company_id.checkout_radius_selection == 'km':
                            if distance > rec.employee_id.checkout_company_id.checkout_radius:
                                rec.check_out_location = 'Out Of Boundary ' + '( ' + rec.employee_id.checkout_company_id.name + ' )'
                            else:
                                rec.check_out_location = 'Within Boundary ' + '( ' + rec.employee_id.checkout_company_id.name + ' )'
                        elif rec.employee_id.checkout_company_id.checkout_radius_selection == 'meter':
                            distance = distance * 1000
                            if distance > rec.employee_id.checkout_company_id.checkout_radius:
                                rec.check_out_location = 'Out Of Boundary ' + '( ' + rec.employee_id.checkout_company_id.name + ' )'
                            else:
                                rec.check_out_location = 'Within Boundary ' + '( ' + rec.employee_id.checkout_company_id.name + ' )'
