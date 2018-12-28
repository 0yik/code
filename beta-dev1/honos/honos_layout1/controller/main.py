import odoo
from odoo import http
from odoo.http import request

class honosHomePage1(http.Controller):    
    @http.route(['/home/1'], type='http', auth="public", website=True)    
    def service(self, **kwargs):        
        return request.render("honos_layout1.honos_layout1_homepage")
