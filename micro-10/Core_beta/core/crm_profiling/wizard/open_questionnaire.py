# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _

class OpenQuestionnaireLine(models.TransientModel):
    _name = 'open.questionnaire.line'
    _rec_name = 'question_id'

    question_id = fields.Many2one('crm_profiling.question', 'Question', required=True)
    answer_id   = fields.Many2one('crm_profiling.answer', 'Answer')
    wizard_id   = fields.Many2one('open.questionnaire', 'Questionnaire')

class OpenQuestionnaire(models.TransientModel):
    _name = 'open.questionnaire'

    questionnaire_id = fields.Many2one('crm_profiling.questionnaire', 'Questionnaire name')
    question_ans_ids = fields.One2many('open.questionnaire.line', 'wizard_id', 'Question / Answers')

    @api.model
    def default_get(self, fields_list):
        res = super(OpenQuestionnaire, self).default_get(fields_list)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id') or []
        for record in self.env[active_model].browse(active_id):
            for question_lines in record.answers_ids:
                question_vals = {}
                question_vals['question_id'] = question_lines.question_id.id
                res['questionnaire_id'] = question_lines.question_id.id
                res['question_ans_ids'] = [(0,0,question_vals)]
        return res

    @api.multi
    def questionnaire_compute(self):
        """ Adds selected answers in partner form """
        model = self.env.context.get('active_model')
        answers = []
        if model == 'res.partner':
            for data in self:
                for d in data.question_ans_ids:
                     if d.answer_id:
                         answers.append(d.answer_id.id)
            self.env.get(model)._questionnaire_compute(answers)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def build_form(self):
        """ Dynamically generates form according to selected questionnaire """
        models_data = self.env.get('ir.model.data')
        result = models_data._get_id('crm_profiling', 'open_questionnaire_form')
        res_id = models_data.browse(result).res_id

        context = {}
        for data in self:
            context = dict(self.env.context or {}, questionnaire_id=data.questionnaire_id.id)

        return {
            'name': _('Questionnaire'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'open.questionnaire',
            'type': 'ir.actions.act_window',
            'views': [(res_id, 'form')],
            'target': 'new',
            'context': context
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: