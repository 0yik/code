# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResQuestionnaireConfig(models.Model):
    _name = 'res.questionnaire.config'

    name = fields.Char('Questionnaire Name')
    question_lines = fields.One2many('res.question.line', 'questionnaire_config_id', string='Questions')


class ResQuestionLines(models.Model):
    _name = 'res.question.line'

    questionnaire_config_id = fields.Many2one('res.questionnaire.config', string='Questionnaire')
    name = fields.Char('Question')


class ResQuestionnaire(models.Model):
    _name = 'res.questionnaire'
    _rec_name = 'partner_id'

    @api.multi
    @api.depends('question_lines')
    def _get_total_points(self):
        for rec in self:
            total_points = 0
            for one_question in rec.question_lines:
                if one_question.point:
                    total_points += int(one_question.point)
            rec.total_points = total_points

    partner_id = fields.Many2one('res.partner','Customer')
    res_questionnaire_config_id = fields.Many2one('res.questionnaire.config',string='Questionnaire Set')
    question_lines = fields.One2many('res.questionnaire.lines', 'questionnaire_id', string='Questions')
    total_points = fields.Integer(compute='_get_total_points', store=True, string='Total Points')

    @api.onchange('res_questionnaire_config_id')
    def _change_res_questionnaire_config_id(self):
        self.question_lines = []
        if self.res_questionnaire_config_id:
            questions = []
            for one_question in self.res_questionnaire_config_id.question_lines:
                questions.append((0,0,{
                    'question_id': one_question.id
                }))
            self.question_lines = questions


class ResQuestionnaireLines(models.Model):
    _name = 'res.questionnaire.lines'
    _rec_name = 'question_id'

    questionnaire_id = fields.Many2one('res.questionnaire', string='Questionnaire')
    question_id = fields.Many2one('res.question.line', string='Question')
    point = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string='Point')

