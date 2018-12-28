# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class HouseColourSummaryWizard(models.TransientModel):
    _name = "termly.updates.wizard"

    @api.multi
    def _print_report(self, data):
        return self.env['report'].get_action(self, 'ap_intervention.report_ap_intervention')
   
   
    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_selection'])[0]
        return self._print_report(data)


