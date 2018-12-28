from odoo import http
from odoo.http import request

class MyProfile(http.Controller):

    @http.route(['/my_profile'], type='http', auth="user", website=True)
    def my_profile(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference('hilti_reusable_user_respartner_changepassword', 'menu_my_partner_profile_customer')[1]
        action_id = request.env['ir.model.data'].get_object_reference('hilti_reusable_user_respartner_changepassword', 'action_client_base_menu')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))

    @http.route(['/my_profile_tester'], type='http', auth="user", website=True)
    def my_profile_tester(self, **post):
        menu_id = request.env['ir.model.data'].get_object_reference('hilti_reusable_user_respartner_changepassword', 'menu_my_tester_profile')[1]
        action_id = request.env['ir.model.data'].get_object_reference('hilti_reusable_user_respartner_changepassword', 'action_client_tester_base_menu')[1]
        return  request.redirect("/web#min=1&limit=80&view_type=list&model=project.booking&menu_id=" + str(menu_id) + "&action=" + str(action_id))

