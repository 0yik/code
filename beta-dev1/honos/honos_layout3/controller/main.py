import odoo
from odoo import http
from odoo.http import request

class honosHomePage2(http.Controller):    
    @http.route(['/home/2'], type='http', auth="public", website=True)    
    def service(self, **kwargs):        
        return request.render("honos_layout3.honos_layout3_homepage")
