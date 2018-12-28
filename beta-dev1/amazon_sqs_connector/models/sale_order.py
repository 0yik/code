# -*- coding: utf-8 -*-

import base64
import urllib2

import boto3
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class Custom_Sale_Order(models.Model):
    _inherit = 'sale.order'

    sales_channel = fields.Char('Sales Channel', readonly=False)
    store_url = fields.Char('Store url', readonly=False)
    shipping_id = fields.Many2one(
        "shipping.address", string='Shipping Address', readonly=True, copy=False)
    billing_id = fields.Many2one(
        "billing.address", string='Billing Address', readonly=True, copy=False)
    mums_order_id = fields.Char('Order ID')
    cus_email = fields.Char('Email')
    cus_phone = fields.Char('Phone')
    shipping_charges = fields.Monetary('Shipping Charges')
    discount_amount = fields.Monetary('Coupon Discount')
    extra_delivery = fields.Monetary('Extra Delivery')
    payment_method = fields.Char('Payment Method', help="Payment Method")
    option_value = fields.Monetary(string='OptionValue', compute="_amount_all")

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """ Compute the total amounts of the SO. """

        for order in self:
            amount_untaxed = amount_tax = option_value = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                if self.sales_channel == 'qoo10':
                    option_value += line.option_value
                else:
                    option_value = 0.0
                print option_value
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * \
                        (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(
                        price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0)
                                      for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
                # # val = self.discount_amount
                # if val < 0:
                #     val = abs(val)
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'option_value': order.pricelist_id.currency_id.round(option_value),
                # 'amount_total': (amount_untaxed + amount_tax + self.shipping_charges + option_value) - val,
            })

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        invoice_vals = super(Custom_Sale_Order, self)._prepare_invoice()
        team_id = self.env['crm.team'].search(
            [('name', 'ilike', 'Website Sales')]).id
        if team_id:
            invoice_vals.update({'team_id': team_id})
        invoice_vals.update({"sales_channel": self.sales_channel,
                             "store_url": self.store_url,
                             "shipping_id": self.shipping_id.id,
                             "billing_id": self.billing_id.id,
                             "mums_order_id": self.mums_order_id,
                             "cus_email": self.cus_email,
                             "cus_phone": self.cus_phone,
                             "shipping_charges": self.shipping_charges,
                             "discount_amount": self.discount_amount,
                             "extra_delivery": self.extra_delivery,
                             "payment_method": self.payment_method,
                             "so_id": self.id,
                             })
        return invoice_vals


class Custom_Sale_Order_Line(models.Model):
    _inherit = 'sale.order.line'
    option_value = fields.Monetary(string='OptionValue')
    suppliers = fields.Many2one('res.partner', 'Suppliers')
    source_id = fields.Many2one('stock.location', 'Source')
    warehouse_id = fields.Char(string='Warehouse Id', help='Warehouse Id')
    sqs_product_id = fields.Char(  # compute='_compute_sqs_product_id',
        string='Product Id', help='Product Id.')
    sqs_supplier_id = fields.Char(  # compute='_compute_sqs_supplier_id',
        string='Supplier Id', help='Supplier Id.')

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        vals = super(Custom_Sale_Order_Line,
                     self)._prepare_order_line_procurement(group_id)
        vals['supplier_id'] = self.suppliers.id
        vals['sqs_product_id'] = self.sqs_product_id
        vals['sqs_supplier_id'] = self.sqs_supplier_id
        return vals

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        invoice_line_vals = super(
            Custom_Sale_Order_Line, self)._prepare_invoice_line(qty=qty)
        invoice_line_vals.update({"suppliers": self.suppliers.id,
                                  "source_id": self.source_id.id,
                                  "warehouse_id": self.warehouse_id,
                                  "sqs_product_id": self.sqs_product_id,
                                  "sqs_supplier_id": self.sqs_supplier_id,
                                  })
        return invoice_line_vals


