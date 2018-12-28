# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xmlrpclib

class pos_product_sync(models.Model):
    _name = 'pos.product.sync'

    ip_address = fields.Char("IP Address")
    database_name = fields.Char("Database")
    username = fields.Char("Username")
    password = fields.Char("Password")

    @api.multi
    def sync_product(self):
        config_ids = self._context['active_ids'];
        configs = self.env['pos.product.sync'].search([('id', 'in', config_ids)], limit=1)
        for config in configs:
            ROOT = 'http://' + config.ip_address + '/xmlrpc/'
            DB = config.database_name
            PASS = config.password
            USER = config.username
            uid = xmlrpclib.ServerProxy(ROOT + 'common').login(DB, USER, PASS)
            sock = xmlrpclib.ServerProxy(ROOT + 'object')

            products = sock.execute(DB, uid, PASS, 'product.product', 'search_read', [
            ])
            fields = sock.execute(DB, uid, PASS, 'product.product', 'fields_get', [])

            for product_dict in products:
                for field_name in fields.keys():
                    field = fields[field_name]
                    if field['type'] in ['many2one']:
                        field_item = product_dict[field_name]
                        if field_item:
                            if field_name in ['product_tmpl_id', 'product_variant_id']:
                                del product_dict[field_name]
                            elif field_name in ['write_uid', 'create_uid','currency_id']:
                                del product_dict[field_name]
                            else:
                                product_dict[field_name] = field_item[0]
                                # TODO: Check external data
                                related_model = field['relation']
                                exist_item    = self.env[related_model].search([
                                    ('id', '=', field_item[0])
                                ], limit=1)
                                if not exist_item and not exist_item.id:
                                    if field_name in ['uom_id','uom_po_id']:
                                        del product_dict[field_name]
                                    else:
                                        self.env[related_model].create({
                                            'id': field_item[0],
                                            'name': field_item[1],
                                        })
                                else:
                                    exist_item.write({
                                        'name': field_item[1],
                                    })
                    elif field['type'] in ['many2many', 'one2many']:
                        del product_dict[field_name]
                    else:
                        if field_name in ['write_date', 'create_date', 'price']:
                            del product_dict[field_name]
                        elif field_name == 'id':
                            product_dict['external_id'] = product_dict['id']
                            del product_dict['id']
                if product_dict['default_code']:
                    exist_product = self.env['product.product'].search([
                        ('default_code', '=', product_dict['default_code'])
                    ], limit=1)
                else:
                    exist_product = self.env['product.product'].search([
                        ('external_id', '=', product_dict['external_id'])
                    ], limit=1)
                if exist_product and exist_product.id:
                    exist_product.write(product_dict)
                else:
                    self.env['product.product'].create(product_dict)
        return True


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    _sql_constraints = [
        ('default_code_uniq',
        'unique (default_code)', 'Default_code must be unique.')
    ]