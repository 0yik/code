from openerp import models, api
import logging
_logger = logging.getLogger(__name__)

class Lazada_Sale_order_SQS(models.TransientModel):
    """ Recieves Data and Creates Sale Orders """

    _inherit = 'sqs.sale.order'

    @api.model
    def create_lazada_sale_order(self, result):
        """ Create Sales Order With the Data Received From SQS """

        print('. . . . . Processsing Recieved Messages.')
        vals = {}
        s_vals = {}
        b_vals = {}
        sale_order_id = self.env['sale.order']
        order_id = result['data']['Order']['OrderNumber']
        dup_id = sale_order_id.search([('mums_order_id', '=', order_id)])
        if dup_id:
            print(dup_id.mums_order_id)
            return False
        else:
            vals['sales_channel'] = result['data']['sales_channel']
            vals['mums_order_id'] = result['data']['Order']['OrderNumber']
            lastname = ''
            if result['data']['Order']['AddressShipping']['LastName']:
                lastname = result['data']['Order'][
                    'AddressShipping']['LastName']
            s_vals['name'] = result['data']['Order'][
                'AddressShipping']['FirstName'] + ' ' + lastname
            # s_vals['phone'] = result['data'][
            #     'Order']['AddressShipping']['Phone']
            s_vals['street'] = result['data'][
                'Order']['AddressShipping']['Address1']
            # s_vals['street2'] = result['data'][
            #     'Order']['AddressShipping']['Address4']
            # s_vals['city'] = result['data']['Order']['AddressShipping']['City']
            s_vals['zip'] = result['data']['Order'][
                'AddressShipping']['PostCode']
            country = result['data']['Order']['AddressShipping']['Country']
            s_vals['country_id'] = self.env['res.country'].search(
                [('name', '=', country)], limit=1).id

            b_vals['name'] = result['data']['Order']['AddressBilling']['FirstName'] + ' ' + str(
                result['data']['Order']['AddressBilling']['LastName'])
            b_vals['phone'] = result['data'][
                'Order']['AddressBilling']['Phone']
            b_vals['street'] = result['data'][
                'Order']['AddressBilling']['Address1']
            b_vals['street2'] = result['data'][
                'Order']['AddressBilling']['Address4']
            b_vals['city'] = result['data']['Order']['AddressBilling']['City']
            b_vals['zip'] = result['data']['Order'][
                'AddressBilling']['PostCode']
            country = result['data']['Order']['AddressBilling']['Country']
            b_vals['country_id'] = self.env['res.country'].search(
                [('name', '=', country)], limit=1).id

            vals['shipping_id'] = self.env[
                'shipping.address'].create(s_vals).id
            vals['billing_id'] = self.env['billing.address'].create(s_vals).id
            vals['shipping_charges'] = result['data'][
                'Order']['OrderItems'][0]['ShippingAmount']
            vals['date_order'] = result['data']['Order']['CreatedAt']
            vals['payment_method'] = result['data']['Order']['PaymentMethod']
            vals['partner_id'] = self.cu_lazada_partner(result)
            vals['order_line'] = self.cu_lazada_product(result)
            _logger.info('before creating sale order %s', vals)
            sale_id = self.env['sale.order'].create(vals)
            for order_line in sale_id.order_line:
                _logger.info('after creating sale order %s sqs_product_id %s', sale_id.id,order_line.sqs_product_id)
            print('. . . . . Sale Order Created.')
            return sale_id




    def cu_lazada_partner(self, result):
        """ Retrive, Create and Update Partner from received messages """

        vals = {}
        lastname = ''
        if result['data']['Order']['CustomerLastName']:
            lastname = result['data']['Order']['CustomerLastName']
        name = result['data']['Order']['CustomerFirstName'] + ' ' + lastname
        if name:
            if self.env['res.partner'].search([('name', '=', name)]):
                customer_id = self.env['res.partner'].search(
                    [('name', '=', name)], limit=1).id
                vals['partner_id'] = customer_id
                print('. . . . . Customer Updated.')
            else:
                res_partner_obj = self.env['res.partner']
                customer_data = {
                    'name': result['data']['Order']['CustomerFirstName'] + ' ' + lastname
                }
                vals['partner_id'] = res_partner_obj.create(customer_data).id
                print('. . . . . Customer Created.')

            return vals['partner_id']

    def cu_lazada_product(self, result):
        """ Retrive, Create and Update Vendor from received messages """
        order_lines = []
        product_list = result['data']['Order']['OrderItems']
        product_seller_id = self.env['res.partner'].search(
            [('name', '=', 'Mums Stock')], limit=1).id
        for order_line in product_list:

            if order_line:
                name = order_line['Name']
                name = name.replace('&amp;', '&')
                name = name.replace('&nbsp;', ' ')

                default_code = order_line['Sku']
                default_code = default_code.replace('&amp;', '&')
                default_code = default_code.replace('&nbsp;', ' ')

                product_obj = self.env['product.product']
                if product_obj.search([('name', '=', name)]):
                    product = product_obj.search(
                        [('name', '=', name)], limit=1)
                    # image_url = order_line['productMainImage']
                    # image = self._get_binary_image(image_url)
                    product_data = {
                        'name': name,
                        'type': 'product',
                        'list_price': order_line['ItemPrice'],
                        'default_code': default_code,
                        'product_id': order_line['OrderItemId'],
                        # 'image': base64.b64encode(image),
                    }

                    product_obj.browse([(product.id)]).write(product_data)
                    order_lines.append([0, 0, {'product_id': product.id,
                                               'warehouse_id': 1,
                                               'sqs_product_id': order_line['OrderItemId'],
                                               'suppliers': product_seller_id}])
                    print('. . . . . Products Updated and Linked to Sale Order Lines.')

                else:
                    # image_url = order_line['productMainImage']
                    # image = self._get_binary_image(image_url)
                    product_data = {
                        'name': name,
                        'type': 'product',
                        'list_price': order_line['ItemPrice'],
                        'default_code': default_code,
                        'product_id': order_line['OrderItemId'],
                        # 'image': base64.b64encode(image),
                    }
                    product = product_obj.create(product_data)
                    order_lines.append([0, 0, {'product_id': product.id, 
                                                'warehouse_id': 1,
                                                'sqs_product_id': order_line['OrderItemId'], 
                                                'suppliers': product_seller_id}])

                    print('. . . . . Products Created and Linked to Sale Order Lines.')

        return order_lines