class Sale_order_SQS(models.Model):

    """ Recieves Data and Creates Sale Orders """

    _name = 'sqs.sale.order'
    _inherit = 'res.config.settings'

    queue_ref = fields.Many2one('amazon.sqs')

    def set_default_fields(self):

        ir_values = self.env['ir.values']
        ir_values.set_default('amazon.sqs', 'queue_ref',
                              self.queue_ref and self.queue_ref.id or False, False)
        return True

    def get_default_fields(self, vals):

        ir_values = self.env['ir.values']
        queue_ref = ir_values.get_default('amazon.sqs', 'queue_ref', False)
        return {'queue_ref': queue_ref}

    @api.model
    def get_queued_messages(self):
        """ Connect to Amazon SQS and Recieve Messages """
        ir_values = self.env['ir.values']
        queue_ref = ir_values.get_default('amazon.sqs', 'queue_ref', False)
        conn_obj = self.env['amazon.sqs'].search(
            [('id', '=', queue_ref)], limit=1)

        max_queue_messages = 10

        # sqs = boto3.resource('sqs')

        # To get sqs object without the aws configuration file
        if conn_obj.id:
            sqs = boto3.resource('sqs',
                                 region_name=conn_obj.default_region,
                                 aws_access_key_id=conn_obj.aws_access_key_id,
                                 aws_secret_access_key=conn_obj.aws_secret_access_key
                                 )
        else:
            raise Warning(
                _('Check your AWS Access Key ID, AWS Secret Access Key, Region Name and Queue name'))
        # Get the queue
        try:
            queue = sqs.get_queue_by_name(QueueName=conn_obj.queue_name)
        except Exception:
            raise Warning(
                _('Queue Name not Found! Please Check your Amazon SQS Connection.'))

        print('* * * . . . Getting Messages From Amazon SQS . . . * * *')

        for message in queue.receive_messages(MaxNumberOfMessages=max_queue_messages):
            # Get the values and replace required values

            if 'false' or 'true' or 'null' in message.body:
                result = message.body.replace('false', 'False')
                result = result.replace('true', 'True')
                result = result.replace('null', 'False')
                result = eval(result)
                _logger.info('sqs sale order %s', result)

            else:
                result = eval(message.body)
            if result['data']['sales_channel'] == 'lazada':

                sale_id = self.env[
                    'sqs.sale.order'].create_lazada_sale_order(result)
                if sale_id:
                    sale_id.action_confirm()
                    sale_id.action_invoice_create(grouped=False, final=False)
                    sale_id.invoice_ids.action_invoice_open()
                    sale_id.picking_ids.send_queued_messages()
                else:
                    print('Sale Order Already Exit')

            elif result['data']['sales_channel'] == 'qoo10':
                sale_id = self.env[
                    'sqs.sale.order'].create_qoo10_sale_order(result)
                if sale_id:
                    sale_id.action_confirm()
                    sale_id.action_invoice_create(grouped=False, final=False)
                    sale_id.invoice_ids.action_invoice_open()
                    sale_id.picking_ids.send_queued_messages()
                else:
                    print('Sale order Already Exist')

            elif result['data']['sales_channel'] == 'mumssg':
                sale_id = self.create_sale_order(result)
                if sale_id:
                    sale_id.action_confirm()
                    sale_id.action_invoice_create(grouped=False, final=False)
                    sale_id.invoice_ids.action_invoice_open()
                    sale_id.picking_ids.send_queued_messages()
                else:
                    print('Sale order Already Exist')

        print('* * * . . . All Messages Processed Successfully . . .* * *')

        return True

    @api.model
    def create_sale_order(self, result):
        """ Create Sales Order With the Data Received From SQS """

        print('. . . . . Processsing Recieved Messages.')
        vals = {}
        s_vals = {}
        sale_order_id = self.env['sale.order']
        order_id = result['data']['Order']['order_id']
        dup_id = sale_order_id.search([('mums_order_id', '=', order_id)])
        if dup_id:
            print(dup_id.mums_order_id)
            return False
        else:
            store_url = result['data']['Order']['store_url']
            store_url = store_url.encode('utf8').strip()
            store_url = str(store_url).replace("\\", '')
            vals['store_url'] = store_url
            vals['sales_channel'] = result['data']['sales_channel']
            vals['mums_order_id'] = result['data']['Order']['order_id']

            s_vals['name'] = result['data']['Order']['shipping_firstname'] + ' ' + str(
                result['data']['Order']['shipping_lastname'])
            s_vals['phone'] = result['data']['Order']['shipping_telephone']
            s_vals['street'] = result['data']['Order']['shipping_address_1']
            s_vals['street2'] = result['data']['Order']['shipping_address_2']
            s_vals['city'] = result['data']['Order']['shipping_city']
            s_vals['zip'] = result['data']['Order']['shipping_postcode']
            country = result['data']['Order']['shipping_country']
            s_vals['country_id'] = self.env['res.country'].search(
                [('name', '=', country)], limit=1).id
            s_vals['shipping_method'] = result[
                'data']['Order']['shipping_method']
            s_vals['shipping_code'] = result['data']['Order']['shipping_code']

            vals['shipping_id'] = self.env[
                'shipping.address'].create(s_vals).id

            vals['partner_id'] = self.cu_partner(result)
            vals['cus_email'] = result['data']['Order']['email']
            vals['cus_phone'] = result['data']['Order']['telephone']
            vals['date_order'] = result['data']['Order']['date_added']
            vals['order_line'] = self.cu_product(result)
            vals['payment_method'] = result['data']['Order']['payment_method']
            for data in result['data']['Order']['totals']:
                if data['code'] == 'coupon':
                    vals['discount_amount'] = data['value']
                elif data['code'] == 'shipping':
                    vals['shipping_charges'] = data['value']
                elif data['code'] == 'extra_delivery':
                    vals['extra_delivery'] = data['value']
            _logger.info('before creating sale order %s', vals)
            sale_id = self.env['sale.order'].create(vals)
            for order_line in sale_id.order_line:
                _logger.info('after creating sale order %s sqs_product_id %s',
                             sale_id.id, order_line.sqs_product_id)

            sale_id.picking_ids.send_queued_messages()
            print('. . . . . Sale Order Created.')
            return sale_id

    def _get_binary_image(self, image_data):
        """ Convert Image url to base64 Image Data """

        url = image_data.encode('utf8').strip()
        url = str(url).replace("\\", '')
        try:
            if url != '':
                request = urllib2.Request(url)
                binary = urllib2.urlopen(request)
            else:
                return
        except urllib2.HTTPError as err:
            if err.code == 404:
                # the image is just missing, we skip it
                return
            else:
                raise
        else:
            return binary.read()

    def cu_partner(self, result):
        """ Retrive, Create and Update Partner from received messages """

        vals = {}
        email = result['data']['Order']['email']
        if email:
            if self.env['res.partner'].search([('email', '=', email)]):
                customer_id = self.env['res.partner'].search(
                    [('email', '=', email)], limit=1).id

                # # Customer Update disabled
                # customer_data = {
                #     'name': result['data']['Order']['firstname'] + ' ' + result['data']['Order']['lastname'],
                #     'email': result['data']['Order']['email'],
                #     'phone': result['data']['Order']['telephone'],
                #     'fax': result['data']['Order']['fax'],
                # }
                # self.env['res.partner'].browse([(customer_id)]).write(customer_data)

                vals['partner_id'] = customer_id
                print('. . . . . Customer Updated.')
            else:
                res_partner_obj = self.env['res.partner']
                customer_data = {
                    'name': result['data']['Order']['firstname'] + ' ' + result['data']['Order']['lastname'],
                    'email': result['data']['Order']['email'],
                    'phone': result['data']['Order']['telephone'],
                    'fax': result['data']['Order']['fax'],
                }
                vals['partner_id'] = res_partner_obj.create(customer_data).id
                print('. . . . . Customer Created.')

            return vals['partner_id']

    def cu_supplier(self, supplier_list):
        """ Retrive, Create and Update Vendor from received messages """

        seller_ids = []
        res_partner_obj = self.env['res.partner']

        for suppliers in supplier_list:
            if suppliers['supplier']:

                email = suppliers['supplier']['email']
                if email:
                    check_mail = res_partner_obj.search(
                        [('email', '=', email)], limit=1).id

                    if check_mail:
                        supplier = res_partner_obj.search(
                            [('email', '=', email)])

                        # # Supplier Update disabled
                        # supplier_data = {'supplier': True,
                        #                  'customer': False,
                        #                  'name': suppliers['supplier']['name'],
                        #                  'email': suppliers['supplier']['email'],
                        #                  'website': suppliers['supplier']['website'],
                        #                  'street': suppliers['supplier']['address'],
                        #                  'active': suppliers['supplier']['active'],
                        #                  'comment': suppliers['supplier']['comments']}
                        #
                        # self.env['res.partner'].browse([(supplier.id)]).write(supplier_data)

                        seller_ids.append([0, 0, {'name': supplier.id,
                                                  'product_code': suppliers['supplier_code']}])

                        print('. . . . . Vendors Updated and Linked to Products.')

                    else:
                        res_partner_category_obj = self.env[
                            'res.partner.category']
                        tag_id = res_partner_category_obj.search(
                            [('name', '=', 'Supplier')], limit=1)
                        if tag_id:
                            tag_data = [(6, 0, [tag_id.ids])]
                        else:
                            tag_data = [(0, 0, {'name': 'Supplier'})]

                        supplier_data = {'supplier': True,
                                         'customer': False,
                                         'supplier_id': suppliers['supplier']['supplier_id'],
                                         'name': suppliers['supplier']['name'],
                                         'email': suppliers['supplier']['email'],
                                         'website': suppliers['supplier']['website'],
                                         'street': suppliers['supplier']['address'],
                                         'active': suppliers['supplier']['active'],
                                         'comment': suppliers['supplier']['comments'],
                                         'category_id': tag_data}

                        supplier = res_partner_obj.create(supplier_data)

                        seller_ids.append([0, 0, {'name': supplier.id,
                                                  'product_code': suppliers['supplier_code']}])

                    print('. . . . . Vendors Created and Linked to Products.')

        return seller_ids

    def cu_categories(self, category_list):
        """ Retrive, Create and Update Categories from received messages """

        category_obj = self.env['product.category']
        product_data = {}
        for category in category_list:
            categ_name = category['name']
            if category_obj.search([('name', '=', categ_name)]):
                categ_id = category_obj.search(
                    [('name', '=', categ_name)], limit=1)
                product_data['categ_id'] = categ_id.id

                # # Category Update disabled
                # if category.has_key('parent'):
                #     parent_name = category['parent']['name']
                #     if category_obj.search([('name', '=', parent_name)]):
                #         parent_id = category_obj.search([('name', '=', parent_name)], limit=1)
                #         data = category_obj.browse([(categ_id.id)])
                #         data.write({'parent_id': parent_id.id})
                #     else:
                #         parent_data = {'name': category['parent']['name']}
                #         parent_id = category_obj.create(parent_data)
                #         data = category_obj.browse([('id', '==', categ_id)])
                #         data.write({'parent_id': parent_id})

            else:
                if category.has_key('parent'):
                    categ_data = {'name': category['name']}
                    parent_name = category['parent']['name']
                    if category_obj.search([('name', '=', parent_name)]):
                        categ_data['parent_id'] = category_obj.search(
                            [('name', '=', parent_name)], limit=1)
                    else:
                        parent_data = {'name': category['parent']['name']}
                        parent_id = category_obj.create(parent_data)
                        categ_data['parent_id'] = parent_id.id
                        categ_id = category_obj.create(categ_data)
                        product_data['categ_id'] = categ_id.id

        print('. . . . . Categories Created/Updated and Linked to Products.')
        if 'categ_id' in product_data.keys():
            return product_data['categ_id']

    def cu_stock_location(self, result):
        """ Retrive, Create and Update Stock Location from received messages """

        stock_location_obj = self.env['stock.location']
        stock_warehouse_obj = self.env['stock.warehouse']

        if result['product'].has_key('sale_type'):
            if result['product']['sale_type'] == 'mumssg':
                # if stock_warehouse_obj.search([('name', '=', 'MUMSWH')]):
                #     warehouse_id = stock_warehouse_obj.search([('name', '=', 'MUMSWH')], limit=1).id
                # else:
                #     warehouse_id = stock_warehouse_obj.search([('name', '=', 'My Company')], limit=1).id
                #     warehouse_data = {'name': 'MUMSWH', }
                #     stock_location_obj.browse([(warehouse_id)]).write(warehouse_data)
                print('. . . . . Location Updated and Added to Products.')
                return 1

            elif result['product']['sale_type'] == 'marketplace':

                for supplier in result['product']['supplier_product']:
                    name = supplier['supplier']['name']

                # stock_warehouse_id = stock_warehouse_obj.search([('name', '=', name)])
                if name:
                    check_mail = stock_warehouse_obj.search(
                        [('name', '=', name)], limit=1).id

                    if check_mail:
                        warehouse_id = stock_warehouse_obj.search(
                            [('name', '=', name)], limit=1).id

                        print('. . . . . Location Updated and Added to Products.')
                        return warehouse_id
                    else:
                        seq = self.env['ir.sequence'].next_by_code(
                            'stock.warehouse')
                        stock_warehouse_data = {'name': name,
                                                'code': seq
                                                }

                        warehouse_id = stock_warehouse_obj.create(
                            stock_warehouse_data)
                        virtual_locations = stock_location_obj.search(
                            [('name', '=', 'Virtual Locations')], limit=1)

                        stock_location_data = {'name': seq + '/' + name,
                                               'location_id': virtual_locations.id,
                                               'usage': 'supplier',
                                               }
                        stock_location_obj.write(stock_location_data)
                        stock_location_obj.browse(
                            [(warehouse_id.lot_stock_id.id)]).write(stock_location_data)

                        print('. . . . . Location Created and Added to Order Line.')
                        return warehouse_id.id
        return False

    def cu_product(self, result):
        """ Retrive, Create and Update Vendor from received messages """

        order_lines = []
        product_list = result['data']['Order']['products']
        for order_line in product_list:

            if order_line['product']:
                name = order_line['product']['name']
                name = name.replace('&amp;', '&')
                name = name.replace('&nbsp;', ' ')

                product_obj = self.env['product.product']
                if product_obj.search([('name', '=', name)]):
                    product = product_obj.search(
                        [('name', '=', name)], limit=1)
                    data = self.get_product_data(order_line)
                    product_obj.browse([(product.id)]).write(
                        data['product_data'])
                    # special_discount = ((product.list_price - product.special_discount)/product.list_price)*100
                    order_lines.append([0, 0, {'product_id': product.id,
                                               'sqs_product_id': order_line['product']['product_id'],
                                               'suppliers': data['product_seller_ids'],
                                               'sqs_supplier_id':order_line['product']['supplier_id'],
                                               'price_unit': order_line['price'],
                                               'product_uom_qty': order_line['quantity'],
                                               'warehouse_id': data['source_id'], }])
                    # 'discount': special_discount

                    print('. . . . . Products Updated and Linked to Sale Order Lines.')

                else:
                    data = self.get_product_data(order_line)
                    product = product_obj.create(data['product_data'])
                    # special_discount = ((product.list_price - product.special_discount)/product.list_price)*100
                    order_lines.append([0, 0, {'product_id': product.id,
                                               'sqs_product_id': order_line['product']['product_id'],
                                               'suppliers': data['product_seller_ids'],
                                               'sqs_supplier_id':order_line['product']['supplier_id'],
                                               'price_unit': order_line['price'],
                                               'product_uom_qty': order_line['quantity'],
                                               'warehouse_id': data['source_id'], }])
                    # 'discount': special_discount

                    print('. . . . . Products Created and Linked to Sale Order Lines.')

        return order_lines

        # def update_stock(self, vals):
        #     """Update Product Quantity Received From SQS"""
        #     values = []
        #     values['lot_id'] = False
        #     values['product_id'] = vals['product']
        #     values['new_quantity'] = vals['qty_available']
        #     update_stock_id = self.pool.get('stock.change.product.qty').create(values)
        #     stock_obj = self.env['stock.change.product.qty'].browse(update_stock_id)
        #     stock_obj.change_product_qty()
        #     return True

    def get_product_data(self, order_line):
        name = order_line['product']['name']
        name = name.replace('&amp;', '&')
        name = name.replace('&nbsp;', ' ')

        default_code = order_line['product']['sku']
        default_code = default_code.replace('&amp;', '&')
        default_code = default_code.replace('&nbsp;', ' ')

        description = order_line['product']['productDescription']
        description = description.replace('&amp;', '&')
        description = description.replace('&nbsp;', ' ')

        image_url = order_line['product']['image']
        image = self._get_binary_image(image_url)
        product_data = {
            'type': 'product',
            'name': name,
            'has_expiry': order_line['product']['has_expiry'],
            'gift_wrap': order_line['product']['gift_wrap'],
            'is_liquid': order_line['product']['is_liquid'],
            'isbn': order_line['product']['isbn'],
            'special_discount': order_line['product']['special_discount'],
            'global_discount': order_line['product']['global_discount'],
            'height': order_line['product']['height'],
            'viewed': order_line['product']['viewed'],
            'jan': order_line['product']['jan'],
            'width': order_line['product']['width'],
            'is_upc_checked': order_line['product']['is_upc_checked'],
            'mpn': order_line['product']['mpn'],
            'offerPriceFormatted': order_line['product']['offerPriceFormatted'],
            'model': order_line['product']['model'],
            'upc': order_line['product']['upc'],
            'length': order_line['product']['length'],
            'minimum': order_line['product']['minimum'],
            'level': order_line['product']['level'],
            'standard_price': order_line['product']['cost'],
            'list_price': order_line['product']['price'],
            'default_code': default_code,
            'has_option': order_line['product']['has_option'],
            'weight': order_line['product']['weight'],
            'qty_available': order_line['product']['stock'],
            'description': description,
            'product_id': order_line['product']['product_id'],
            'image': base64.b64encode(image),
        }

        supplier_list = order_line['product']['supplier_product']

        product_data['seller_ids'] = self.cu_supplier(
            supplier_list)

        if len(product_data['seller_ids']) > 0:
            product_seller_ids = product_data[
                'seller_ids'][0][2]['name']
        else:
            product_seller_ids = None

        category_list = order_line['product']['categoryTree']
        if category_list:
            product_data['categ_id'] = self.cu_categories(
                category_list)

        source = self.cu_stock_location(order_line)
        if source:
            source_id = source
        else:
            source_id_data = self.env['stock.warehouse'].search(
                [('name', '=', 'MUMSWH')]).id
            if source_id_data:
                source_id = source_id_data
            else:
                source_id = 1
        return {'product_data': product_data, 'source_id': source_id, 'product_seller_ids': product_seller_ids}

Sale_order_SQS()
