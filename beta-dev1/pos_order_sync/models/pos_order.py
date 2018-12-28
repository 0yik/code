from odoo import models, fields, api
import xmlrpclib

class pos_order(models.Model):
    _inherit = 'pos.order'

    pos_sync = fields.Boolean('Already Sync',default=False)

    @api.multi
    def update_pos_sync(self):
        if self:
            pos_order_ids = self.filtered(lambda record: record.pos_sync == False)
            db = 'Restaurant'
            username = 'demo@demo.com'
            password = 'demo'
            protocol = 'jsonrpc+ssl'
            port = 8069
            sock_common = xmlrpclib.ServerProxy('http://beta-dev1.hashmicro.com/xmlrpc/common')
            uid = sock_common.login(db, username, password)

            # replace localhost with the address of the server if it is not on the same server
            # OpenERP Object manipulation service
            sock = xmlrpclib.ServerProxy('http://beta-dev1.hashmicro.com/xmlrpc/object')
            for record in pos_order_ids:
                pos_data = {
                    'name': record.name or '',
                    'date_order': record.date_order,
                    'state': 'paid'
                }
                # Calling the remote ORM create method to search for records
                if record.partner_id:
                    partner = sock.execute(db, uid, password, 'res.partner', 'search', [('name', '=', record.partner_id.name)])
                    if partner:
                        pos_data['partner_id'] = partner[0]
                    else:
                        partner_data = {
                            'name': record.partner_id.name,
                        }
                        partner_id = sock.execute(db, uid, password, 'res.partner', 'create', partner_data)
                        pos_data['partner_id'] = partner_id
                if record.branch_id:
                    branch = sock.execute(db, uid, password, 'res.branch', 'search', [('name', '=', record.branch_id.name)])
                    if branch:
                        pos_data['branch_id'] = branch[0]
                    else:
                        branch_data = {
                            'name': record.branch_id.name,
                            'company_id': record.company_id.id
                        }
                        branch_id = sock.execute(db, uid, password, 'res.branch', 'create', branch_data)
                        pos_data['branch_id'] = branch_id
                session = sock.execute(db, uid, password, 'pos.session', 'search', [('state', '=', 'opened')])
                if not session:
                    pos = sock.execute(db, uid, password, 'pos.config', 'search', [])
                    session_data = {
                        'user_id':      uid,
                        'config_id':    pos[0],
                    }
                    session_id = sock.execute(db, uid, password, 'pos.session', 'create', session_data)
                    pos_data['session_id'] = session_id
                else:
                    pos_data['session_id'] = session[0]
                pos_id = sock.execute(db, uid, password, 'pos.order', 'create', pos_data)
                for pos_line in record.lines:
                    po_line_data = {
                        'qty': pos_line.qty,
                        'price_unit': pos_line.price_unit,
                        'discount': pos_line.discount,
                        'order_id': pos_id,
                    }
                    product = sock.execute(db, uid, password, 'product.product', 'search',[('name', '=', pos_line.product_id.name)])
                    if not product:
                        product_data = {
                            'name': pos_line.product_id.name,
                            'type': 'product',
                            'default_code': pos_line.product_id.default_code,

                        }
                        product_id = sock.execute(db, uid, password, 'product.product', 'create', product_data)
                        po_line_data['product_id'] = product_id
                    else:
                        po_line_data['product_id'] = product[0]
                    tax_list = []
                    for tax in pos_line.tax_ids_after_fiscal_position:
                        tax_ids = sock.execute(db, uid, password, 'account.tax', 'search',[('name', '=', tax.name)])
                        if not tax_ids:
                            tax_data = {'name': tax.name,
                                        'type_tax_use': tax.type_tax_use,
                                        'amount_type': tax.amount_type,
                                        'amount': tax.amount
                                        }
                            tax_id = sock.execute(db, uid, password, 'account.tax', 'create', tax_data)
                            tax_list.append(tax_id)
                        else:
                            tax_list.append(tax_ids[0])
                    po_line_data['tax_ids_after_fiscal_position'] = [(6, 0, tax_list)]
                    po_line_data['tax_ids'] = [(6, 0, tax_list)]
                    po_line_id = sock.execute(db, uid, password, 'pos.order.line', 'create', po_line_data)
                    
                for payment in record.statement_ids:
                    payment_data = {
                        'name':     payment.name,
                        'date':     payment.date,
                        'ref':      payment.ref,
                        'amount':   payment.amount,
                        'sequence': payment.sequence,
                        'pos_statement_id': pos_id
                    }
                    partner = sock.execute(db, uid, password, 'res.partner', 'search',
                                           [('name', '=', payment.partner_id.name)])
                    if partner:
                        payment_data['partner_id'] = partner[0]
                    statement = sock.execute(db, uid, password, 'account.bank.statement', 'search',[('name', '=', payment.statement_id.name)])
                    if not statement:
                        statement_data = {
                            'name': payment.statement_id.name
                        }
                        journal = sock.execute(db, uid, password, 'account.journal', 'search',[('name', '=', payment.journal_id.name)])
                        if not journal:
                            journal_data = {
                                'name': payment.journal_id.name,
                                'type': payment.journal_id.type,
                                'code': payment.journal_id.code,
                            }
                            journal_id = sock.execute(db, uid, password, 'account.journal', 'create', journal_data)
                            statement_data['journal_id'] = journal_id
                        else:
                            statement_data['journal_id'] = journal[0]
                        statement_id = sock.execute(db, uid, password, 'account.bank.statement', 'create', statement_data)
                        payment_data['statement_id'] = statement_id
                    else:
                        payment_data['statement_id'] = statement[0]
                    payment_line = sock.execute(db, uid, password, 'account.bank.statement.line', 'create', payment_data)
                record.pos_sync = True
            # Get the details from all contacts

        return True