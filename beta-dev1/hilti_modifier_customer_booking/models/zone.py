# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class Zone(models.Model):
    _inherit = 'zone.zone'

    @api.constrains('tester_ids')
    def _check_tester_id(self):
        zone_ids = self.search([('id', '!=', self.id)])
        allocated_tester = []
        for zone_obj in zone_ids:
            for tester_al in zone_obj.tester_ids:
                allocated_tester.append(tester_al.id)
        if allocated_tester:
            for zone in self:
                for current_tester in zone.tester_ids:
                    if current_tester.id in allocated_tester:
                        print "DDDDDDDDd"
                        raise exceptions.ValidationError(
                            _("Tester %s, is already allocated in %s. \n Please allocate another tester for this Zone." % (current_tester.name, current_tester.zone_id.name)))

