from odoo import api, fields, models

class hide_hide(models.TransientModel):
    _name = 'hide.menu'

    @api.model
    def hide_menu(self):

        account_analytic_account_obj = self.env['account.analytic.account'].search([])

        for account_analytic_account in account_analytic_account_obj:
            if account_analytic_account.is_project == False:
                account_analytic_account.is_project = False

class hr_education_information(models.Model):
    _inherit = 'hr.education.information'

    institution = fields.Text('Institution')
    country_id =fields.Many2one('res.country','Country')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    language_of_instruction = fields.Text('Language Of Instruction')
    qualification_obtained = fields.Text('Qualification Obtained')
    attachments = fields.Binary('Attachments')
    remarks = fields.Text('Remarks')