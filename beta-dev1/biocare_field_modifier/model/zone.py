# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class zone_postal_code(models.Model):
    _inherit = 'zonepostal.code'
    '''
    @api.constrains('name')
    def _check_cons_name(self):
        if len(str(self.name)) > 2 or len(str(self.name))< 2:
            raise exceptions.ValidationError(
                _('Please enter the first 2 digits of the Postal Code. Eg: 78'))
    '''

zone_postal_code()


class SequenceDetails(models.Model):
    _inherit = 'sequence.details'

    # overriding field to change M2M to M2o
    #postal_code_id = fields.Many2many('zonepostal.code','rel_postal_zone_detail', 'seq_id', 'postal_id', string="Postal Code")
    postal_code_id = fields.Many2one(comodel_name='zonepostal.code', string='Postal Code',)


class Zone(models.Model):
    _inherit = 'zone.zone'

    vehicle_ids = fields.Many2many(
        comodel_name='stock.location',
        string='Vehicle Number', help='Select Vehicle')
    team_ids = fields.Many2many(
        comodel_name='booking.team', relation="zone_zone_team_rel",
        column1="zone_id", column2="team_id",
        string='Teams', help='Team for zone')

    @api.constrains('team_ids')
    def _check_tester_id(self):
        zone_ids = self.search([('id', '!=', self.id)])
        allocated_tester = []
        for zone_obj in zone_ids:
            for team_al in zone_obj.team_ids:
                allocated_tester.append(team_al.id)
        if allocated_tester:
            for zone in self:
                for current_team in zone.team_ids:
                    if current_team.id in allocated_tester:
                        zone_search = self.search([('team_ids', '=', current_team.id),
                                            ('id', '!=', zone.id)
                                            ], limit=1)
                        raise exceptions.ValidationError(
                            _("%s is already allocated in %s. \n Please select another team." % (current_team.name, zone_search.name)))


Zone()
