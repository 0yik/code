from odoo import api, fields, models
from odoo.tools.translate import html_translate

 
class product_category(models.Model):
    
    _inherit = ["product.public.category"]
     
    content = fields.Html('Category Content', translate=html_translate)