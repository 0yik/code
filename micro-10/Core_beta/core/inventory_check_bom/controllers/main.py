from odoo import http, SUPERUSER_ID
from odoo.http import route, request

class product_details(http.Controller):
    @http.route('/get_product_details', type='json', auth='public')
    def products_details(self,product_id):
        product_id = request.env['product.template'].browse(product_id)
        return product_id.virtual_available,product_id.uom_id.name

