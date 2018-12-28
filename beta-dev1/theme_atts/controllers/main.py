# -*- coding: utf-8 -*-
import base64
import werkzeug

from odoo import fields, http, SUPERUSER_ID, _
from odoo.http import request
from odoo.addons.website.models.website import slug
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.web.controllers.main import binary_content
import logging

_logger = logging.getLogger(__name__)

class Web(Home):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(Web, self).web_login(*args, **kw)
        redirect = request.params.get('redirect')
        if request.session.uid:
            if request.env.user.partner_id.student_type == 'corporate':
                redirect = '/page/corporate_access'
            if not redirect and request.params['login_success']:
                if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
                    redirect = '/web?' + request.httprequest.query_string
                else:
                    redirect = '/'
            return http.redirect_with_hash(redirect)
        return response

class AuthSignupHome(AuthSignupHome):

    @http.route()
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                if request.session.uid:
                    if request.env.user.partner_id.student_type == 'corporate':

                        school_admins = [user.email for user in request.env['res.users'].sudo().search([]) if user.has_group('atts_course.group_school_administration') and user.email]
                        if len(school_admins) > 0:
                            template = request.env.ref('theme_atts.atts_notify_corporate_user')
                            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
                            ctx = {}
                            db = request.env.cr.dbname
                            action = request.env.ref('base.action_res_users')
                            ctx['user_name'] = request.env.user.name
                            ctx['school_admins'] = ','.join(school_admins)
                            ctx['action_url']  = "{}/web?db={}#id={}&view_type=form&action={}&model=res.users".format(base_url, db, request.env.uid, action.id)
                            template.with_context(ctx).sudo().send_mail(request.env.user.company_id.id, force_send=True)

                        request.env.user.active = False
                        redirect = '/page/atts_corporate_welcome_page'
                        return http.redirect_with_hash(redirect)
                return super(AuthSignupHome, self).web_login(*args, **kw)
            except (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("ATTS: don't allow user to create account with same email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not create a new account.")

        if 'error' in qcontext:
            if qcontext.get('password', False) != qcontext.get('confirm_password', False):
                qcontext['error'] = _("Your password and confirmation password do not match.")
        return request.render('auth_signup.signup', qcontext)

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'student_type', 'company_name', 'fax_no', 'uen_no_company_number', 'company_address') }
        values['name'] = values['login']
        assert values.values(), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()


