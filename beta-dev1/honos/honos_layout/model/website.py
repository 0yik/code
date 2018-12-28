from odoo import api, fields, models
 
class website(models.Model):
     
    _inherit = "website"
    
    honos_header_style_one = fields.Char('honos Heading')
    honos_header_style_two = fields.Char("honos header style2")
    honos_header_style_three = fields.Char("honos header style3")
     
    def category_check(self,filter=[]):
         
        if filter:
            filter.extend([('website_published','=',True)])
        else:
            filter=([('website_published','=',True)])
         
        return self.env['product.public.category'].sudo().search(filter)
       
