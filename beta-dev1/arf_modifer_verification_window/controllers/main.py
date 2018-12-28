from odoo.addons.mail.controllers.main import MailController
from odoo import http
import werkzeug.utils
from werkzeug.exceptions import BadRequest
from odoo.http import request

class website_nric(http.Controller):

    @http.route('/nric', type="http", auth="user")
    def render_helpdesk(self, **post):
        cid     = post['cid'] or False
        nric    = post['uid'] or False
        type    = post['type'] or False
        
        print "CCCCCCC------>>", cid, nric, type, post
        
        redirect_url = '/web#id=%(verification_id)d&view_type=form&model=verification.window&menu_id=%(menu_id)d&action=%(action_id)d'
        
        existing_customer = request.env['res.partner'].search([('nric_passport_ros','=',nric)])
        params = {}
        if existing_customer:
            vals = {'partner_id': existing_customer.id,
                    'name'      : existing_customer.name,
                    'date_birth': existing_customer.date_birth,
                    'phone'     : existing_customer.contract_mobile,
                    'email'     : existing_customer.email,
                    
                    'nric'          : existing_customer.nric_passport_ros,
                    'passport'      : existing_customer.nric_passport_ros,
                    'policy_number' : 'XXX',
                    'vehicle_number': 'XXX',
                }
            verification = request.env['verification.window'].create(vals)
            verification_id = verification.id
            params['verification_id'] = verification_id   
            ir_model_obj = request.env['ir.model.data']
            action_id = ir_model_obj.get_object_reference('arf_modifer_verification_window', 'action_verification_window')[1]
            params['action_id'] = action_id
            
            menu_id = request.env['ir.ui.menu'].browse([action_id]).id
            params['menu_id'] = menu_id
            print "params----->>", params
            
            redirect_url = redirect_url%params
            return werkzeug.utils.redirect(redirect_url)
    
        #context = dict(self.env.context or {})
        #context['active_id'] = self.id
#         return {
#             'name': ('Verification Windows'),
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'verification.window',
#             'view_id': 427,#self.env.ref('arf_modifer_verification_window.view_verification_window_wizard').id,
#             'type': 'ir.actions.act_window',
#             #'res_id': self.env.context.get('cashbox_id'),
#             #'context': context,
#             'target': 'new'
#         }
        
#     @api.multi
#     def open(self):
#         context = dict(self.env.context or {})
#         context['active_id'] = self.id
#         return {
#             'name': _('Verification Windows'),
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'verification.window',
#             'view_id': self.env.ref('arf_modifer_verification_window.view_verification_window_wizard').id,
#             'type': 'ir.actions.act_window',
#             #'res_id': self.env.context.get('cashbox_id'),
#             'context': context,
#             'target': 'new'
#         }