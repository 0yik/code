# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools, _

class StockWarehouseUser(models.Model):
    _name = 'stock.warehouse.user.line'

    user_id      = fields.Many2one('stock.warehouse.user')
    state        = fields.Selection([('draft', 'To Process'), ('process', 'In Progress'), ('done', 'Processed')], related='user_id.state')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True)
    location_id  = fields.Many2one('stock.location', 'Location', required=True)
    start_date   = fields.Date('From', required=False)
    stop_date    = fields.Date('To', required=False)
    allday       = fields.Boolean('All Day')
    recurrency   = fields.Boolean('Recurrency')
    popup_ids    = fields.One2many('stock.warehouse.user.line.popup', 'line_id', string='Popups')

    interval     = fields.Integer('Repeat Every')
    rrule_type   = fields.Selection([
        ('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), ('yearly', 'Year(s)')
    ], 'Recurrency', default='daily')
    end_type     = fields.Selection([
        ('count', 'Number of repetitions'),
        ('end_date', 'End date')
    ], 'Recurrence Termination')
    count        = fields.Integer('Repeat', help="Repeat x times")
    final_date   = fields.Date('Repeat Until')
    mo           = fields.Boolean('Mon')
    tu           = fields.Boolean('Tue')
    we           = fields.Boolean('Wed')
    th           = fields.Boolean('Thu')
    fr           = fields.Boolean('Fri')
    sa           = fields.Boolean('Sat')
    su           = fields.Boolean('Sun')
    starting_no  = fields.Integer('Starting from Number')
    teacher_id   = fields.Many2one('hr.employee', 'Teacher')
    month_by     = fields.Selection([('date', 'Date of month'), ('day', 'Day of month')], 'Option', oldname='select1')
    day          = fields.Integer('Date of month')
    byday        = fields.Selection([('1', 'First'), ('2', 'Second'), ('3', 'Third'), ('4', 'Fourth'), ('5', 'Fifth'), ('-1', 'Last')],
            'By day')
    week_list    = fields.Selection([('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'), ('TH', 'Thursday'), ('FR', 'Friday'), ('SA', 'Saturday'), ('SU', 'Sunday')], 'Weekday')


    @api.multi
    def update_recurrency(self):
        for record in self:
            if record.recurrency:
                return {
                    'name': _('Recurrency Popup'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.warehouse.user.line.popup',
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                }