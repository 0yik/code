import json
from odoo.addons.base_geolocalize.models.res_partner import geo_find, geo_query_address
from odoo import models, fields, api
import re
import json
from urllib2 import urlopen
import time
import string

class Meeting(models.Model):

    _inherit = 'calendar.event'

    sign_in_location = fields.Char(string="Sign In Location")
    sign_out_location = fields.Char(string="Sign Out Location")
    sign_in = fields.Boolean('Sign In')
    sign_out = fields.Boolean('Sign Out')
    notee_field = fields.Html(string='Comment')

    @api.model
    def get_sign_in_location(self, lat, long, event_id):
        event_rec = self.env['calendar.event'].browse(event_id)
        maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 3}
        json_map = json.dumps(maps_loc)
        event_rec.write({'sign_in_location': json_map,
                         'sign_in': True})

    @api.model
    def get_sign_out_location(self, lat, long, event_id):
        event_rec = self.env['calendar.event'].browse(event_id)
        maps_loc = {u'position': {u'lat': lat, u'lng': long}, u'zoom': 3}
        json_map = json.dumps(maps_loc)
        event_rec.write({'sign_out_location': json_map,
                         'sign_out': True})
    @api.multi
    def cancel_sign_in(self):
        for rec in self:
            rec.sign_in = False
            rec.sign_in_location = ''

    @api.multi
    def cancel_sign_out(self):
        for rec in self:
            rec.sign_out = False
            rec.sign_out_location = ''
