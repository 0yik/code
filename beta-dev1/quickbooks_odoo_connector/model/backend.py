from odoo import models, fields, api, osv

from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth2Session
import requests
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth2
from urlparse import parse_qs
from datetime import datetime

from datetime import timedelta
import json
from odoo.addons.connector.connector import ConnectorEnvironment
from ..unit.import_synchronizer import (WooImporter)
from odoo.addons.queue_job.job import job, related_action
# from ..connector import get_environment
# from odoo.addons.connector.session import ConnectorSession
import webbrowser
from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import UserError
from base64 import b64encode


class bk_backend(models.Model):
    _name = 'qb.backend'
    # _inherit = account.invoice
    _inherit = 'connector.backend'
    _description = 'quickbook Backend Configuration'

    _backend_type = 'quick'
    name = fields.Char(string='name')
    location = fields.Char("Url", required=True)
    client_key = fields.Char("Consumer key", required=True)
    client_secret = fields.Char("Consumer Secret", required=True)
    type = fields.Selection([('oauth1','OAuth1'),
                            ('oauth2','OAuth2')],
                            default='oauth2',
                            string='Oauth Type')
    version = fields.Selection([('v2', 'V2'),
                            ('v2', 'V3')], 'Version')

    #oauth1 fields
    request_token_url = fields.Char(
        "Request Token URl", default='https://oauth.intuit.com/oauth/v1/get_request_token')
    access_token_url = fields.Char(
        "Access Token URl", default='https://oauth.intuit.com/oauth/v1/get_access_token')
    authorization_base_url = fields.Char(
        "Authorization Base URl", default='https://appcenter.intuit.com/connect/begin')
    company_id = fields.Char("Company Id")
    resource_owner_key = fields.Char(string="Token")
    resource_owner_secret = fields.Char(string="Token Secret")
    signature_method = fields.Char(string="Signature Method")
    verify_ssl = fields.Boolean("Verify SSL")
    default_lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Default Language',
        help="If a default language is selected, the records "
             "will be imported in the translation of this language.\n"
             "Note that a similar configuration exists "
             "for each storeview.",
    )
    asset_account_ref = fields.Many2one(
        comodel_name='account.account',
        string="Asset Account",
    )
    new_url = fields.Char("Authorized Url")
    go_to = fields.Char("Go to link")


    #oauth2 fields
    redirect_uri = fields.Char("Redirect URI", required=True, default='https://www.getpostman.com/oauth2/callback')
    oauth2_authorization_base_url = fields.Char("Authorization Base URL", required=True, default='https://appcenter.intuit.com/connect/oauth2')
    token_url = fields.Char("Token URL", required=True, default='https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer')
    scope = fields.Selection([
                                ('com.intuit.quickbooks.accounting', 'Accounting'),
                                ('com.intuit.quickbooks.payment', 'Payment'), 
                                ('all', 'All')], 
                                string='Scope', default='com.intuit.quickbooks.accounting')
    token_type = fields.Char(string='Token Type', help='Identifies the type of token returned. At this time, this field will always have the value Bearer')
    x_refresh_token_expires_in = fields.Char(string='X Refresh Token Expires In ', help='The remaining lifetime, in seconds, for the connection, after which time the user must re-grant access, See refresh_token policy for details.')
    refresh_token = fields.Char(string='Refresh Token', help='A token used when refreshing the access token.')
    access_token = fields.Char(string='Access Token', help='The token that must be used to access the QuickBooks API.')
    expires_in = fields.Char(string='Expires In', help='The remaining lifetime of the access token in seconds. The value always returned is 3600 seconds (one hour). Use the refresh token to get a fresh one')
    expires_at = fields.Char(string='Expires At', help='The remaining lifetime of the access token in seconds. The value always returned is 3600 seconds (one hour). Use the refresh token to get a fresh one. See Refreshing the access token for further information.')
    token = fields.Char(string='Token', help='The token that must be used to access the QuickBooks API.')
    o2_auth_url = fields.Char("Authorized Url")
    o2_go_to = fields.Char("Go to link")

    # Two step oauth2 authorization 
    @api.multi
    def qb_authorization_o2_step1(self):
        if self.scope == 'all':
            scope = ['com.intuit.quickbooks.accounting',
                    'com.intuit.quickbooks.payment',
                    'openid',
                    'profile',
                    'email',
                    'phone',
                    'address']
        elif self.scope == 'com.intuit.quickbooks.accounting':
            scope = self.scope
        elif self.scope == 'com.intuit.quickbooks.payment':
            scope = self.scope
        qbo = OAuth2Session(self.client_key, scope=scope, redirect_uri=self.redirect_uri)
        authorization_url, state = qbo.authorization_url(self.oauth2_authorization_base_url)
        print 'Please go here and authorize,', authorization_url
        self.write({'o2_go_to': authorization_url,
                    'o2_auth_url': self.o2_auth_url,})

    @api.multi
    def qb_authorization_o2_step2(self):
        if self.scope == 'all':
            scope = ['com.intuit.quickbooks.accounting',
                    'com.intuit.quickbooks.payment',
                    'openid',
                    'profile',
                    'email',
                    'phone',
                    'address']
        elif self.scope == 'com.intuit.quickbooks.accounting':
            scope = self.scope
        elif self.scope == 'com.intuit.quickbooks.payment':
            scope = self.scope
        qbo = OAuth2Session(self.client_key, scope=scope, redirect_uri=self.redirect_uri)
        redirect_response = self.o2_auth_url
        fetch_toke = qbo.fetch_token(self.token_url, client_secret=self.client_secret,
         authorization_response=redirect_response)
        print fetch_toke
        self.write({'token_type':fetch_toke.get('token_type'),
                'x_refresh_token_expires_in':fetch_toke.get('x_refresh_token_expires_in'),
                'refresh_token':fetch_toke.get('refresh_token'),
                'access_token':fetch_toke.get('access_token'),
                'expires_in':fetch_toke.get('expires_in'),
                'expires_at':fetch_toke.get('expires_at')})
        self.write({'token':fetch_toke})
        con_url = self.location+self.company_id+'/customer/1'
        r = qbo.get(con_url)
        print r.content

    @api.multi
    def qb_auth_o2_auto_step2(self, context):
        obj=self.env['qb.backend'].search([('id','=',context['id'])])
        if context['scope'] == 'all':
            scope = ['com.intuit.quickbooks.accounting',
                    'com.intuit.quickbooks.payment',
                    'openid', 'profile', 'email', 'phone', 'address']
        elif context['scope'] == 'com.intuit.quickbooks.accounting':
            scope = context['scope']
        elif context['scope'] == 'com.intuit.quickbooks.payment':
            scope = context['scope']
        qbo = OAuth2Session(context['client_key'], scope=scope, redirect_uri=context['redirect_uri'])
        redirect_response = context['o2_auth_url']
        fetch_toke = qbo.fetch_token(context['token_url'], client_secret=context['client_secret'],
         authorization_response=redirect_response)
        print fetch_toke
        obj.write({'token_type':fetch_toke.get('token_type'),
                'x_refresh_token_expires_in':fetch_toke.get('x_refresh_token_expires_in'),
                'refresh_token':fetch_toke.get('refresh_token'),
                'access_token':fetch_toke.get('access_token'),
                'expires_in':fetch_toke.get('expires_in'),
                'expires_at':fetch_toke.get('expires_at')})
        obj.write({'token':fetch_toke})
        con_url = context['location']+context['company_id']+'/customer/1'
        r = qbo.get(con_url)
        print r.content

    @api.multi
    def test_connection(self):
        """ Test backend connection """
        location = self.location
        cons_key = self.client_key
        sec_key = self.client_secret
        version = self.version
        verify_ssl = self.verify_ssl
        headerauth = OAuth2Session(cons_key)
        headers = {'Authorization': 'Bearer %s' %self.access_token, 'content-type': 'application/json', 'accept': 'application/json'}

        con_url = self.location+self.company_id+'/customer/1'
        re = headerauth.get(con_url, headers=headers)
        
        if re.status_code == 404:
            raise Warning(_("Enter Valid url"))
        print re.text
        val = re.json()

        print val
        msg = ''
        if 'errors' in re.json():
            msg = val['errors'][0]['message'] + '\n' + val['errors'][0]['code']
            raise Warning(_(msg))
        else:
            raise UserError(_("Connection Test Succeeded! Everything seems properly set up!"))

    @api.multi
    def refresh_connection(self):
        """ Refresh backend connection """
        headeroauth = OAuth2Session(self.client_key)
        auth = "Basic " + b64encode(self.client_key + ":" + self.client_secret)
        api_method = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
        headers = {
                    'authorization': auth,
                    'accept': 'application/json',
                    'content-type': 'application/x-www-form-urlencoded',
                }
        body = {
            'grant_type':'refresh_token',
            'refresh_token':self.refresh_token
        }
        fetch_toke = headeroauth.post(api_method, data=body, headers=headers)
        if fetch_toke.status_code == 200:
            keys = fetch_toke.json()
            self.write({'refresh_token':keys['refresh_token'],
                        'access_token':keys['access_token'],
                        'token_type':keys['token_type'],
                        'x_refresh_token_expires_in':keys['x_refresh_token_expires_in'],
                        'expires_in':keys['expires_in'],})
            self.write({'token':fetch_toke})
        print fetch_toke.content

    @api.multi
    def refresh_connection_action(self):
        """ Refresh backend connection """
        self = self.search([('type', '=', 'oauth2')])
        headeroauth = OAuth2Session(self.client_key)
        auth = "Basic " + b64encode(self.client_key + ":" + self.client_secret)
        api_method = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
        headers = {
                    'authorization': auth,
                    'accept': 'application/json',
                    'content-type': 'application/x-www-form-urlencoded',
                }
        body = {
            'grant_type':'refresh_token',
            'refresh_token':self.refresh_token
        }
        fetch_toke = headeroauth.post(api_method, data=body, headers=headers)
        if fetch_toke.status_code == 200:
            keys = fetch_toke.json()
            self.write({'refresh_token':keys['refresh_token'],
                        'access_token':keys['access_token'],
                        'token_type':keys['token_type'],
                        'x_refresh_token_expires_in':keys['x_refresh_token_expires_in'],
                        'expires_in':keys['expires_in'],})
            self.write({'token':fetch_toke})
        print fetch_toke.content

    @api.multi
    def qb_authorization(self):

        oauth = OAuth1Session(self.client_key, self.client_secret,
                              callback_uri='http://localhost:8069/web/auth/')
        request_response = oauth.fetch_request_token(self.request_token_url)
        self.write({'resource_owner_key': request_response.get('oauth_token')})
        self.write(
            {'resource_owner_secret': request_response.get('oauth_token_secret')})
        # 3. Redirect user to your provider implementation for authorization
        # Cut and paste the authorization_url and run it in a browser
        authorization_url = oauth.authorization_url(
            self.authorization_base_url)
        print 'Please go here and authorize,', authorization_url
        webbrowser.open(authorization_url)
        self.write({'go_to': authorization_url})
        # 4. Get the authorization verifier code from the callback url

        # redirect response is the complete callback_uri after you have
        # authorized access to a company

        # string_vals = request.httprequest.query_string

    @api.multi
    def qb_authorization_step2(self):

        oauth = OAuth1Session(self.client_key, self.client_secret,
                              self.resource_owner_key, self.resource_owner_secret)
        redirect_response = self.new_url
        d = oauth.parse_authorization_response(redirect_response)
        print d
        self.write({'company_id': d.get('realmId')})
        # 5. Fetch the access token
        # At this point, oauth session object already has the request token and
        # request token secret
        fetch_response = oauth.fetch_access_token(self.access_token_url)
        print fetch_response
        self.write({'resource_owner_key': fetch_response.get('oauth_token')})
        self.write(
            {'resource_owner_secret': fetch_response.get('oauth_token_secret')})

    # @api.multi
    # def import_data(self):
    #     for backend in self:
    #         job_uuid = backend.with_delay(priority=100).import_batch('nada.vehicle.make')

    #     return True

    @api.multi
    def get_environment(self, binding_model_name):
        self.ensure_one()
        return ConnectorEnvironment(self, binding_model_name)

    @api.multi
    @job(default_channel='root.quick')
    def import_batch(self, binding_model_name, filters=None):
        """ Prepare a batch import of records from CSV """
        self.ensure_one()
        connector_env = self.get_environment(binding_model_name)
        importer = connector_env.get_connector_unit(BatchImporter)
        importer.run(filters=filters)

    @api.multi
    @job(default_channel='root.quick')
    def import_record(self, binding_model_name, ext_id, force=False):
        """ Import a record from Models"""
        self.ensure_one()
        connector_env = self.get_environment(binding_model_name)
        importer = connector_env.get_connector_unit(WooImporter)
        importer.run(ext_id, force=force)

    # @api.multi
    # def export_invoice(self):

    #     session = ConnectorSession(self.env.cr, self.env.uid,
    #                                context=self.env.context)
    #     import_start_time = datetime.now()
    #     backend_id = self.id
    #     from_date = None
    #     export_expertise_inventory.delay(
    #         session, 'instructor.expertise', backend_id,
    #         {'from_date': from_date,
    #          'to_date': import_start_time}, priority=1)
    #     return True

    @api.multi
    def import_customer(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['res.partner'].with_delay(priority=1).customer_import_batch(
            model_name='res.partner', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )
        return True

    @api.multi
    def import_customers(self):
        """ Import categories from all websites """
        for backend in self:
            backend.import_customer()
        return True

    @api.multi
    def import_vendor(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['res.partner'].with_delay(priority=1).vendor_import_batch(
            model_name='res.partner', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )

        return True

    @api.multi
    def import_vendors(self):
        """ Import categories from all websites """
        for backend in self:
            backend.import_vendor()
        return True

    @api.multi
    def import_product(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['product.template'].with_delay(priority=1).Item_import_batch(
            model_name='product.template', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )

        return True

    @api.multi
    def import_products(self):
        """ Import categories from all websites """
        for backend in self:
            backend.import_product()
        return True

    @api.multi
    def import_sale(self):

        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['sale.order'].with_delay(priority=1).sale_import_batch(
            model_name='sale.order', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )

        return True

    @api.multi
    def import_sales(self):
        """ Import categories from all websites """
        for backend in self:
            backend.import_sale()
        return True

    @api.multi
    def import_purchase(self):

        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['purchase.order'].with_delay(priority=1).purchases_import_batch(
            model_name='purchase.order', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )

        return True

    @api.multi
    def import_purchases(self):
        """ Import categories from all websites """
        for backend in self:
            backend.import_purchase()
        return True

    @api.multi
    def import_account(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['account.account'].with_delay(priority=1).account_import_batch(
            model_name='account.account', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )

        return True

    @api.multi
    def import_accounts(self):
        """ Import categories from all websites """
        for backend in self:
            backend.import_account()
        return True

    @api.multi
    def import_invoice(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['account.invoice'].with_delay(priority=1).invoice_import_batch(
            model_name='account.invoice', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )
        return True

    @api.multi
    def import_invoices(self):
        """ Import categories from all websites """
        for backend in self:
            backend.import_invoice()
        return True

    @api.multi
    def import_term(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['account.payment.term'].with_delay(priority=1).term_import_batch(
            model_name='account.payment.term', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )
        return True

    @api.multi
    def import_terms(self):
        """ Import Terms From QBO """
        for backend in self:
            backend.import_term()
        return True

    @api.multi
    def import_payment_method(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['payment.acquirer'].with_delay(priority=1).PaymentMethod_import_batch(
            model_name='payment.acquirer', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )
        return True

    @api.multi
    def import_payment_methods(self):
        """ Import Payment Method From QBO """
        for backend in self:
            backend.import_payment_method()
        return True

    @api.multi
    def import_taxcode(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['account.tax'].with_delay(priority=1).tax_import_batch(
            model_name='account.tax', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )
        return True

    @api.multi
    def import_taxes(self):
        """ Import Tax Code From QBO """
        for backend in self:
            backend.import_taxcode()
        return True

    @api.multi
    def import_taxrate(self):
        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self.id
        from_date = None
        self.env['account.tax'].with_delay(priority=1).rate_import_batch(
            model_name='account.tax', backend_id=backend_id,
            filters={'from_date': from_date,
                     'to_date': import_start_time}
        )
        return True

    @api.multi
    def import_taxrates(self):
        """ Import Tax Code From QBO """
        for backend in self:
            backend.import_taxrate()
        return True

    @api.multi
    def export_customers(self):
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self
        from_date = None

        self.env['res.partner'].with_delay(
            priority=1).export_customer_inventory(
            backend_id)

        return True

    @api.multi
    def export_items(self):
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self
        from_date = None
        self.env['product.template'].with_delay(
            priority=1).export_item_inventory(
            backend_id)
        
        return True

    @api.multi
    def export_vendors(self):
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self
        from_date = None
        self.env['res.partner'].with_delay(
            priority=1).export_vendor_details(
            backend_id)

        return True

    @api.multi
    def export_sales(self):
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self
        from_date = None
        self.env['sale.order'].with_delay(
            priority=1).export_sale_details(backend_id)

        return True

    @api.multi
    def export_purchases(self):
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self
        from_date = None
        self.env['purchase.order'].with_delay(
            priority=1).export_purchase_details(
            backend_id)

        return True

    @api.multi
    def export_accounts(self):
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self
        from_date = None
        self.env['account.account'].with_delay(
            priority=1).export_account_details(backend_id)

        return True

    @api.multi
    def export_invoice(self):

        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self
        from_date = None
        self.env['account.invoice'].with_delay(
            priority=1).export_invoice_details(backend_id)

        return True

    @api.multi
    def export_payment_methods(self):

        session = ConnectorEnvironment(self,  self._name)
        import_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        backend_id = self
        from_date = None
        self.env['payment.acquirer'].with_delay(
            priority=1).export_PaymentMethod_details(backend_id)

        return True
