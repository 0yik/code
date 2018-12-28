# coding: utf-8

from odoo import api, fields, models
from odoo import api, fields, models, tools, _
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class res_purpose(models.Model):
    _name='res.purpose'
    _rec_name = 'name'

    name = fields.Char('Name')

class res_visitor(models.Model):
    _name = 'res.visitor'
    _rec_name = 'name'

    @api.depends('check_in','check_out')
    def _compute_duration(self):
        for record in self:
            if record.check_in and record.check_out:
                date_check_in = datetime.strptime(record.check_in, '%Y-%m-%d %H:%M:%S')
                date_check_out = datetime.strptime(record.check_out, '%Y-%m-%d %H:%M:%S')
                duration = date_check_out - date_check_in
                days, seconds = duration.days, duration.seconds
                record.duration_hours = days * 24 + seconds // 3600
                record.duration_minutes = (record.duration_hours * 60) + (seconds % 3600) // 60

    name = fields.Char('Name',required=True)
    company_visitor = fields.Char('Company')
    nric = fields.Char('NRIC/FIN')
    contact_number = fields.Char('Contact Number')
    looking_for = fields.Char('Looking For')
    purpose_visitor = fields.Many2one('res.purpose','Purpose')
    remarks_visitor = fields.Text('Remarks')
    check_in = fields.Datetime('Check In Time')
    check_out = fields.Datetime('Check Out Time')
    state = fields.Selection([
        ('draft', _('Draft')),
        ('check_in', _('Checked In')),
        ('check_out',_('Checked Out'))], string='Status', default='draft')
    duration_hours = fields.Float(compute=_compute_duration, string='Duration(hrs)', store=True)
    duration_minutes = fields.Float(compute=_compute_duration, string='Duration(mins)', store=True)

    @api.multi
    def action_check_in(self):
        for ob in self:
            if not self.check_in:
                self.check_in = fields.Datetime.now()
                self.state = 'check_in'
            else:
                raise UserError(_('This visitor has already checked In.'))
        return True

    @api.multi
    def action_check_out(self):
        for ob in self:
            if not self.check_out:
                self.check_out = fields.Datetime.now()
                self.state = 'check_out'
            else:
                raise UserError(_('This visitor has already checked Out.'))
        return True