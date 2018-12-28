from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo import models, fields, api


class honosblog(http.Controller):
     
    @http.route(['/blog_data'],type='json', auth='public', website=True , csrf=False, cache=30)
    def category_data(self,template):
        data=request.env['blog.post'].search([('website_published','=',True)],limit=3)
        values = {'object':data}
        print values
        return request.env.ref(template).render(values)

    
    
    
       

    
     
    
    
    
    
    
    
    
    
    
    
