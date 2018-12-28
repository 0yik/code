# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    team_ids = fields.Many2many(
        comodel_name='booking.team',
        string='Teams', help='Add dedicate team here.')
    reserved_team = fields.Boolean(
        string='Reserved Team',
        help='Tick if this service have dedicated team.')

    @api.onchange('type')
    def _onchange_type(self):
        # override for biocare
        if self.type == 'service':
            # self.track_service = 'timesheet'
            print "---------------"
        else:
            self.track_service = 'manual'


ProductTemplate()
