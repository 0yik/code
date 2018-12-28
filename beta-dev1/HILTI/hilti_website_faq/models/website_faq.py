from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError


class WebsiteFaqTags(models.Model):

    _name = "website.faq.tag"
    
    name = fields.Char('Name', required=True)
    
    _sql_constraints = [('website_faq_tags_unique', 'unique(name)', 'The same tag already exist.')]

    @api.model
    def create(self, vals):
        rec = self.search([('name', 'ilike', vals.get('name'))])
        if rec:
            raise UserError(_('The same tag already exist.'))
        return super(WebsiteFaqTags, self).create(vals)
    
    @api.multi
    def write(self, vals):
        rec = self.search([('name', 'ilike', vals.get('name'))])
        if rec:
            raise UserError(_('The same tag already exist.'))
        return super(WebsiteFaqTags, self).write(vals)

class website_question_answer(models.Model):

    _name = "website.question.answer"

    sequence = fields.Integer(index=True, default=1) 
    question = fields.Char('Question', required=True)
    answer = fields.Html('Answer', required=True)
    website_faq_id = fields.Many2one('website.faq', 'Website Faq')


class website_faq_type(models.Model):

    _name = "website.faq.type"
    _order = 'id ASC'
    
    name = fields.Char('Type Name', required=True)
#     faq_type = fields.Selection([
#         ('question_answer', 'General Q&A'),
#         ('user_manual', 'User Manual'),
#         ('instructional_video', 'Instructional Video')
#     ], string='FAQ Type', required=True, default='question_answer')
    

class WebsiteFAQ(models.Model):

    _name = "website.faq"
    _order = 'sequence ASC'
    
    sequence = fields.Integer()
    name = fields.Char('FAQ Title', required=True)
    faq_type_id = fields.Many2one('website.faq.type', string='FAQ Category')
    faq_type = fields.Selection([
        ('question_answer', 'General Q&A'),
        ('user_manual', 'User Manual'),
        ('instructional_video', 'Instructional Video')
    ], string='FAQ Type')
    faq_tags = fields.Many2many('website.faq.tag', string='Tags')
    website_question_answer_ids = fields.One2many('website.question.answer', 'website_faq_id','Question & Answer')
    sub_title = fields.Char('Subtitle')
    description = fields.Html('Description')
    user_manual_datas_fname = fields.Char('File Name')
    instructional_video_datas_fname = fields.Char('File Name')
    mimetype = fields.Char('Mime Type', readonly=True)
    user_manual = fields.Binary(string='File')
    instructional_video = fields.Binary(string='File')
    file_size = fields.Integer('File Size', readonly=True)
    
    
    @api.multi
    def write(self, vals):
        if vals.get('instructional_video'):
            vals['file_size'] = len(vals.get('instructional_video').decode('base64'))
            vals['mimetype'] = self.env['ir.attachment']._compute_mimetype({'datas_fname': vals.get('instructional_video_datas_fname')})
        if vals.get('user_manual'):
            vals['file_size'] = len(vals.get('user_manual').decode('base64'))
            vals['mimetype'] = self.env['ir.attachment']._compute_mimetype({'datas_fname': vals.get('user_manual_datas_fname')})
        return super(WebsiteFAQ, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('instructional_video'):
            vals['file_size'] = len(vals.get('instructional_video').decode('base64'))
            vals['mimetype'] = self.env['ir.attachment']._compute_mimetype({'datas_fname': vals.get('instructional_video_datas_fname')})
        if vals.get('user_manual'):
            vals['file_size'] = len(vals.get('user_manual').decode('base64'))
            vals['mimetype'] = self.env['ir.attachment']._compute_mimetype({'datas_fname': vals.get('user_manual_datas_fname')})
        if not vals.get('sequence'):
            rec = self.search([], limit=1, order='sequence DESC')
            if rec:
                vals['sequence'] = rec[0].sequence + 1
            else:
                vals['sequence'] = 0
        return super(WebsiteFAQ, self).create(vals)
    
#     user_manual = fields.Many2one('ir.attachment', 'User Manual')
#     instructional_video = fields.Many2one('ir.attachment', 'Video')
    