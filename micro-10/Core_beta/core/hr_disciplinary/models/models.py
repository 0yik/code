# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DisciplinaryStage(models.Model):
    _name='disciplinary.stage'
    _rec_name='disciplinary_name'

    disciplinary_name=fields.Char(String="Disciplinary Name", required=True)
    disciplinary_stage=fields.Integer(String="Disciplinary Stage", required=True)
    valid_for_months=fields.Integer(String="Valid for (months)", required=True)
    after_x_days=fields.Integer(String="After", required=True)
    # manual_action=fields.Boolean(String="Manual Action")
    send_email=fields.Boolean(String="Send an Email")
    # send_letter=fields.Boolean(String="Send a Letter")
    assign_a_responsible=fields.Many2one('hr.employee', String="Assign a Responsible")
    # action_to_do=fields.Text(required=True)
    letter_content=fields.Text()
    sequence=fields.Char(String="Sequence")

class DisciplinaryHistory(models.Model):
    _name = 'disciplinary.history'

    date_diciplined = fields.Date('Date Disciplined')
    disciplinary_stage = fields.Many2one('disciplinary.stage')
    valid_until = fields.Date()
    reason_disciplinary=fields.Text(string="Reason of Disciplinary", required=True)
    manual_action=fields.Text(string="Action Taken")
    employee_id = fields.Many2one('hr.employee')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    disciplinary_history_ids = fields.One2many('disciplinary.history', 'employee_id')