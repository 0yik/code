# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class DocumentType(models.Model):
    _inherit = 'document.type'

    duration = fields.Integer(
        string='Duration',
        help='Add expire duration in days.')

    @api.one
    @api.constrains('duration')
    def _check_duration_zero(self):
        if self.duration <= 0:
            raise exceptions.ValidationError(_("You can not set duration 0."))

DocumentType()
