import boto3
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _prepare_pack_ops(self, quants, forced_qties):
        pickings = super(StockPicking, self)._prepare_pack_ops(
            quants, forced_qties)
        final_picking = []
        for picking in pickings:
            sale_order = self.env['sale.order'].search(
                [('name', '=', self.origin)])
            sale_order_lines = self.env['sale.order.line'].search(
                [('order_id', '=', sale_order.id), ('product_id', '=', picking['product_id'])])
            for sale_order_line in sale_order_lines:
                if sale_order_line.suppliers:
                    picking['from_supplier'] = sale_order_line.suppliers[0].name
                    picking['sqs_product_id'] = sale_order_line.sqs_product_id
                    picking['sqs_supplier_id'] = sale_order_line.sqs_supplier_id
            final_picking.append(picking)
        return final_picking

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        self.send_queued_messages()
        return res

    @api.model
    def send_queued_messages(self):
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
            queue = sqs.get_queue_by_name(QueueName=conn_obj.delivery_queue)
        except Exception:
            raise Warning(
                _('Queue Name not Found! Please Check your Amazon SQS Connection.'))

        print('* * * . . . Sending Messages To Amazon SQS . . . * * *')

        max_queue_messages = 10

        if self:
            for picking_id in self:
                operations = []
                initial = []
                for operation_line in picking_id.pack_operation_product_ids:
                    operations.append(
                        {'product': {
                            'product_id': operation_line.product_id.product_id,
                            'product_name': operation_line.product_id.name,
                            'model': operation_line.product_id.model,
                            'upc': operation_line.product_id.upc,
                            'jan': operation_line.product_id.jan,
                            'isbn': operation_line.product_id.isbn,
                            'mpn': operation_line.product_id.mpn,
                            'brand_name': operation_line.product_id.brand_name,
                            'special_discount': operation_line.product_id.special_discount,
                            'has_expiry': operation_line.product_id.has_expiry,
                            'is_liquid': operation_line.product_id.is_liquid,
                            'is_upc_checked': operation_line.product_id.is_upc_checked,
                            'gift_wrap': operation_line.product_id.gift_wrap,
                            'isbn': operation_line.product_id.isbn,
                            'height': operation_line.product_id.height,
                            'viewed': operation_line.product_id.viewed,
                            'width': operation_line.product_id.width,
                            'offerPriceFormatted': operation_line.product_id.offerPriceFormatted,
                            'length': operation_line.product_id.length,
                            'minimum': operation_line.product_id.minimum,
                            'level': operation_line.product_id.level,
                            'has_option': operation_line.product_id.has_option,
                        },
                            'product_qty': operation_line.product_qty,
                            'product_state': operation_line.state,
                            'from_supplier': operation_line.from_supplier,
                            'sqs_product_id': operation_line.sqs_product_id,
                            'sqs_supplier_id': operation_line.sqs_supplier_id,
                            'qty_done': operation_line.qty_done,
                        })

                for initial_demand in picking_id.move_lines:

                    initial.append({
                        'product': {
                            'product_id': initial_demand.product_id.product_id,
                            'product_name': initial_demand.product_id.name,
                            'model': initial_demand.product_id.model,
                            'upc': initial_demand.product_id.upc,
                            'jan': initial_demand.product_id.jan,
                            'isbn': initial_demand.product_id.isbn,
                            'mpn': initial_demand.product_id.mpn,
                            'brand_name': initial_demand.product_id.brand_name,
                            'special_discount': initial_demand.product_id.special_discount,
                            'has_expiry': initial_demand.product_id.has_expiry,
                            'is_liquid': initial_demand.product_id.is_liquid,
                            'is_upc_checked': initial_demand.product_id.is_upc_checked,
                            'gift_wrap': initial_demand.product_id.gift_wrap,
                            'isbn': initial_demand.product_id.isbn,
                            'height': initial_demand.product_id.height,
                            'viewed': initial_demand.product_id.viewed,
                            'width': initial_demand.product_id.width,
                            'offerPriceFormatted': initial_demand.product_id.offerPriceFormatted,
                            'length': initial_demand.product_id.length,
                            'minimum': initial_demand.product_id.minimum,
                            'level': initial_demand.product_id.level,
                            'has_option': initial_demand.product_id.has_option,
                        },
                        "availability": initial_demand.availability,
                        "product_uom_qty": initial_demand.product_uom_qty,
                        "product_uom": initial_demand.product_uom.name,
                        "location_dest_id": initial_demand.location_dest_id.name,
                        "scrapped": initial_demand.scrapped,
                        "state": initial_demand.state,
                    })

                if 'PO' in picking_id.origin:
                    do_type = 'PO_DO'
                elif 'SO' in picking_id.origin:
                    do_type = 'SO_DO'

                vals = str({
                    'name': picking_id.name,
                    'type': do_type,
                    'status': picking_id.state,
                    'supplier': {
                        'supplier_id': picking_id.partner_id.supplier_id,
                        'name': picking_id.partner_id.name,
                        'street': picking_id.partner_id.street,
                        'street2': picking_id.partner_id.street2,
                        'city': picking_id.partner_id.city,
                        'state': picking_id.partner_id.state_id.name,
                        'zip': picking_id.partner_id.zip,
                        'country_id': picking_id.partner_id.country_id.name,
                        'email': picking_id.partner_id.email,
                        'website': picking_id.partner_id.website,
                        'street': picking_id.partner_id.street,
                        'active': picking_id.partner_id.active,
                        'comment': picking_id.partner_id.comment,
                        'fax': picking_id.partner_id.fax,
                        'phone': picking_id.partner_id.phone,
                        'mobile': picking_id.partner_id.mobile,
                    },
                    'date': picking_id.min_date,
                    'source_document': picking_id.origin,
                    'response': picking_id.rb_response,
                    'operations': operations,
                    'initial_demand': initial,
                    'delivery_type': picking_id.move_type,
                    'priority': picking_id.priority,
                })

                response = queue.send_message(MessageBody=vals)

                print(response.get('MessageId'))
                print(response.get('MD5OfMessageBody'))


class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    from_supplier = fields.Char('From', size=16, help="Supplier Name")
    sqs_product_id = fields.Char(string='Product ID', readonly=False)
    sqs_supplier_id = fields.Char('Supplier ID', required=False)
