from odoo import models, fields, api

from odoo.addons.connector.event import on_record_create, on_record_write
from odoo.addons.connector.connector import ConnectorEnvironment

from ..connector import get_environment
from ..backend import quick
from ..unit.backend_adapter import (GenericAdapter)
from odoo.addons.connector.unit.synchronizer import (Importer, Exporter)
import xmlrpclib

from odoo.exceptions import except_orm, Warning, RedirectWarning
import logging
from ..unit.import_synchronizer import ( DelayedBatchImporter, WooImporter)
from odoo.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper
                                                  )
from odoo.addons.queue_job.job import job, related_action
from ..related_action import unwrap_binding
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):

    _inherit = 'account.invoice'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='Quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Woo', readonly=False, required=False)
    sync_date = fields.Datetime(string='Last synchronization date')
    doc_number = fields.Char(string='QBO Doc Number', help='Stores QBO document number for reference purpose')
    
    @api.multi
    def sync_invoice(self):
        """ Export Customer Invoices And Details. """

        env = self.backend_id.get_environment(self._name)
        
        # session = ConnectorSession(self.env.cr, self.env.uid,
        #                            context=self.env.context)
        # env = get_environment(session, 'account.invoice', self.backend_id[0].id)
        invoice_exporter = env.get_connector_unit(InvoiceExporter)
        invoice_exporter.run_sync(self.quickbook_id or 0, self)

    @api.multi
    @job(default_channel='root.quick')
    def invoice_import_batch(session, model_name, backend_id, filters=None):
        """ Import Customer Invoices And Details. """

        env = get_environment(session, model_name, backend_id)
        importer = env.get_connector_unit(InvoiceBatchImporter)
        importer.run(filters=filters)

    @job(default_channel='root.quick')
    @related_action(action=unwrap_binding)
    def export_invoice_details(self, backend_id):
        """ Export Customer Invoices And Details. """

        env = backend_id.get_environment(self._name)
        # env = get_environment(session, model_name, backend_id)
        inventory_exporter = env.get_connector_unit(
            InvoiceExporter)

        return inventory_exporter.run(backend_id, fields)

@quick
class InvoiceAdapter(GenericAdapter):
    _model_name = 'account.invoice'
    _booking_model = 'invoice'

    def _call(self, method, arguments):
        print method
        try:
            return super(InvoiceAdapter, self)._call(method, arguments)
        except xmlrpclib.Fault as err:
            # this is the error in the Quickbook API
            # when the apointment does not exist
            if err.faultCode == 102:
                raise IDMissingInBackend
            else:
                raise

    def search(self, filters=None, from_date=None, to_date=None):
        """ Search records according to some criteria and return a
        list of ids

        :rtype: list
        """

        if filters is None:
            filters = {}
        WOO_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        dt_fmt = WOO_DATETIME_FORMAT
        if from_date is not None:
            # updated_at include the created records
            filters.setdefault('updated_at', {})
            filters['updated_at']['from'] = from_date
        if to_date is not None:
            filters.setdefault('updated_at', {})
            filters['updated_at']['to'] = to_date
        # the search method is on ol_customer instead of customer
        if 'url' in filters:
            if filters['url'] is 'invoice':
                return self._call('/query?query=select%20from%20invoice',
                                  [filters] if filters else [{}])
        

    def update_invoice(self, id, data):
        # product_stock.update is too slow

        return self._call_invoice('update_invoice', [int(id), data])


@quick
class InvoiceBatchImporter(DelayedBatchImporter):

    """ Import the Quickbook Partners.

    For every partner in the list, a delayed job is created.
    """
    _model_name = ['account.invoice']
    url = None

    def _import_record(self, quickbook_id, priority=None):
        """ Delay a job for the import """

        super(InvoiceBatchImporter, self)._import_record(
            quickbook_id, priority=priority)

    def run(self, filters=None):
        """ Run the synchronization """
        from_date = filters.pop('from_date', None)
        to_date = filters.pop('to_date', None)
        count = 1
        record_ids = ['start']
        filters['url'] = 'invoice'
        while record_ids:
            filters['count'] = count
            record_ids = self.backend_adapter.search(
                filters,
                from_date=from_date,
                to_date=to_date,
            )
    #         record_ids = self.env['bk.backend'].get_salesreceipt_ids(record_ids)
            _logger.info('search for invoice %s returned %s',
                         filters, record_ids)
            count += 300
            self.url = 'invoice'
            if 'Invoice' in record_ids['QueryResponse']:
                record_ids = record_ids['QueryResponse']['Invoice']
                for record_id in record_ids:
                    
                    self._import_record(int(record_id['Id']), 40)
            else:
                record_ids = record_ids['QueryResponse']
        
