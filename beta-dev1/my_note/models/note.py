# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class MyNote(models.Model):

    _inherit = 'note.note'

    @api.model
    def create(self, values):
        if 'stage_id' not in values:
            if self._context.get('default_stage_id', False):
                values['state_id'] = self._context.get('default_stage_id')
        print "==========> Context: %s" %(self._context,)
        print "==========> Values: %s" % (values,)
        result = super(MyNote, self).create(values)
        return result

    @api.multi
    def _get_user_color(self):
        for note in self:
            if note.note_color:
                note.color = note.note_color
            else:
                note.color = int(note.user_id.color)

    color      = fields.Integer(string='Color Index', compute='_get_user_color')
    note_color = fields.Integer(string='Color Index')
