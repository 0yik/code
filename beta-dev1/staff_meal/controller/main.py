from odoo import http
from odoo.http import request
from odoo import tools
import werkzeug.utils
from odoo import api, http, SUPERUSER_ID, _


class posConfirm(http.Controller):
    
    @http.route(['/confirm-pos-order/<int:id>'], type='http', auth="user", website=True)
    def changestate(self,id=None ,**kwargs):
        if id:
            root = request.env.user
            if root.env['pos.order'].browse(id).state == 'draft':
                root.env['pos.order'].browse(id).state = 'open'
            return werkzeug.utils.redirect('/web#id={0}&view_type=form&model=pos.order&action=312'.format(id))