InvoiceBatchImporter = InvoiceBatchImporter  # deprecated


@quick
class InvoiceImporter(WooImporter):
    _model_name = ['account.invoice']
    url = None

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        record = self.woo_record
        if 'Invoice' in record:
            if 'Line' in record['Invoice']:
                for line in record['Invoice']['Line']:
                    if 'SalesItemLineDetail' in line:
                        self._import_dependency(line['SalesItemLineDetail']['ItemRef']['value'],
                                        'product.template')

        if 'Invoice' in record:
            if 'SalesTermRef' in record['Invoice']:
                if record['Invoice']['SalesTermRef']:
                    self._import_dependency(record['Invoice']['SalesTermRef']['value'],
                                    'account.payment.term')
        return

    def _create(self, data):
        openerp_binding = super(InvoiceImporter, self)._create(data)
        return openerp_binding

    def _after_import(self, binding):
        """ Hook called at the end of the import """
        record = self.woo_record
        if 'Invoice' in record:
            if 'LinkedTxn' in record['Invoice']:
                for line in record['Invoice']['LinkedTxn']:
                    if 'TxnType' in line:
                        if line['TxnType'] == 'Payment':
                            self._import_dependency(line['TxnId'],
                                            'account.payment')
        return

InvoiceImporter = InvoiceImporter  # deprecated


@quick
class InvoiceImportMapper(ImportMapper):
    _model_name = 'account.invoice'

    @mapping
    def partner_id(self, record):
        if 'Invoice' in record:
            if 'CustomerRef' in record['Invoice']:
                rec = record['Invoice']
                if 'CustomerRef' in rec:
                    partner_id = self.env['res.partner'].search(
                        [('quickbook_id', '=', rec['CustomerRef']['value']),
                         ('name', '=', rec['CustomerRef']['name'])])
                    if not partner_id:
                        raise Warning(('Please import "Customer" First'))

                    partner_id = partner_id.id or False
                else:
                    partner_id = False
                return {'partner_id': partner_id}

    @mapping
    def payment_term_id(self, record):
        if 'Invoice' in record:
            if 'SalesTermRef' in record['Invoice']:
                rec = record['Invoice']
                if 'SalesTermRef' in rec:
                    payment_term = self.env['account.payment.term'].search(
                        [('quickbook_id', '=', rec['SalesTermRef']['value'])])

                    payment_term = payment_term.id
                else:
                    payment_term = False
                return {'payment_term_id': payment_term}

    @mapping
    def invoice_line_ids(self, record):
        if 'Invoice' in record:
            rec = record['Invoice']
            if 'Line' in rec:
                product_ids = []
                for lines in rec['Line']:
                    if 'SalesItemLineDetail' in lines:
                        product_template_id = self.env['product.template'].search(
                            [('quickbook_id', '=', lines['SalesItemLineDetail']['ItemRef']['value']),
                             ('name', '=', lines['SalesItemLineDetail']['ItemRef']['name'])])
                        product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_template_id.id),
                             ('name', '=', product_template_id.name)])
                        order_id = self.env['account.invoice'].search([('backend_id', '=', self.backend_record.id),('quickbook_id', '=', rec['Id'])])

                        tax_id = []
                        if lines['SalesItemLineDetail']['TaxCodeRef']['value'] == 'TAX':
                            if 'TxnTaxDetail' in rec and 'TxnTaxCodeRef' in rec.get('TxnTaxDetail'):
                                tax_id = [self.env['account.tax'].search([('amount_type', '=', 'group'),('quickbook_id', '=', rec['TxnTaxDetail']['TxnTaxCodeRef']['value'])]).id]
                        # tax_id = self.env['account.tax'].search([('amount_type', '=', 'group'),('quickbook_id', '=', lines['SalesItemLineDetail']['TaxCodeRef']['value'])]).id or None
                        order = self.env['account.invoice.line'].search([('invoice_id', '=', order_id.id),('quickbook_id', '=', lines['Id']),('name', '=', lines.get('Description'))])
                        
                        if 'UnitPrice' in lines['SalesItemLineDetail']:
                            unitprice = lines['SalesItemLineDetail']['UnitPrice']
                        else:
                            unitprice = product_id.list_price

                        if 'Qty' in lines['SalesItemLineDetail']:
                            quantity = lines['SalesItemLineDetail']['Qty']
                        else:
                            quantity = product_id.qty_available

                        result = {'product_id':product_id.id,
                            # 'sequence': lines['LineNum'],
                            'price_unit': unitprice,
                            'quantity': quantity,
                            'tax_id': [(6, 0, [tax_id])],
                            'account_id': 41,
                            'uom_id': 1,
                            'price_subtotal': lines['Amount'],
                            'name': lines['Description'],
                            'quickbook_id': lines['Id'],
                            }
                        if not order:

                            product_ids.append([0,0,result]) or False
                        else:
                            product_ids.append([1,order.id,result])

                return {'invoice_line_ids': product_ids}

    # @mapping
    # def invoice_line_tax_id(self, record):
    #     if 'Invoice' in record:
    #         if 'Line' in record['Invoice']:
    #             rec = record['Invoice']
    #             invoice_line_tax_id = self.env['account.tax'].search(
    #                 [('name', '=', rec['Line'][0]['SalesItemLineDetail']['TaxCodeRef']['value'])])
    #             if not invoice_line_tax_id:
    #                 invoice_line_tax_id = self.env['res.currency'].create(
    #                     {'name': rec['Line'][0]['SalesItemLineDetail']['TaxCodeRef']['value']})
    #             invoice_line_tax_id = invoice_line_tax_id.id or False
    #         else:
    #             invoice_line_tax_id = False
    #         return {'invoice_line_tax_id': rec['Line'][0]['SalesItemLineDetail']['TaxCodeRef']}


    @mapping
    def date_invoice(self, record):
        if 'Invoice' in record:
            if 'TxnDate' in record['Invoice']:
                rec = record['Invoice']
                return {'date_invoice': rec['TxnDate']}

    @mapping
    def doc_number(self, record):
        if 'Invoice' in record:
            if 'DocNumber' in record['Invoice']:
                rec = record['Invoice']
                return {'doc_number': rec['DocNumber']}

    @mapping
    def date_due(self, record):
        if 'Invoice' in record:
            if 'DueDate' in record['Invoice']:
                rec = record['Invoice']
                return {'date_due': rec['DueDate']}

    @mapping
    def id(self, record):
        if 'Invoice' in record:
            rec = record['Invoice']
            if rec['Id']:
                return {'quickbook_id': rec['Id']}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}



