# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import werkzeug


class CxaCallfunction(http.Controller):
    @http.route('/pbx', type="http", auth="user")
    def render_helpdesk(self, **post):
        print "post---->>>", post['cl']

        # temp = post['cl'].split('?qc=')
        # print "temp>>>>>>", temp[0], temp[1]
        # post = {'cl': temp[0], 'qc': temp[1]}

        print "NEW POST", post

        # cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        redirect_url, partner_ids = '/', []

        print "request.ids*********"

        partner_obj = request.env['res.partner']
        helpdesk_obj = request.env['helpdesk.ticket']
        categ_obj = request.env['helpdesk.ticket.type']
        employee_history = request.env['employee.history']
        partner_ids = []
        if not 'qc' in post:
            print "*****OUT--1"
            return werkzeug.utils.redirect(redirect_url)
        categ_ids = categ_obj.search([('type', '=', post['qc'])])
        categ_name, categ_id = '', False
        if categ_ids:
            categ = categ_obj.browse(categ_ids.id)
            categ_name, categ_id = categ.name, categ.id
        if not categ_id:
            print "*****OUT---2"
            return werkzeug.utils.redirect(redirect_url)
        # if 'uid' in post:
        #     partner_ids = partner_obj.search(cr, uid, [('customer_id', '=', post['uid'])], context=context)
        if not partner_ids and 'cl' in post:
            partner_ids = partner_obj.search([('phone', '=', post['cl'])])

        redirect_url = '/web#id=%(helpdesk_id)d&view_type=form&model=crm.helpdesk&menu_id=%(menu_id)d&action=%(action_id)d'
        params = {}
        partner_id = partner_ids and partner_ids.id or False

        # categ_name = "XXX"
        print "categ_id----------->>", categ_id
        ##
        partner_name = ""
        if partner_id:
            print "partner_id-------->", partner_id
            partner = partner_obj.browse(partner_id)
            partner_name = partner.name
            print "partner_name-------->", partner_name
            if partner.parent_id:
                company_id = partner.parent_id.id
                company_name = partner.parent_id.name
            # company_id = helpdesk_obj.get_entity(partner)
            # company = employee_history.browse(company_id)
            # if company and company.emp_company and company.emp_company.name:
            #     partner_name = company.emp_company.name
            #     print "company_name-------->", partner_name
        ##
        phone = ''
        if not partner_id:
            phone = post['cl']
        # department_sales_team = request.env['crm.case.section'].search([('name', '=', 'Contact Centre')],
        #                                                             limit=1)
        # department_sales_team = department_sales_team[0] if department_sales_team != [] else False
        helpdesk_data = {
            'name': categ_name + ' - ' + partner_name or " ",
            'partner_id': partner_id,
            'ticket_type_id': categ_id,
            ##
            # 'respond_id': uid,
            # 'department': department_sales_team,
            # 'enquiry_id': enquiry_id,
            ##
            'tag_ids':[(6, 0, request.env['helpdesk.tag'].search([('name', '=', 'Call')], limit=1).ids)],
            'email': partner.email,
            'description': post['cl'],
        }
        helpdesk_id = helpdesk_obj.create(helpdesk_data)
        helpdesk = helpdesk_obj.browse(helpdesk_id)
        # if partner_id:
        #     helpdesk.update_customer_info(partner_id)

        params['helpdesk_id'] = helpdesk_id.id

        # request.env['crm.phonecall'].create({
        #     'helpdesk_id': helpdesk_id,
        #     'partner_id': partner_id,
        #     'name': categ_name
        # })

        menu_id = request.env['ir.model.data'].get_object_reference('helpdesk', 'helpdesk_ticket_menu_main')
        if menu_id:
            params['menu_id'] = menu_id[1]
            menu_obj = request.env['ir.ui.menu']
            menu = menu_obj.browse([menu_id[1]])
            params['action_id'] = menu.action.id
            redirect_url = redirect_url % params
        return werkzeug.utils.redirect(redirect_url)
