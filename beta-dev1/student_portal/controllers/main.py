# -*- encoding: utf-8 -*-

import odoo
import odoo.modules.registry
import ast

from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home

import datetime
import json
import pytz
import os
from odoo.addons.school_enrolment_paypal.controllers.main import WebsitePayment
import logging

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# OpenERP Web web Controllers
#----------------------------------------------------------

class WebsitePayment(WebsitePayment):

    @http.route(['/website_payment/transaction'], type='json', auth="public", website=True)
    def transaction(self, reference, amount, currency_id, acquirer_id):
        res = super(WebsitePayment, self).transaction(reference=reference, amount=amount, currency_id=currency_id, acquirer_id=acquirer_id)
        pay_tra_id = request.env['payment.transaction'].sudo().browse(res)
        ref = reference[reference.rfind('-')+1:]
        inv_ref = reference
        if inv_ref and pay_tra_id:
            request.session.update({'invoice_number':reference})
            if inv_ref.startswith('INV/'):
                invoice_id = request.env['account.invoice'].sudo().search([('number','=',inv_ref)])    
                pay_tra_id.invoice_id = invoice_id.id
        return res

    @http.route(['/website_payment/confirm'], type='http', auth='public', website=True)
    def confirm(self, **kw):
        # print "request.session ==============",request.session.get('invoice_number')
        tx_id = request.session.pop('website_payment_tx_id', False)
        values = {'tx_id':tx_id, 'without_paypal':False}
        if tx_id:
            tx = request.env['payment.transaction'].sudo().browse(tx_id)
            status = (tx.state == 'done' and 'success') or 'danger'
            message = (tx.state == 'done' and _('Your payment was successful! It may take some time to be validated on our end.')) or _('Oops! There was a problem with your payment.')
            inv_ref = request.session.get('invoice_number')
            if inv_ref.startswith('INV/'):
                invoice_id = request.env['account.invoice'].sudo().search([('number','=',inv_ref)])
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                action_id = request.env.ref('account.action_invoice_tree1')
                menu_id = request.env.ref('student_portal.menu_action_invoice_tree1_modifier')
                if menu_id and action_id and invoice_id:
                    url = base_url + '/web?#id=' + str(invoice_id.id) + '&view_type=form&model=account.invoice&menu_id=' + str(menu_id.id) + '&action=' + str(action_id.id)
                    return request.redirect(url)
                else:
                    return request.render('website.home',{})
            return request.render('online_school_enrollment.thanks', values)
        else:
            return request.render('online_school_enrollment.thanks', values)

