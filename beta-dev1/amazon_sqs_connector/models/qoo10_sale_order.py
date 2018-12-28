from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class Qoo10_Sale_order_SQS(models.TransientModel):
    """ Recieves Data and Creates Sale Orders """

    _inherit = 'sqs.sale.order'

    @api.model
    def create_qoo10_sale_order(self, result):
        """ Create Sales Order With the Data Received From SQS """

        print('. . . . . Processsing Recieved Messages.')

        vals = {}
        s_vals = {}
        b_vals = {}
        sale_order_id = self.env['sale.order']
        order_id = result['data']['Order']['orderNo']
        dup_id = sale_order_id.search([('mums_order_id', '=', order_id)])
        if dup_id:
            print(dup_id.mums_order_id)
            return False
        else:
            vals['sales_channel'] = result['data']['sales_channel']
            vals['mums_order_id'] = result['data']['Order']['orderNo']

            s_vals['name'] = result['data']['Order']['receiver']
            s_vals['phone'] = result['data']['Order']['receiverMobile']
            s_vals['street'] = result['data']['Order']['shippingAddr']
            country = result['data']['Order']['shippingCountry']
            s_vals['country_id'] = self.env['res.country'].search(
                [('code', '=', country)], limit=1).id
            s_vals['zip'] = result['data']['Order']['zipCode']

            b_vals['name'] = result['data']['Order']['senderName']
            s_vals['phone'] = result['data']['Order']['senderTel']
            b_vals['street'] = result['data']['Order']['senderAddr']
            b_vals['zip'] = result['data']['Order']['senderZipCode']
            country = result['data']['Order']['senderNation']
            b_vals['country_id'] = self.env['res.country'].search(
                [('name', '=', country)], limit=1).id

            vals['shipping_id'] = self.env[
                'shipping.address'].create(s_vals).id
            vals['billing_id'] = self.env['billing.address'].create(s_vals).id

            vals['partner_id'] = self.cu_qoo10_partner(result)
            vals['cus_email'] = result['data']['Order']['buyerEmail']
            vals['cus_phone'] = result['data']['Order']['buyerTel']
            vals['shipping_charges'] = result['data']['Order']['ShippingRate']
            vals['date_order'] = result['data']['Order']['orderDate']
            vals['payment_method'] = result['data']['Order']['PaymentMethod']
            vals['order_line'] = self.cu_qoo10_product(result)
            vals['amount_total'] = result['data']['Order']['total']
            vals['amount_untaxed'] = result['data']['Order']['orderPrice']
            vals['discount_amount'] = result['data']['Order']['discount']
            _logger.info('before creating sale order %s', vals)
            sale_id = self.env['sale.order'].create(vals)
            for order_line in sale_id.order_line:
                _logger.info('after creating sale order %s sqs_product_id %s', sale_id.id,order_line.sqs_product_id)
            print('. . . . . Sale Order Created.')
            return sale_id

    def cu_qoo10_partner(self, result):
        """ Retrive, Create and Update Partner from received messages """

        vals = {}
        email = result['data']['Order']['buyerEmail']
        if email:
            if self.env['res.partner'].search([('email', '=', email)]):
                customer_id = self.env['res.partner'].search(
                    [('email', '=', email)], limit=1).id
                vals['partner_id'] = customer_id
                print('. . . . . Customer Updated.')
            else:
                res_partner_obj = self.env['res.partner']
                customer_data = {
                    'name': result['data']['Order']['buyer'],
                    'email': result['data']['Order']['buyerEmail'],
                    'phone': result['data']['Order']['buyerTel'],
                    'mobile': result['data']['Order']['buyerMobile'],
                    'street': result['data']['Order']['Addr1'],
                    'street2': result['data']['Order']['Addr2'],
                }
                vals['partner_id'] = res_partner_obj.create(customer_data).id
                print('. . . . . Customer Created.')

            return vals['partner_id']

    def cu_qoo10_product(self, result):
        """ Retrive, Create and Update Vendor from received messages """
        order_lines = []
        order_line = result['data']['Order']
        # for order_line in product_list:
        if order_line:
            name = order_line['itemTitle']
            name = name.encode('utf8').strip()
            name = str(name).replace("\\", '')
            name = name.replace('&amp;', '&')
            name = name.replace('&nbsp;', ' ')

            default_code = order_line['itemCode']
            default_code = default_code.encode('utf8').strip()
            default_code = str(default_code).replace("\\", '')
            default_code = default_code.replace('&amp;', '&')
            default_code = default_code.replace('&nbsp;', ' ')
            option = float(order_line['option'].split('S$')[0][-1] + order_line['option'].split('$')[1].split(')')[0])
            product_seller_id = self.env['res.partner'].search(
                [('name', '=', 'Mums Stock')], limit=1).id

            product_obj = self.env['product.product']

            if product_obj.search([('name', '=', name)]):
                product = product_obj.search([('name', '=', name)], limit=1)

                product_data = {
                    'name': name,
                    'type': 'product',
                    'product_id': order_line['sellerItemCode'],
                    'list_price': order_line['orderPrice'],
                    'default_code': default_code,
                }

                product_obj.browse([(product.id)]).write(product_data)
                order_lines.append([0, 0, {'product_id': product.id, 
                                            'sqs_product_id':order_line['sellerItemCode'],
                                            'warehouse_id': 1, 
                                            'product_uom_qty' : order_line['orderQty'],
                                            'suppliers': product_seller_id, 
                                            'option_value': option}])

                print('. . . . . Products Updated and Linked to Sale Order Lines.')

            else:
                product_data = {
                    'name': name,
                    'type': 'product',
                    'product_id': order_line['sellerItemCode'],
                    'list_price': order_line['orderPrice'],
                    'default_code': default_code,
                }

                product = product_obj.create(product_data)
                order_lines.append([0, 0, {'product_id': product.id, 
                                            'sqs_product_id':order_line['sellerItemCode'],
                                            'warehouse_id': 1, 
                                            'product_uom_qty' : order_line['orderQty'],
                                            'suppliers': product_seller_id, 
                                            'option_value': option}])

                print('. . . . . Products Created and Linked to Sale Order Lines.')

        return order_lines
