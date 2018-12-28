# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools, _

class StockWarehouseUserPopUp(models.TransientModel):
    _name = 'stock.warehouse.user.line.popup'

    line_id      = fields.Many2one('stock.warehouse.user.line')
    state        = fields.Selection([('draft', 'To Process'), ('process', 'In Progress'), ('done', 'Processed')], related='line_id.state')
    recurrency   = fields.Boolean('Recurrency', related='line_id.recurrency')
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

    # def save_popup(self, cr , uid, id ,context):
    #     # self.ensure_one()
    #     popup_obj = self.browse(cr, uid, id, context)
    #     id = popup_obj.id
    #     values = {
    #         'interval' : popup_obj[0]['interval'],
    #         'count'    : popup_obj[0]['count'],
    #         'end_type' : popup_obj[0]['end_type'],
    #         'rrule_type' : popup_obj[0]['rrule_type'],
    #         'recurrency' : popup_obj[0]['recurrency'],
    #         'final_date' : popup_obj[0]['final_date'],
    #         'mo' : popup_obj[0]['mo'],
    #         'tu' : popup_obj[0]['tu'],
    #         'we' : popup_obj[0]['we'],
    #         'th' : popup_obj[0]['th'],
    #         'fr' : popup_obj[0]['fr'],
    #         'sa' : popup_obj[0]['sa'],
    #         'su' : popup_obj[0]['su'],
    #         'month_by' : popup_obj[0]['month_by'],
    #         'day' : popup_obj[0]['day'],
    #         'byday' : popup_obj[0]['byday'],
    #         'week_list' : popup_obj[0]['week_list'],
    #         'starting_no' : popup_obj[0]['starting_no'],
    #         'teacher_id' : popup_obj[0]['teacher_id'],
    #     }
    #
    #     popup_obj[0].write(values)
