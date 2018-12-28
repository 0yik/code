# -*- coding: utf-8 -*-

import boto3
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import json


class CustomDeliveryOrder(models.Model):
    _inherit = "stock.picking"

    rb_response = fields.Selection(
        [("success", "Success"), ("failed", "Failed")], "Response")


class CustomStockMove(models.Model):
    _inherit = "stock.move"

    tracking_no = fields.Char("Tracking No.")


class purchase_order_confirm(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ["draft", "sent"]:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == "one_step" \
                    or (order.company_id.po_double_validation == "two_step"
                        and order.amount_total < self.env.user.company_id.currency_id.compute(
                            order.company_id.po_double_validation_amount, order.currency_id)) \
                    or order.user_has_groups("purchase.group_purchase_manager"):
                order.button_approve()

            else:
                order.write({"state": "to approve"})

            order.send_queued_messages()
        return True

    @api.model
    def send_queued_messages(self):
        """ Connect to Amazon SQS and Recieve Messages """

        ir_values = self.env["ir.values"]
        queue_ref = ir_values.get_default("amazon.sqs", "queue_ref", False)
        conn_obj = self.env["amazon.sqs"].search(
            [("id", "=", queue_ref)], limit=1)

        max_queue_messages = 10

        # sqs = boto3.resource("sqs")

        # To get sqs object without the aws configuration file
        if conn_obj.id:
            sqs = boto3.resource("sqs",
                                 region_name=conn_obj.default_region,
                                 aws_access_key_id=conn_obj.aws_access_key_id,
                                 aws_secret_access_key=conn_obj.aws_secret_access_key)

        else:
            raise Warning(
                _("Check your AWS Access Key ID, AWS Secret Access Key, Region Name and Queue name"))

        # Get the queue
        try:
            queue = sqs.get_queue_by_name(QueueName=conn_obj.delivery_queue)
        except Exception:
            raise Warning(
                _("Queue Name not Found! Please Check your Amazon SQS Connection."))

        print("* * * . . . Sending Messages To Amazon SQS . . . * * *")

        max_queue_messages = 10
        if self.picking_ids:
            for picking_id in self.picking_ids:
                operations = []
                initial = []
                for operation_line in picking_id.pack_operation_product_ids:
                    operations.append({
                        "product": {
                            "product_id": str(operation_line.product_id.product_id),
                            "product_name": str(operation_line.product_id.name),
                            "model": str(operation_line.product_id.model),
                            "upc": str(operation_line.product_id.upc),
                            "jan": str(operation_line.product_id.jan),
                            "isbn": str(operation_line.product_id.isbn),
                            "mpn": str(operation_line.product_id.mpn),
                            "brand_name": str(operation_line.product_id.brand_name),
                            "special_discount": operation_line.product_id.special_discount,
                            "has_expiry": operation_line.product_id.has_expiry,
                            "is_liquid": operation_line.product_id.is_liquid,
                            "is_upc_checked": operation_line.product_id.is_upc_checked,
                            "gift_wrap": operation_line.product_id.gift_wrap,
                            "isbn": str(operation_line.product_id.isbn),
                            "height": operation_line.product_id.height,
                            "viewed": operation_line.product_id.viewed,
                            "width": operation_line.product_id.width,
                            "offerPriceFormatted": str(operation_line.product_id.offerPriceFormatted),
                            "length": operation_line.product_id.length,
                            "minimum": operation_line.product_id.minimum,
                            "level": operation_line.product_id.level,
                            "has_option": operation_line.product_id.has_option,
                        },
                        "product_qty": operation_line.product_qty,
                        "product_state": str(operation_line.state),
                        "from_supplier": operation_line.from_supplier,
                        "sqs_product_id": operation_line.sqs_product_id,
                        "sqs_supplier_id": operation_line.sqs_supplier_id,
                        "qty_done": operation_line.qty_done,
                    })
                for initial_demand in picking_id.move_lines:
                    on_hand = self.product_id.qty_available
                    add = self.env["stock.pack.operation"].search(
                        [("product_id", "=", initial_demand.product_id.id), ("picking_id", "=", initial_demand.picking_id.id)]).product_qty
                    initial.append({
                        "product": {
                            "product_id": str(initial_demand.product_id.product_id),
                            "product_name": str(initial_demand.product_id.name),
                            "model": str(initial_demand.product_id.model),
                            "upc": str(initial_demand.product_id.upc),
                            "jan": str(initial_demand.product_id.jan),
                            "isbn": str(initial_demand.product_id.isbn),
                            "mpn": str(initial_demand.product_id.mpn),
                            "brand_name": str(initial_demand.product_id.brand_name),
                            "special_discount": initial_demand.product_id.special_discount,
                            "has_expiry": initial_demand.product_id.has_expiry,
                            "is_liquid": initial_demand.product_id.is_liquid,
                            "is_upc_checked": initial_demand.product_id.is_upc_checked,
                            "gift_wrap": initial_demand.product_id.gift_wrap,
                            "isbn": str(initial_demand.product_id.isbn),
                            "height": initial_demand.product_id.height,
                            "viewed": initial_demand.product_id.viewed,
                            "width": initial_demand.product_id.width,
                            "offerPriceFormatted": str(initial_demand.product_id.offerPriceFormatted),
                            "length": initial_demand.product_id.length,
                            "minimum": initial_demand.product_id.minimum,
                            "level": initial_demand.product_id.level,
                            "has_option": initial_demand.product_id.has_option,
                        },
                        "availability": initial_demand.availability,
                        "product_uom_qty": initial_demand.product_uom_qty,
                        "product_uom": str(initial_demand.product_uom.name),
                        "location_dest_id": str(initial_demand.location_dest_id.name),
                        "scrapped": initial_demand.scrapped,
                        "state": str(initial_demand.state),
                        "product_quantity": int(on_hand + add),

                    })

                vals = {
                    "name": str(picking_id.name),
                    "type": str("PO_DO"),
                    "status": str(picking_id.state),
                    "supplier": {
                        "supplier_id": str(picking_id.partner_id.supplier_id),
                        "name": str(picking_id.partner_id.name),
                        "street": str(picking_id.partner_id.street),
                        "street2": str(picking_id.partner_id.street2),
                        "city": str(picking_id.partner_id.city),
                        "state": str(picking_id.partner_id.state_id.name),
                        "zip": str(picking_id.partner_id.zip),
                        "country_id": str(picking_id.partner_id.country_id.name),
                        "email": str(picking_id.partner_id.email),
                        "website": str(picking_id.partner_id.website),
                        "street": str(picking_id.partner_id.street),
                        "active": picking_id.partner_id.active,
                        "comment": str(picking_id.partner_id.comment),
                        "fax": picking_id.partner_id.fax,
                        "phone": str(picking_id.partner_id.phone),
                        "mobile": picking_id.partner_id.mobile,
                    },
                    "date": picking_id.min_date,
                    "source_document": str(picking_id.origin),
                    "response": picking_id.rb_response,
                    "operations": operations,
                    "initial_demand": initial,
                    "delivery_type": str(picking_id.move_type),
                    "priority": str(picking_id.priority),
                }

                val = str(json.dumps(vals))
                response = queue.send_message(MessageBody=val)

                print(response.get("MessageId"))
                print(response.get("MD5OfMessageBody"))