@quick
class InvoiceExporter(Exporter):
    _model_name = ['account.invoice']

    def _get_data(self, product, fields):
        result = {}
        return result

    def _domain_for_update_invoice(self):
        return [
            ('backend_id', '!=', None),

        ]

    def run(self, binding_id, fields):
        """ Export the product inventory to wordpress """

        invoice_obj = self.env['account.invoice']
        domain = self._domain_for_update_invoice()

        invoice_data = invoice_obj.search(domain)

        if invoice_data:
            for invoice in invoice_data:
                self.backend_adapter.update_invoice(invoice.quickbook_id,
                                                    {'invoice': data})

    def run_sync(self, binding_id, data):

        self.backend_adapter.update_invoice(binding_id, {'invoice': data})


InvoiceExporter = InvoiceExporter  # deprecated


# @job(default_channel='root.quick')
# @related_action(action=unwrap_binding)
# def export_invoice_details(session, model_name, record_id, fields=None):
#     """ Export the invoice of customers. """
#     account = session.env[model_name].browse(record_id)
#     try:
#         if account.backend_id:
#             backend_id = account.backend_id.id
#         else:
#             backend_id = record_id

#     finally:
#         pass

#     env = get_environment(session, model_name, backend_id)
#     inventory_exporter = env.get_connector_unit(
#         AccountExporter)


#     return inventory_exporter.run(record_id, fields)


# @on_record_create(model_names=['account.invoice'])
# @on_record_write(model_names=['account.invoice'])
def single_export_appointments(session, model_name, record_id, fields=None):
    if not 'job_uuid' in session.context.keys():

        invoice = session.env[model_name].browse(record_id)
        if not invoice.backend_id:
            invoice.backend_id = session.env[
                'qb.backend'].search([('id', '!=', None)])[0]
        env = get_environment(
            session, 'account.invoice', invoice.backend_id.id)
        invoice_exporter = env.get_connector_unit(InvoiceExporter)
        invoice_exporter.run_sync(invoice.quickbook_id or 0, invoice)


@on_record_create(model_names=['account.invoice'])
def create_invoice(session, model_name, record_id, fields=None):
    if 'job_uuid' in session.context.keys():
        invoice_id = session[model_name].search([('id', '=', record_id)])
        if invoice_id:
            invoice_id.action_invoice_open()

class quickbook_product(models.Model):

    _inherit = 'account.invoice.line'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)


class quickbook_acount_tax(models.Model):

    _inherit = 'account.tax'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)


class quickbook_product_product(models.Model):

    _inherit = 'product.product'

    backend_id = fields.Many2one(comodel_name='qb.backend',
                                 string='quick Backend', store=True,
                                 readonly=False, required=False,
                                 )

    quickbook_id = fields.Char(
        string='ID on Quickbook', readonly=False, required=False)
