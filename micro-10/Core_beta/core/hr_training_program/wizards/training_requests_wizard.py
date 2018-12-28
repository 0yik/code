# -*- coding: utf-8 -*-

from openerp import models, fields, api

class TrainingRequestsWizard(models.TransientModel):
    _name = 'training.requests.wizard'

    request_id   = fields.Many2one('training.requests', string='Request')
    conducts_ids = fields.Many2many('training.conducts', string='Conducts')

    @api.model
    def default_get(self, fields):
        res = super(TrainingRequestsWizard, self).default_get(fields)
        context = self.env.context or {}
        if context.get('active_model', False) == 'training.requests' and context.get('active_id', False):
            if res is None:
                res = {}
            request_id = context.get('active_id')
            res.update({
                'request_id': request_id,
            })
        return res

    @api.onchange('request_id')
    def onchange_request_id(self):
        for record in self:
            if record.request_id and record.request_id.id:
                domain = [
                    ('status', '=', 'pending'),
                ]
                if record.request_id.trainingprogram and record.request_id.trainingprogram.id:
                    domain.append(('program_id', '=', record.request_id.trainingprogram.id))
                result = {'domain': {
                    'conducts_ids': domain
                }}
                return result

    @api.multi
    def action_confirm(self):
        context = self.env.context or {}
        if context.get('active_model', False) == 'training.requests' and context.get('active_id', False):
            request_id       = context.get('active_id')
            training_request = self.env['training.requests'].browse(request_id)
            if training_request and training_request.id:
                for record in self:
                    for training_conduct in record.conducts_ids:
                        # Register conduct item
                        conduct_item = {
                            'employee_id': training_request.employee and training_request.employee.id,
                            'remarks': training_request.remarks,
                            'status_list': 'success',
                            'program_id': training_request.trainingprogram and training_request.trainingprogram.id,
                            'data_start': fields.Date.today(),
                            'training_id': training_conduct and training_conduct.id,
                        }
                        self.env['list.conducts'].create(conduct_item)

                        # Register candidate
                        candidate_item = {
                            'employee': training_request.employee and training_request.employee.id,
                            # 'trainings_todo_ids': [(6, 0, conduct.ids)],
                            'job_training': training_request.job_position and training_request.job_position.id,
                        }
                        self.env['candidates.training'].create(candidate_item)

                        # Register

            training_request.state = 'approved'
