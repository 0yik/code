import json
from odoo.addons.base_geolocalize.models.res_partner import geo_find, geo_query_address
from odoo import models, fields, api
import re
import json
from urllib2 import urlopen
import time
import string

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    sign_in_location = fields.Char(string="Check In Location")
    sign_out_location = fields.Char(string="Check Out Location")
    sign_in_lat = fields.Char('Check In Latitude')
    sign_in_lng = fields.Char('Check In Longitude')
    sign_out_lat = fields.Char('Check Out Latitude')
    sign_out_lng = fields.Char('Check Out Longitude')

    # @api.multi
    # def write(self, vals):
    #     if vals.get('sign_in_location', False) or vals.get('sign_out_location', False):
    #         if self.sign_in_lat and self.sign_in_lng:
    #             maps_loc = {u'position': {u'lat': float(self.sign_in_lat), u'lng': float(self.sign_in_lng)}, u'zoom': 5}
    #             json_map = json.dumps(maps_loc)
    #             vals.update({'sign_in_location': json_map})
    #         if self.sign_out_lat and self.sign_out_lng:
    #             maps_loc_out = {u'position': {u'lat': float(self.sign_out_lat), u'lng': float(self.sign_out_lng)},u'zoom': 5}
    #             json_map_out = json.dumps(maps_loc_out)
    #             vals.update({'sign_out_location': json_map_out})
    #     res = super(HrAttendance, self).write(vals)
    #     return res

    @api.model
    def get_sign_in_out_location(self, lat, long, att_id):
        att_rec = self.env['hr.attendance'].browse(att_id)
        maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 16}
        json_map = json.dumps(maps_loc)
        if att_rec.employee_id.attendance_state != 'checked_in':
            att_rec.write({'sign_out_location': json_map,
                           'sign_out_lat': lat,
                           'sign_out_lng': long})
        else:
            att_rec.write({'sign_in_location': json_map,
                           'sign_in_lat': lat,
                           'sign_in_lng': long})
        print "******************************************"