class WebsiteATTS(http.Controller):

    @http.route([
        "/course_calendar/pdf",
        "/course_calendar/pdf/<model('registration.files'):file>",
        ], type='http', auth="public", website=True)
    def course_calendar_pdf(self, file=None, **post):
        if file:
            status, headers, content = binary_content(model='registration.files', id=file.id, field='registration_file', filename_field='filename', env=request.env(user=SUPERUSER_ID))
            content_base64 = base64.b64decode(content) if content else ''
            headers.append(('Content-Length', len(content_base64)))
            return request.make_response(content_base64, headers)
        return werkzeug.wrappers.Response(status=404)

        classes = request.env['class.class'].sudo().search([('date_start', '>=', fields.Datetime.now())])
        class_list = dict()
        for c in classes:
            if c.course_id not in class_list:
                class_list.update({c.course_id: request.env['class.class']})
            class_list[c.course_id] = class_list[c.course_id] + c
        pdf = request.env['report'].sudo().with_context(set_viewport_size=True, class_list=class_list).get_pdf(classes.ids, 'theme_atts.report_course_calendar')
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/course/class_infos/<model("subject.subject"):course>'], type='json', auth="public", methods=['POST'], website=True)
    def country_infos(self, course, **kw):
        return dict(
            classes=[(c.id, c.class_schedule) for c in request.website.get_course_class(course=course)],
        )

    @http.route(['/course/detail/<int:course>'], type='http', auth="public", website=True)
    def find_course_detail(self, course=None, **kw):
        values = {}
        if not course or course == 0:
            return http.local_redirect('/course/0')
        values['course'] = request.env['subject.subject'].sudo().browse(course)
        return request.render("theme_atts.course_detail", values)

    @http.route(['/course', '/course/<int:course>', '/course/level/<int:course_level>', '/industry', '/industry/<int:industry>'], type='http', auth="public", website=True)
    def find_course_industry(self, course=None, industry=None, course_level=None, **kw):
        values = {}
        domain = []
        if 'search' in kw and kw['search']:
            if 'course_title' in kw and kw['course_title'] != '0':
                domain = [('id', '=', kw.get('course_title', False))]
            elif 'class_date' in kw and kw['class_date'] != '0':
                classes = request.env['class.class'].sudo().search([('id', '=', kw.get('class_date', False))])
                if classes:
                    domain = [('id', 'in', [cls.course_id.id for cls in classes])]
            values['search_class_id'] = kw.get('class_date', False)
            course = 0
        if course or course == 0:
            if course == 0:
                course_id = [course for course in request.env['subject.subject'].sudo().search(domain)]
                values['is_all_course'] = True
            else:
                course_id = [request.env['subject.subject'].sudo().browse(course)]
            values['is_course'] = True
            values['course_id'] = course
            values['course_ids'] = course_id
            values['course'] = course_id and course_id[0] or 0
        if industry or industry == 0:
            if industry == 0:
              course_ids = [course for course in request.env['subject.subject'].sudo().search([])]
              values['is_all_industry'] = True
            else:
                course_ids = [course_id for course_id in request.env['subject.subject'].sudo().search([('industry_level', 'in', industry)])]
            values['is_industry'] = True
            values['industry_id'] = industry
            values['course_ids'] = course_ids
            values['industry'] = request.env['course.industry'].sudo().browse(industry)
        if course_level or course_level == 0:
            if course_level == 0:
                course_ids = [course for course in request.env['subject.subject'].sudo().search(domain)]
                values['is_all_course'] = True
            else:
                course_ids = [course_id for course_id in request.env['subject.subject'].sudo().search([('course_level', 'in', course_level)])]
            values['is_course'] = True
            values['course_id'] = course_level
            values['course_ids'] = course_ids
            values['course'] = request.env['course.level'].sudo().browse(course_level)
        return request.render("theme_atts.course_industry", values)

    @http.route(['/course/<int:course>/register'], type='http', auth="public", website=True)
    def course_register(self, course=None, **kw):
        user = request.env['res.users'].browse(request.uid)
        course_id = request.env['subject.subject'].sudo().browse(course)
        values = {
            'course': course_id,
            'countries': request.env['res.country'].search([]),
            'all_courses': [course for course in request.env['subject.subject'].sudo().search([])],
            'user': user,
            'student': user.student_id,
            'register_status': 'false',
        }
        if 'course_class' in kw:
            class_id = request.env['class.class'].sudo().search([('id', '=', kw.get('course_class'))])[0]
            values['class_id'] = class_id
        if not request.session.uid:
            return http.local_redirect('/web/login?redirect=/course/%s/register/?course_class=%s&redirect=/course/0' %(course_id.id or 0, kw.get('course_class')))
        if 'save' in kw and kw['save']:
            vals = {}
            if user.student_type == 'corporate':
                if 'individual_billing' not in kw or kw['individual_billing'] == '':
                    kw['individual_billing'] = False
                register_fields = ['class_id', 'name', 'contact_number', 'company_name', 'fax_no', 'uen_no_company_number', 'email', 'mail_address', 'certi_mailing_add', 'payment_method', 'individual_billing']
                delegate_details_list = ['is_delegate', 'delegate_name', 'delegate_date', 'delegate_nationality', 'delegate_designation', 'country_id', 'dietary_request', 'delegate_number', 'delegate_email']
                delegate_details_dict = []
                for delegate in delegate_details_list:
                    delegate_dict = None
                    for idx, val in enumerate(request.httprequest.form.getlist(delegate)):
                        delegate_dict = delegate_details_dict.pop(idx) if len(delegate_details_dict) > idx else (0, 0, dict())
                        if delegate == 'delegate_number':
                            val = request.httprequest.form.getlist('phone_country_code')[idx] + ' ' + val
                        delegate_dict[2][delegate] = val or False
                        if delegate_dict:
                            delegate_details_dict.insert(idx, delegate_dict)
                vals['delegate_lines'] = delegate_details_dict
            else:
                register_fields = ['class_id', 'name', 'nric_passport', 'nationality', 'country_id', 'date_of_birth', 'contact_number', 'email', 'mail_address', 'company_name', 'job_title', 'dietary_request', 'dietary_request_comment', 'payment_method', 'payment_deadline']
            for field in register_fields:
                if field == 'contact_number':
                    vals[field] = kw['phone_country_code'] + ' ' + kw[field]
                else:
                    vals[field] = kw[field]
            vals['registration_type'] = user.student_type
            vals['registration_id'] = 'New'

            vals['student_id'] = user.student_id.id
            registration = request.env['class.registration'].sudo().create(vals)

            for file in request.httprequest.files.getlist('course_document'):
                attachment_value = {
                    'name': file.filename,
                    'datas': base64.encodestring(file.read()),
                    'datas_fname': file.filename,
                    'res_model': 'class.registration',
                    'res_id': registration.id,
                }
                attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
            values['register_status'] = registration.id and 'success' or 'error'

            if user.student_id:
                vals.pop('delegate_lines', None)
                vals.pop('class_id', None)
                user.student_id.write(vals)

            if registration:
                school_admins = [user.email for user in request.env['res.users'].sudo().search([]) if user.has_group('atts_course.group_school_administration') and user.email]
                if len(school_admins) > 0:
                    template = request.env.ref('theme_atts.atts_notify_class_registration_user')
                    ctx = {}
                    ctx['student_name'] = registration.name
                    ctx['school_admins'] = ','.join(school_admins)
                    ctx['class_display_name'] = registration.class_id.display_name
                    template.with_context(ctx).sudo().send_mail(user.id, force_send=True)
        if user.student_type == 'corporate':
            return request.render("theme_atts.course_registration_corporate", values)
        return request.render("theme_atts.course_registration_individual", values)

    @http.route(['/page/document_download'], type='http', auth="public", website=True)
    def document_download(self, **kw):
        student_id = request.env['res.users'].browse(request.uid).student_id
        attachment_ids =  request.env['ir.attachment'].sudo().search([('res_model', '=', 'student.student'), ('res_id', '=', student_id.id)])
        values = {
            'document_ids': attachment_ids,
        }
        return request.render("website.document_download", values)

    @http.route(['/page/search_certificate'], type='http', auth="public", website=True)
    def search_certificate(self, **kw):
        values = {
            'no_result': False,
            'key': '',
        }
        if 'key' in kw:
            certificate_ids = [course for course in request.env['class.student.list'].sudo().search([('certification_no' , '=', kw.get('key'))])]
            if not certificate_ids:
                values['no_result'] = True
            values['certificate_ids'] = certificate_ids
            values['key'] = kw.get('key')
        return request.render("theme_atts.search_certificate", values)

