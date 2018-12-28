from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError


class serial_lot_number(models.Model):
    _inherit = 'serial.lot.number'

    @api.multi
    def wizard_view_mrp(self):
        view = self.env.ref('warehouse_serializer_mrp.view_form_serial_lot_from_mo')

        return {
            'name': _('Enter transfer details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'serial.lot.number',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }

    @api.multi
    def write(self, vals):
        res = super(serial_lot_number, self).write(vals)
        mo_id = self.env['mrp.production'].search([('name', '=', self.serial_name)])
        if mo_id:
            lists = []
            for stock_lot in self.stock_lot_line_ids:
                if not lists:
                    lists.append({'name': stock_lot.product_id.name, 'qty': stock_lot.quantity})
                else:
                    if stock_lot.product_id.name not in [line.get('name') for line in lists]:
                        lists.append({'name': stock_lot.product_id.name, 'qty': stock_lot.quantity})
                    else:
                        for list in lists:
                            if list.get('name') == stock_lot.product_id.name:
                                list.update({'qty': list.get('qty') + stock_lot.quantity})
                                break

            for finish in mo_id.move_finished_ids:
                for list in lists:
                    if finish.product_id.name == list.get('name'):
                        if finish.product_id.tracking == 'lot':
                            if finish.quantity_done != list.get('qty'):
                                raise UserError(_('%s Product quantity should be same as Finished Product quantity produce.')% finish.product_id.name)

            for stock_lot in self.stock_lot_line_ids:
                for finish in mo_id.move_finished_ids:
                    if finish.product_id == stock_lot.product_id:
                        for move_lot in finish.active_move_lot_ids:
                            if move_lot.lot_id and move_lot.lot_id.name == stock_lot.lot_serial_number:
                                move_lot.write({'quantity_done':stock_lot.quantity, 'quantity': stock_lot.quantity})
        return res


class serial_lot_product(models.Model):
    _inherit = 'serial.lot.product'

    @api.multi
    def split_quantities_mrp(self):
        mo_id = self.env['mrp.production'].search([('name', '=', self.lot_id.serial_name)])
        if self.product_id.tracking == 'serial':
            product_category = self.product_id.categ_id

            product_sku_serializer_id = self.env['lot.number.serializer'].search(
                [('product_categ_id', '=', product_category.id)])

            if product_sku_serializer_id:
                self.quantity = self.quantity - 1
                prefix_sku = product_sku_serializer_id.prefix_lot
                current_number = int(product_sku_serializer_id.current_number) + 1

                sequence = str(current_number).zfill(product_sku_serializer_id.digits)

                suffix_sku = product_sku_serializer_id.suffix_lot

                if product_sku_serializer_id.start_with_sku == True:
                    serialize_sequence = self.product_id.default_code + '_' + prefix_sku + sequence + suffix_sku
                else:
                    serialize_sequence = prefix_sku + sequence + suffix_sku

                # serialize_sequence = prefix_sku + sequence + suffix_sku
                product_sku_serializer_id.current_number = sequence
                self.lot_id.write({'stock_lot_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                                                  'quantity': '1',
                                                                  'source_location_id': self.location_dest_id.id,
                                                                  'lot_serial_number': serialize_sequence,
                                                                  'location_dest_id': self.location_dest_id.id,
                                                                  })]})

                lot_id = self.env['stock.production.lot'].search([('name', '=', self.lot_serial_number)])

                production_lot_id = self.env['stock.production.lot'].create(
                    {'name': serialize_sequence, 'product_id': self.product_id.id,})

                for finish_id in mo_id.move_finished_ids:
                    if finish_id.product_id == self.product_id:
                        move_lot_id = finish_id.active_move_lot_ids.filtered(lambda x : x.lot_id == lot_id)
                        move_lot_id.write({'quantity_done': self.quantity})
                        finish_id.write(
                            {'active_move_lot_ids': [(0, 0, {
                                'lot_id': production_lot_id.id,
                                'quantity_done': 1
                            })]})
            else:
                raise UserError(_('First create serial number'))

        elif self.product_id.tracking == 'lot':

            self.quantity = self.quantity - 1

            if self.main_product == True:
                self.write({'check_lot_number': True})

            product_category = self.product_id.categ_id

            lot_number_serializer_id = self.env['lot.number.serializer'].search(
                [('product_categ_id', '=', product_category.id)])
            if lot_number_serializer_id:
                prefix_lot = lot_number_serializer_id.prefix_lot
                current_number = int(lot_number_serializer_id.current_number) + 1
                suffix_lot = lot_number_serializer_id.suffix_lot

                sequence = str(current_number).zfill(lot_number_serializer_id.digits)
                if lot_number_serializer_id.start_with_sku == True:
                    if self.product_id.default_code:
                        serialize_sequence = self.product_id.default_code + '_' + prefix_lot + sequence + suffix_lot
                    else:
                        serialize_sequence = prefix_lot + sequence + suffix_lot
                else:
                    serialize_sequence = prefix_lot + sequence + suffix_lot

                lot_number_serializer_id.current_number = sequence

                self.lot_id.write({'stock_lot_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                                                  'quantity': '1',
                                                                  'source_location_id': self.location_dest_id.id,
                                                                  'lot_serial_number': serialize_sequence,
                                                                  'location_dest_id': self.location_dest_id.id,
                                                                  })]})

                lot_id = self.env['stock.production.lot'].search([('name', '=', self.lot_serial_number)])

                production_lot_id = self.env['stock.production.lot'].create(
                    {'name': serialize_sequence, 'product_id': self.product_id.id,
                     })

                for finish_id in mo_id.move_finished_ids:
                    if finish_id.product_id == self.product_id:
                        move_lot_id = finish_id.active_move_lot_ids.filtered(lambda x : x.lot_id == lot_id)
                        move_lot_id.write({'quantity_done': self.quantity, 'quantity': self.quantity})
                        finish_id.write(
                            {'active_move_lot_ids': [(0, 0, {
                                'lot_id': production_lot_id.id,
                                'quantity_done': 1,
                                'quantity' : 1
                            })]})

            else:
                raise UserError(_('First create lot serial number'))


        elif self.product_id.tracking == 'none':
            raise UserError(_('You can not select the tracking for the Product'))

        if self and self[0]:
            return self[0].lot_id.wizard_view_mrp()

    @api.multi
    def generate_lot_number_mrp(self):
        mo_id = self.env['mrp.production'].search([('name', '=', self.lot_id.serial_name)])
        product_category = self.product_id.categ_id

        if (self.lot_serial_number == '') or (self.lot_serial_number == False):
            if self.product_id.tracking == 'serial':
                product_sku_serializer_id = self.env['lot.number.serializer'].search(
                    [('product_categ_id', '=', product_category.id)])
                if product_sku_serializer_id:
                    prefix_sku = product_sku_serializer_id.prefix_lot
                    current_number = int(product_sku_serializer_id.current_number) + 1

                    sequence = str(current_number).zfill(product_sku_serializer_id.digits)

                    suffix_sku = product_sku_serializer_id.suffix_lot

                    if product_sku_serializer_id.start_with_sku == True:
                        serialize_sequence = self.product_id.default_code + '_' + prefix_sku + sequence + suffix_sku
                    else:
                        serialize_sequence = prefix_sku + sequence + suffix_sku

                    # serialize_sequence = prefix_sku + sequence + suffix_sku
                    product_sku_serializer_id.current_number = sequence

                    self.write({'lot_serial_number': serialize_sequence})

                    production_lot_id = self.env['stock.production.lot'].create(
                        {'name': serialize_sequence, 'product_id': self.product_id.id,
                         })

                    # for finish_id in mo_id.move_finished_ids:
                    #     if finish_id.product_id == self.product_id:
                    #         finish_id.write(
                    #             {'active_move_lot_ids': [(0, 0, {
                    #                 'lot_id': production_lot_id.id,
                    #                 'quantity_done': self.quantity
                    #             })]})
                else:
                    raise UserError(_('First create Product SKU Serializer'))
            elif self.product_id.tracking == 'lot':
                lot_number_serializer_id = self.env['lot.number.serializer'].search(
                    [('product_categ_id', '=', product_category.id)])

                if lot_number_serializer_id:
                    prefix_lot = lot_number_serializer_id.prefix_lot
                    current_number = int(lot_number_serializer_id.current_number) + 1
                    suffix_lot = lot_number_serializer_id.suffix_lot

                    sequence = str(current_number).zfill(lot_number_serializer_id.digits)
                    if lot_number_serializer_id.start_with_sku == True:
                        if self.product_id.default_code:
                            serialize_sequence = self.product_id.default_code + '_' + prefix_lot + sequence + suffix_lot
                        else:
                            serialize_sequence = prefix_lot + sequence + suffix_lot
                    else:
                        serialize_sequence = prefix_lot + sequence + suffix_lot

                    lot_number_serializer_id.current_number = sequence

                    self.write({'lot_serial_number': serialize_sequence})

                    production_lot_id = self.env['stock.production.lot'].create(
                        {'name': serialize_sequence, 'product_id': self.product_id.id,
                         })

                    # for finish_id in mo_id.move_finished_ids:
                    #     if finish_id.product_id == self.product_id:
                    #         finish_id.write(
                    #             {'active_move_lot_ids': [(0, 0, {
                    #                 'lot_id': production_lot_id.id,
                    #                 'quantity_done': self.quantity,
                    #             })]})
                else:
                    raise UserError(_('First create Batch/lot Number serializer'))
            if self and self[0]:
                return self[0].lot_id.wizard_view()
        else:
            for finish in mo_id.move_finished_ids:
                move_lots = finish.active_move_lot_ids.filtered(lambda x: x.lot_id.name == self.lot_serial_number)
                self.quantity = sum(move.quantity_done for move in move_lots)
            if self and self[0]:
                return self[0].lot_id.wizard_view()
            raise UserError(_('Serializer number already generated'))
