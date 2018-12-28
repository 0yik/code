# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _
import datetime
from datetime import timedelta


class DocumentEpirteCron(models.Model):
    _name = 'document.expire.cron'
    _description = 'Document Epire Cron'

    @api.multi
    def _send_mail_document_expire(self):
        doc_type_ids = self.env['document.type'].search([])
        # doc_type_id for document type id
        # employee_id for employee id
        document_list = []
        for doc_type in doc_type_ids:
            # add days in today's date to get expire date
            date_expire = datetime.datetime.today().date() + timedelta(days=doc_type.duration)
            # based on expire date find document
            document_ids = self.env['employee.immigration'].search(
                [('exp_date', '=', fields.Date.to_string(date_expire)),
                 ('doc_type_id', '=', doc_type.id),
                 ])
            for document in document_ids:
                document_list.append(
                    {'employee': document.employee_id.name,
                     'document_type': document.doc_type_id and document.doc_type_id.name or '-',
                     'document': document.documents,
                     'expire_date': document.exp_date,
                     })
                expiring_vals = {}
                expiring_vals['expiry_name'] = document.documents
                expiring_vals['expiry_number'] = document.number
                expiring_vals['employee_id'] = document.employee_id.id
                expiring_vals['exp_date'] = document.exp_date
                expiring_vals['issue_date'] = document.issue_date
                expiring_vals['eligible_status'] = document.eligible_status
                expiring_vals['issue_by'] = document.issue_by and document.issue_by.id or False
                expiring_vals['eligible_review_date'] = document.eligible_review_date
                expiring_vals['doc_type_id'] = document.doc_type_id and document.doc_type_id.id or False
                expiring_vals['comments'] = document.comments
                expiring_vals['immigration_id'] = document.id
                expiring_vals['expiry_attachment'] = document.attach_document

                self.env['expiring.document'].create(expiring_vals)

        # search user with hr_manager access right
        if document_list:

            hr_manage_id = self.env.ref('hr.group_hr_manager').id
            user_ids = self.env['res.users'].search(
                    [('groups_id', 'in',  [hr_manage_id])])
            super_user_obj = self.env['res.users'].search([('id', '=', 1)])
            ctx = self._context.copy()
            ctx.update({'document_list': document_list})
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference(
                    'document_type_expiry',
                    'email_template_edi_document_expire')[1]
            except ValueError:
                template_id = False

            for user in user_ids:
                ctx.update({'email_to': user.email,
                            'email_from': super_user_obj.email,
                            'user_name': user.name,
                            })
                self.env['mail.template'].browse(template_id).with_context(
                    ctx).send_mail(self.id, force_send=True)

        return True


DocumentEpirteCron()
