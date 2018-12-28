import time
from zipfile import ZipFile
from tempfile import SpooledTemporaryFile
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductImage(models.TransientModel):
    _name = "product.image"
    _description = "Upload Image Product"

    
    images = fields.Binary('Choose Zip File')
   
    

    @api.multi
    def upload_product(self):
    	
    	decoded_base64 = base64.b64decode(self.images)
    	res = []
 
    	with SpooledTemporaryFile() as tmp:
    		tmp.write(decoded_base64)
    		archive = ZipFile(tmp, 'r')
    		for file in archive.filelist:
    			content = archive.read(file.filename)
    			if content:
    				product_name = file.filename.split("/",1)[1]
    				name = product_name.split(".",1)[0]
    				product_obj = self.env['product.template']
	    			product_rec = product_obj.search([('name','=',name)])   				
		    		if len(product_rec) != 0:
		    			encoded = base64.b64encode(content)
		    			product_rec.write({"image_medium":encoded})
		    		else:
		    			res.append(name)		
		if len(res) != 0:

			product_not_found = ','.join(res)
			return {
	        'name': 'Message',
	            'type': 'ir.actions.act_window',
	            'view_type': 'form',
	            'view_mode': 'form',
	            'res_model': 'custom.pop.message',
	            'target':'new',
	            'context':{'default_name':"Please correct following image with product name  %s  is not avalible." %(product_not_found)} 
	            }	        
		else:

			return {
	        'name': 'Message',
	            'type': 'ir.actions.act_window',
	            'view_type': 'form',
	            'view_mode': 'form',
	            'res_model': 'custom.pop.message',
	            'target':'new',
	            'context':{'default_name':"All  Product image updated "} 
	            }	
			
		
class CustomPopMessage(models.TransientModel):
	_name = "custom.pop.message"

	name = fields.Char('Message')