class StudentPortal(http.Controller):

    _items_per_page = 5

    # Main student Portal home page
    @http.route(['/student/portal/home'], type='http', auth="user", website=True)
    def student_portal_home(self, **kw):
        values = {}
        return request.render("student_portal.student_portal_my_home", values)

    # Student Portal Invoices
    
    @http.route(['/student/portal/invoices', '/student/portal/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def student_portal_invoices(self, page=1, **kw):
        partner = request.env.user.partner_id
        payslip = request.env['student.payslip']
        account_invoice = request.env['account.invoice']
        student_id = request.env['student.student'].search([('user_id','=',request.env.user.id)], limit=1)
        values = {}
        domain = []
        student_invoice_ids = False
        if student_id:
            payslip_ids = payslip.search([('student_id','=',student_id.id)])
            domain = [('student_payslip_id','in',payslip_ids.ids or [])] 
            # student_invoice_ids = account_invoice.search([('student_payslip_id','in',payslip_ids.ids or [])])
            # count for pager
            invoice_count = account_invoice.search_count(domain)
            # pager
            pager = request.website.pager(
                url="/student/portal/invoices",
                total=invoice_count,
                page=page,
                step=self._items_per_page
            )
            student_invoice_ids = account_invoice.search(domain, limit=self._items_per_page, offset=pager['offset'], order='id')
            # content according to pager and archive selected
            values.update({
                'invoices': student_invoice_ids,
                'page_name': 'invoice',
                'pager': pager,
                'default_url': '/student/portal/invoices',
            })
        return request.render("student_portal.student_portal_invoices_template", values)

    # Student Reminders
    @http.route(['/student/portal/reminders', '/student/portal/reminders/page/<int:page>'], type='http', auth="user", website=True)
    def student_portal_reminder(self, page=1, **kw):
        partner = request.env.user.partner_id
        reminder_obj = request.env['student.reminder']
        student_id = request.env['student.student'].search([('user_id','=',request.env.user.id)], limit=1)
        values = {}
        domain = []
        student_reminder_ids = False
        if student_id:
            domain = [('stu_id','=',student_id.id)]
            # count for pager
            reminder_count = reminder_obj.search_count(domain)
            # pager
            pager = request.website.pager(
                url="/student/portal/reminders",
                total=reminder_count,
                page=page,
                step=self._items_per_page
            )
            student_reminder_ids = reminder_obj.search(domain, limit=self._items_per_page, offset=pager['offset'], order='id')
            # content according to pager and archive selected
            values.update({
                'reminders': student_reminder_ids,
                'page_name': 'reminders',
                'pager': pager,
                'default_url': '/student/portal/reminders',
            })
        return request.render("student_portal.student_portal_reminders_template", values)

    # Main student Portal Profile 
    @http.route(['/student/portal/profile'], type='http', auth="user", website=True)
    def student_portal_profile(self, **kw):
        partner = request.env.user.partner_id
        student_id = request.env['student.student'].search([('user_id','=',request.env.user.id)], limit=1)
        country_ids = request.env['res.country'].sudo().search([])
        state_ids = request.env['res.country.state'].sudo().search([])
        mother_tongue_ids = request.env['mother.toungue'].sudo().search([])
        general_survey_ids = request.env['general.survey'].sudo().search([])
        highest_qualification_ids = request.env['highest.qualification'].sudo().search([])
        values = {'student_profile': student_id,
                'gender':student_id.gender,
                'school_ids':student_id.sudo().school_id,
                'standard_ids': student_id.sudo().standard_id,
                'year_ids': student_id.sudo().year,
                'country_id': student_id.sudo().country_id,
                'country_ids': country_ids,
                'state_id': student_id.sudo().state_id,
                'state_ids': state_ids,
                'marital_status': student_id.maritual_status,
                'mother_tongue_ids': mother_tongue_ids,
                'mother_tongue_id': student_id.sudo().mother_tongue,
                'income':student_id.sudo().income,
                'general_survey_ids': general_survey_ids,
                'general_survey_id': student_id.sudo().general_survey_id,
                'highest_qualification_ids': highest_qualification_ids,
                'highest_qualification_id': student_id.sudo().highest_qualification_id,
                'references_ids': student_id.sudo().reference_ids,
                'parent_ids': student_id.sudo().parent_id,
                'education_background_ids': student_id.sudo().education_background_id,
                'family_ids': student_id.sudo().family_con_ids,
        }
        return request.render("student_portal.student_portal_profile_template", values)

    # Main student Portal Classes Schedules 
    @http.route(['/student/portal/schedulers', '/student/portal/schedulers/page/<int:page>'], type='http', auth="user", website=True)
    def student_portal_classes_schedulers(self, page=1, **kw):
        values = {}
        partner = request.env.user.partner_id
        ems_class_student_line_obj = request.env['ems.class.student.line']
        ems_class_obj = request.env['ems.class']
        ems_class_list = []
        student_id = request.env['student.student'].sudo().search([('user_id','=',request.env.user.id)], limit=1)
        student_reminder_ids = False
        if student_id:
            class_line_ids = ems_class_student_line_obj.sudo().search([('student_id','=',student_id.id)])
            for ems_id in class_line_ids:
                ems_class_list.append(ems_id.ems_id.id)
            domain = [('id','in',ems_class_list)] 
            # count for pager
            ems_class_count = len(ems_class_list)
            # pager
            pager = request.website.pager(
                url="/student/portal/schedulers",
                total=ems_class_count,
                page=page,
                step=self._items_per_page
            )
            ems_class_ids = ems_class_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'], order='id')
            # content according to pager and archive selected
            values.update({
                'ems_class_ids': ems_class_ids,
                'page_name': 'schedulers',
                'pager': pager,
                'default_url': '/student/portal/schedulers',
            })
        return request.render("student_portal.student_portal_classes_schedulers_template", values)

    # Main student Portal Assignment 
    @http.route(['/student/portal/assignment', '/student/portal/assignment/page/<int:page>'], type='http', auth="user", website=True)
    def student_portal_assignment(self, page=1, **kw):
        values = {}
        partner = request.env.user.partner_id
        assignment_obj = request.env['student.assignment']
        student_id = request.env['student.student'].search([('user_id','=',request.env.user.id)], limit=1)
        if student_id:
            domain = [('student_id','=',student_id.id)]
            # count for pager
            assignment_count = assignment_obj.search_count(domain)
            # pager
            pager = request.website.pager(
                url="/student/portal/assignment",
                total=assignment_count,
                page=page,
                step=self._items_per_page
            )
            student_assignment_ids = assignment_obj.search(domain, limit=self._items_per_page, offset=pager['offset'], order='id')
            # content according to pager and archive selected
            values.update({
                'assignment_ids': student_assignment_ids,
                'page_name': 'reminders',
                'pager': pager,
                'default_url': '/student/portal/assignment',
            })
        return request.render("student_portal.student_portal_assignment_template", values)

    # Main student Portal Exam Result
    @http.route(['/student/portal/exam', '/student/portal/exam/page/<int:page>'], type='http', auth="user", website=True)
    def student_portal_exam(self, page=1, **kw):
        values = {}
        partner = request.env.user.partner_id
        exam_obj = request.env['exam.exam']
        student_id = request.env['student.student'].sudo().search([('user_id','=',request.env.user.id)], limit=1)
        if student_id:
            domain = [('academic_year','=',student_id.year.id)]
            # count for pager
            exam_count = exam_obj.sudo().search_count(domain)
            # pager
            pager = request.website.pager(
                url="/student/portal/exam",
                total=exam_count,
                page=page,
                step=self._items_per_page
            )
            student_exam_ids = exam_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'], order='id')
            # content according to pager and archive selected
            values.update({
                'exam_ids': student_exam_ids,
                'page_name': 'result',
                'pager': pager,
                'default_url': '/student/portal/exam',
            })
        return request.render("student_portal.student_portal_exam_template", values)

    # Main student Portal Exam Result
    @http.route(['/student/portal/exam/result', '/student/portal/exam/result/page/<int:page>'], type='http', auth="user", website=True)
    def student_portal_exam_result(self, page=1, **kw):
        values = {}
        partner = request.env.user.partner_id
        exam_result_obj = request.env['exam.result']
        student_id = request.env['student.student'].sudo().search([('user_id','=',request.env.user.id)], limit=1)
        if student_id:
            domain = [('student_id','=',student_id.id)]
            # count for pager
            result_count = exam_result_obj.sudo().search_count(domain)
            # pager
            pager = request.website.pager(
                url="/student/portal/exam/result",
                total=result_count,
                page=page,
                step=self._items_per_page
            )
            student_exam_result_ids = exam_result_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'], order='id')
            # content according to pager and archive selected
            values.update({
                'exam_result_ids': student_exam_result_ids,
                'page_name': 'result',
                'pager': pager,
                'default_url': '/student/portal/exam/result',
            })
        return request.render("student_portal.student_portal_exam_result_template", values)

    # Main student Portal Monthly Attendance Sheet
    @http.route(['/student/portal/attendance', '/student/portal/attendance/page/<int:page>'], type='http', auth="user", website=True)
    def student_portal_attendance(self, **kw):
        values = {}
        return request.render("student_portal.student_portal_attendance_template", values)

    # Student Profile Update
    @http.route(['/student/profile/update'], type='http', auth="public", website=True, csrf=False)
    def student_profile_update(self, **post):
        partner = request.env.user.partner_id
        student_id = request.env['student.student'].search([('user_id','=',request.env.user.id)], limit=1)
        vals = {
                'name': post.get('first_name',False) or '',
                'gender': post.get('gender',False),
                'street':post.get('address1',False),
                'street2':post.get('address2',False),
                'state_id':post.get('state_ids',False) and int(post.get('state_ids',False)),
                'zip':post.get('zip',False),
                'country_id':post.get('country_ids',False) and int(post.get('country_ids',False)),
                'phone':post.get('phone',False),
                'mobile':post.get('mobile',False),
                'email':post.get('email',False),
                'contact_phone1':post.get('phone_no',False),
                'contact_mobile1':post.get('mobile_no',False),
                'nric':post.get('nric',False),
                'maritual_status': post.get('marital_status',False),
                'hp_no':post.get('hp_no',False),
                'occupation': post.get('occupation',False),
                'income': '' if post.get('income',False) == 'select_income' else post.get('income',False) ,
                'citizenship': post.get('citizenship',False),
                'remark': post.get('qualification_remark',False),
                'mother_tongue': post.get('mother_tongue_ids',False) and int(post.get('mother_tongue_ids',False)),
                }
        if student_id:
            student_id.sudo().write(vals)
        return request.redirect("/student/portal/profile")

    # Student Assignment update
    @http.route(['/student/profile/assignment/update'], type='http', auth="public", website=True, csrf=False)
    def student_profile_assignment_update(self, **post):
        partner = request.env.user.partner_id
        attachments = request.env['ir.attachment']
        student_id = request.env['student.student'].search([('user_id','=',request.env.user.id)], limit=1)
        file_data = False
        val = {}
        if post.get('fileupload'):
            file_data = post.get('fileupload').read()
            val = {'name': post.get('file_name'),
                    'datas': file_data.encode('base64'),
                    'datas_fname': post.get('file_name'),
                    }
        attachment_id = False
        if student_id and post.get('assignment_id'):
            val.update({'res_id':int(post.get('assignment_id')), 'res_model': 'student.assignment'})
            attachment_id = attachments.sudo().create(val)
        if student_id and post.get('assignment_id'):
            assignment_id = request.env['student.assignment'].browse(int(post.get('assignment_id')))
            assignment_id.sudo().write({'attachment_result':attachment_id.datas,'file_result':post.get('file_name')})
        return request.redirect("/student/portal/assignment")

    
    @http.route(['/student/assignment/remove/<int:assignment_id>'], type='http', auth="public", website=True)
    def student_assignment_remove(self, assignment_id, **post):
        assignment_id = request.env['student.assignment'].browse(assignment_id)
        assignment_id.attachment_result = False
        return request.redirect("/student/portal/assignment")

    # Main student Portal Grades
    @http.route(['/student/portal/grades', '/student/portal/grades/page/<int:page>'], type='http', auth="user", website=True)
    def student_portal_grades(self, page=1, **kw):
        values = {}
        partner = request.env.user.partner_id
        grades_obj = request.env['overall.gpa']
        gpa_line_obj = request.env['gpa.line']
        grade_line_ids = []
        student_id = request.env['student.student'].sudo().search([('user_id','=',request.env.user.id)], limit=1)
        if student_id:
            domain = [('student_id','=',student_id.id)]
            # count for pager
            grades_ids = grades_obj.search(domain)
            domain = [('gpa_id','in',grades_ids.ids)]
            gpa_line_ids = gpa_line_obj.sudo().search(domain)
            gpa_line_count = gpa_line_obj.sudo().search_count(domain)
            # pager
            pager = request.website.pager(
                url="/student/portal/grades",
                total=gpa_line_count,
                page=page,
                step=self._items_per_page
            )
            student_grades_ids = gpa_line_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'], order='id')
            
            # content according to pager and archive selected
            values.update({
                'student_grades_ids': student_grades_ids,
                'page_name': 'result',
                'pager': pager,
                'default_url': '/student/portal/grades',
            })
        return request.render("student_portal.student_portal_grades_template", values)

    # @http.route(['/invoice/payment'], type='http', auth="public", website=True, csrf=False)
    # def student_invoice_payment(self, **post):
    #     if post.get('invoice_id'):
    #         env = request.env
    #         user = env.user.sudo()
    #         invoice_id = post.get('invoice_id',False) and int(post.get('invoice_id',False))
    #         invoice_id = request.env['account.invoice'].sudo().browse(invoice_id)
    #         user_id = request.env['res.users'].sudo().search([('partner_id','=',invoice_id.partner_id.id)], limit=1)
    #         student_id = request.env['student.student'].sudo().search([('user_id','=',user_id and user_id.id or False)])
    #         reference = invoice_id.partner_id.name + '-' + invoice_id.number + '-' + str(student_id.id)
    #         amount = invoice_id.amount_total
    #         partner_id = False
    #         acquirer_id = False
    #         currency = invoice_id.currency_id
    #         acquirer_id = env['payment.acquirer'].search([('provider', '=', 'paypal'), ('website_published', '=', True)], limit=1)
    #         acquirer_id = acquirer_id and acquirer_id.id
    #         acquirer = env['payment.acquirer'].with_context(submit_class='btn btn-primary pull-right',
    #                                                         submit_txt=_('Pay Now')).browse(acquirer_id)
    #         # auto-increment reference with a number suffix if the reference already exists
    #         base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #         payment_form = acquirer.sudo().render(reference, float(amount), currency.id, values={'return_url': '/website_payment/confirm'})
            
    #         values = {
    #             'reference': reference,
    #             'acquirer': acquirer,
    #             'currency': currency,
    #             'amount': float(amount),
    #             'payment_form': payment_form,
    #         }
    #         return request.render('school_enrolment_paypal.admission_payment', values)



