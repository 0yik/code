# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Question(models.Model):
    """ Question """
    _name = 'crm_profiling.question'
    _description = 'Question'

    name        = fields.Char('Question', required=True)
    answers_ids = fields.One2many('crm_profiling.answer', 'question_id', 'Available Answers', copy=True)



class Questionnaire(models.Model):
    """ Questionnaire """
    _name = 'crm_profiling.questionnaire'
    _description = 'Questionnaire'

    name          = fields.Char('Questionnaire', required=True)
    description   = fields.Text('Description', required=True)
    questions_ids = fields.Many2many('crm_profiling.question', 'profile_questionnaire_quest_rel',\
                                'questionnaire', 'question', 'Questions')

class Answer(models.Model):
    _name = 'crm_profiling.answer'
    _description = 'Answer'

    name = fields.Char('Answer', required=True)
    question_id = fields.Many2one('crm_profiling.question', 'Question')

class Partner(models.Model):
    _inherit = 'res.partner'

    answers_ids = fields.Many2many('crm_profiling.answer', 'partner_question_rel',\
                                'partner', 'answer', 'Answers')

    @api.model
    def _questionnaire_compute(self, answers):
        partner_id = self._context.get('active_id')
        query = 'SELECT answer FROM partner_question_rel WHERE partner=%s'
        self._cr.execute(query, (partner_id,))
        for x in self._cr.fetchall():
            answers.append(x[0])
        partner = self.browse(partner_id)
        partner.answers_ids = [[6, 0, answers]]

    @api.multi
    def write(self, values):
        if 'answers_ids' in values:
            values['category_id'] = [[6, 0, self._recompute_categ(values['answers_ids'][0][2])]]
        return super(Partner, self).write(values)

    @api.multi
    def _recompute_categ(self, answers_ids):
        ok = []
        self._cr.execute('''
                SELECT r.category_id
                FROM res_partner_res_partner_category_rel r LEFT JOIN crm_segmentation s ON (r.category_id = s.categ_id)
                WHERE r.partner_id IN %s and (s.exclusif = false or s.exclusif is null)
                ''', (self._ids,))
        for x in self._cr.fetchall():
            ok.append(x[0])

        query = '''
                select id, categ_id
                from crm_segmentation
                where profiling_active = true'''
        if ok != []:
            query = query + ''' and categ_id not in(%s)''' % ','.join([str(i) for i in ok])
        query = query + ''' order by id '''

        self._cr.execute(query)
        segm_cat_ids = self._cr.fetchall()

        for (segm_id, cat_id) in segm_cat_ids:
            if self.env.get('crm.segmentation').browse([segm_id]).test_prof(self._ids, answers_ids):
                ok.append(cat_id)
        return ok


class crm_segmentation(models.Model):
    """ CRM Segmentation """

    _inherit = 'crm.segmentation'
    answer_yes = fields.Many2many('crm_profiling.answer', 'profile_question_yes_rel', \
                                  'profile', 'answer', 'Included Answers')
    answer_no  = fields.Many2many('crm_profiling.answer', 'profile_question_no_rel', \
                                 'profile', 'answer', 'Excluded Answers')
    parent_id  = fields.Many2one('crm.segmentation', 'Parent Profile')
    child_ids  = fields.Many2many('crm.segmentation', 'parent_id', 'Child Profiles')
    profiling_active = fields.Boolean('Use The Profiling Rules', help='Check\
                             this box if you want to use this tab as part of the \
                             segmentation rule. If not checked, the criteria beneath will be ignored')

    @api.multi
    def _get_parents(self):
        ids_to_check = []
        for id in self._ids:
            ids_to_check.append(id)
        parent_ids = [record.parent_id.id for record in self if record.parent_id]
        trigger = False
        for x in parent_ids:
            if x not in ids_to_check:
                ids_to_check.append(x)
                trigger = True
        if trigger:
            ids_to_check = self.browse(ids_to_check)._get_parents()
        return ids_to_check

    @api.multi
    def _get_answers(self):
        ans_yes = []
        ans_no  = []
        for record in self:
            ans_yes += [answer.id for answer in record.answer_yes]
            ans_no  += [answer.id for answer in record.answer_no]
        return [ans_yes, ans_no]

    @api.multi
    def test_prof(self, pid, answers_ids=None):

        """ return True if the partner pid fetch the segmentation rule seg_id
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param seg_id: Segmentaion's ID
            @param pid: partner's ID
            @param answers_ids: Answers's IDs
        """

        ids_to_check = self._get_parents()
        [yes_answers, no_answers] = self.browse(ids_to_check)._get_answers()
        temp = True
        for y_ans in yes_answers:
            if y_ans not in answers_ids:
                temp = False
                break
        if temp:
            for ans in answers_ids:
                if ans in no_answers:
                    temp = False
                    break
        if temp:
            return True
        return False

    @api.one
    @api.constrains('parent_id')
    def _check_parent_id(self):
        if self.parent_id and self.parent_id.id and self.parent_id.id == self.id:
            raise ValidationError("Error ! You cannot create recursive profiles.")

    @api.multi
    def process_continue(self, start=False):

        partner_obj = self.env.get('res.partner')
        categs = self.read(['categ_id','exclusif','partner_id', 'sales_purchase_active', 'profiling_active'])
        for categ in categs:
            if start:
                if categ['exclusif']:
                    self._cr.execute('DELETE FROM res_partner_res_partner_category_rel WHERE \
                            category_id IN %s', (categ['categ_id'],))
                    partner_obj.invalidate_cache(['category_id'])
            id = categ['id']

            self._cr.execute('select id from res_partner order by id ')
            partners = [x[0] for x in self._cr.fetchall()]

            if categ['sales_purchase_active']:
                to_remove_list=[]
                self._cr.execute('select id from crm_segmentation_line where segmentation_id=%s', (id,))
                line_ids = [x[0] for x in self._cr.fetchall()]

                for pid in partners:
                    lines = self.env.get('crm.segmentation.line').browse(line_ids)
                    if (not lines.test(pid)):
                        to_remove_list.append(pid)
                for pid in to_remove_list:
                    partners.remove(pid)

            if categ['profiling_active']:
                to_remove_list = []
                for pid in partners:

                    self._cr.execute('select distinct(answer) from partner_question_rel where partner=%s',(pid,))
                    answers_ids = [x[0] for x in self._cr.fetchall()]

                    if (not self.test_prof(pid, answers_ids)):
                        to_remove_list.append(pid)
                for pid in to_remove_list:
                    partners.remove(pid)

            for partner in partner_obj.browse(partners):
                category_ids = [categ_id.id for categ_id in partner.category_id]
                if categ['categ_id'][0] not in category_ids:
                    self._cr.execute('insert into res_partner_res_partner_category_rel (category_id,partner_id) values (%s,%s)', (categ['categ_id'][0],partner.id))
                    partner_obj.invalidate_cache(['category_id'], [partner.id])

        self.write({'state':'not_running', 'partner_id': 0})
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: