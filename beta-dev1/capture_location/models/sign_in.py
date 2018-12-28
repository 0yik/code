from odoo import models, fields, api
import datetime


class sign_in(models.Model):
    _name = 'sign.in'

    @api.one
    def get_history(self):
        history = self.env['sign_in.history']
        list = []
        list_history = history.search(['|', ('author_user', '=', self._uid), '|', ('author_in', '=', self._uid), ('author_out', '=', self._uid)])
        list = [history_id.id for history_id in list_history ]
        self.history_ids = list

    author_user     = fields.Many2one('res.users', string='Author Meeting')
    setting_time    = fields.Datetime('Meeting Time')
    author_in       = fields.Many2one('res.users', string='User Sign In')
    author_out      = fields.Many2one('res.users', string='User Out')
    subject         = fields.Char('Meeting Subject')
    latitude_in     = fields.Char('Latitude In')
    longitude_in    = fields.Char('Longitude In')

    latitude_out    = fields.Char('Latitude Out')
    longitude_out   = fields.Char('Longitude Out')
    start_time      = fields.Datetime('Start Time')
    end_time        = fields.Datetime('End Time')
    history_ids     = fields.Many2many('sign_in.history', id1='sign_in_id', id2='history_ids', string='Sign In History',
                                   compute='get_history')
    signed          = fields.Boolean('Check Sign In')
    sign_out        = fields.Boolean('Check Sign Out')

    @api.multi
    def sign_in_func(self):
        return True

    @api.multi
    def sign_out_func(self):
        return True

    @api.multi
    def update_location_signin(self, vals):
        values = {}
        values['author_in'] = self._uid
        values['start_time'] = datetime.datetime.now()
        values['latitude_in'] = vals.get('latitude', '')
        values['longitude_in'] = vals.get('longitude', '')
        values['signed'] = True
        if values and len(values) > 0:
            for record in self:
                record.write(values)

    @api.multi
    def update_location_signout(self, vals):
        values = {
            'author_out' : self._uid,
            'end_time' : datetime.datetime.now(),
            'latitude_out' : vals.get('latitude', ''),
            'longitude_out' : vals.get('longitude', ''),
            'sign_out' : True,
        }
        self.write(values)
        ctx = {
            'default_subject': self.subject or '',
            'default_sign_in_time': self.start_time or False,
            'default_sign_out_time': self.end_time or False,
            'default_latitude_in': self.latitude_in or False,
            'default_longitude_in': self.longitude_in or False,
            'default_latitude_out': self.latitude_out or False,
            'default_longitude_out': self.longitude_out or False,
            'default_author_in': self.author_in.id or False,
            'default_author_out': self.author_out.id or False,
            'default_author_user': self.author_user.id or False,
        }
        return ctx

    @api.model
    def update_abc(self, record_id, values):
        self.browse(record_id).write(values)
        return self.browse(record_id).read(['author_in'])

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            subject = record.subject or ''
            res.append((record.id,subject))
        return res


