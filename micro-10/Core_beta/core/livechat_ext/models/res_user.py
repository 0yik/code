# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.addons.bus.models.bus_presence import AWAY_TIMER
from odoo.addons.bus.models.bus_presence import DISCONNECTION_TIMER

class ResUsers(models.Model):
    _inherit = "res.users"

    im_status = fields.Char('IM Status', compute='_compute_im_status')
    user_status = fields.Selection([('online', 'Online'),('offline', 'Offline')], string='Live Chat Status', default='online')

    @api.multi
    def write(self, vals):
        # Resolving access right issue for the users
        if vals.get('user_status'):
            self = self.sudo()
        return super(ResUsers, self).write(vals)

    @api.multi
    @api.depends('user_status')
    def _compute_im_status(self):
        """ Compute the im_status of the users """
        self.env.cr.execute("""
            SELECT
                user_id as id,
                CASE WHEN age(now() AT TIME ZONE 'UTC', last_poll) > interval %s THEN 'offline'
                     WHEN age(now() AT TIME ZONE 'UTC', last_presence) > interval %s THEN 'away'
                     ELSE 'online'
                END as status
            FROM bus_presence
            WHERE user_id IN %s
            """, ("%s seconds" % DISCONNECTION_TIMER, "%s seconds" % AWAY_TIMER, tuple(self.ids)))
        res = dict(((status['id'], status['status']) for status in self.env.cr.dictfetchall()))
        for user in self:
            if user.user_status == 'online':
                user.im_status = res.get(user.id, 'offline')
            else:
                user.im_status = 'offline'

ResUsers()