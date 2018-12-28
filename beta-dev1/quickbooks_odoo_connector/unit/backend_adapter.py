# -*- coding: utf-8 -*-
#
#
#    TechSpawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY TechSpawn(<http://www.TechSpawn.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import socket
import json
import logging
import xmlrpclib
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth2Session
import requests
from requests_oauthlib import OAuth1, OAuth2
from odoo.addons.connector.unit.backend_adapter import CRUDAdapter
from odoo.addons.connector.exception import (NetworkRetryableError,
                                                RetryableJobError)
from datetime import datetime
import json


from odoo.exceptions import Warning
from odoo.tools.translate import _


_logger = logging.getLogger(__name__)

recorder = {}


def call_to_key(method, arguments):
    """ Used to 'freeze' the method and arguments of a call to Quickbook
    so they can be hashable; they will be stored in a dict.

    Used in both the recorder and the tests.
    """
    def freeze(arg):
        if isinstance(arg, dict):
            items = dict((key, freeze(value)) for key, value
                         in arg.iteritems())
            return frozenset(items.iteritems())
        elif isinstance(arg, list):
            return tuple([freeze(item) for item in arg])
        else:
            return arg

    new_args = []
    for arg in arguments:
        new_args.append(freeze(arg))
    return (method, tuple(new_args))


def record(method, arguments, result):
    """ Utility function which can be used to record test data
    during synchronisations. Call it from WooCRUDAdapter._call

    Then ``output_recorder`` can be used to write the data recorded
    to a file.
    """
    recorder[call_to_key(method, arguments)] = result


def output_recorder(filename):
    import pprint
    with open(filename, 'w') as f:
        pprint.pprint(recorder, f)
    _logger.debug('recorder written to file %s', filename)


class WooLocation(object):

    def __init__(self, location, client_key, client_secret, resource_owner_key, resource_owner_secret, company_id, asset_account_ref, access_token, type):
        self._location = location
        self.client_key = client_key
        self.client_secret = client_secret
        self.resource_owner_key = resource_owner_key
        self.resource_owner_secret = resource_owner_secret
        self.company_id = company_id
        self.asset_account_ref = asset_account_ref
        self.access_token = access_token
        self.type = type
    @property
    def location(self):
        location = self._location
        return location


class WooCRUDAdapter(CRUDAdapter):

    """ External Records Adapter for woo """

    def __init__(self, connector_env):
        """

        :param connector_env: current environment (backend, session, ...)
        :type connector_env: :class:`connector.connector.ConnectorEnvironment`
        """
        super(WooCRUDAdapter, self).__init__(connector_env)
        backend = self.backend_record
        quick = WooLocation(
            backend.location,
            backend.client_key,
            backend.client_secret,
            backend.resource_owner_key,
            backend.resource_owner_secret,
            backend.company_id,
            backend.asset_account_ref,
            backend.access_token,
            backend.type)
        self.quick = quick

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids """
        raise NotImplementedError

    def read(self, id, attributes=None):
        """ Returns the information of a record """
        raise NotImplementedError

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        raise NotImplementedError

    def create(self, data):
        """ Create a record on the external system """
        raise NotImplementedError

    def write(self, id, data):
        """ Update records on the external system """
        raise NotImplementedError

    def delete(self, id):
        """ Delete a record on the external system """
        raise NotImplementedError

    def _call(self, method, arguments):
        if 'vendor' in arguments:
            method = method.replace('customer', 'vendor')

        if 'taxrate' in arguments:
            method = method.replace('taxcode', 'taxrate')
        print method
        if self.quick.type == 'oauth1':
            try:
                _logger.debug("Start calling booking api %s", method)
                headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                     self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                     signature_type='auth_header')
                headers = {
                    'content-type': 'application/json', 'accept': 'application/json'}
                if method == '/query?query=select%20ID%20from%20customer' or \
                        method == '/query?query=select%20%2A%20from%20vendor' or \
                        method == '/query?query=select%20from%20item' or \
                        method == '/query?query=select%20from%20purchaseorder'or \
                        method == '/query?query=select%20from%20salesreceipt' or \
                        method == '/query?query=select%20from%20account' or \
                        method == '/query?query=select%20from%20term' or \
                        method == '/query?query=select%20ID%20from%20taxrate' or \
                        method == '/query?query=select%20from%20taxcode' or \
                        method == '/query?query=select%20id%20from%20paymentmethod' or \
                        method == '/query?query=select%20from%20invoice':
                    data = requests.get(self.quick.location+self.quick.company_id +
                                        method+'&minorversion=4', auth=headeroauth, headers=headers)
                else:
                    data = requests.get(self.quick.location+self.quick.company_id +
                                        '/'+method+'?&minorversion=4', auth=headeroauth, headers=headers)
                # https://sandbox-quickbooks.api.intuit.com/v3/company/123145714682589/query?query=select%20ID%20from%20customer&minorversion=4
                if data:
                    if isinstance(arguments, list):
                        while arguments and arguments[-1] is None:
                            arguments.pop()
                    start = datetime.now()

                    try:
                        if 'false' or 'true' or 'null'in data.content:
                            result = data.content.replace(
                                'false', 'False')
                            result = result.replace('true', 'True')
                            result = result.replace('null', 'False')
                            print result
                            result = eval(result)
                        else:
                            result = eval(data.content)
                    except:
                        _logger.error("api.call(%s, %s) failed", method, arguments)
                        raise
                    else:
                        _logger.debug("api.call(%s, %s) returned %s in %s seconds",
                                      method, arguments, result,
                                      (datetime.now() - start).seconds)
                    return result
            except (socket.gaierror, socket.error, socket.timeout) as err:
                raise NetworkRetryableError(
                    'A network error caused the failure of the job: '
                    '%s' % err)
            except xmlrpclib.ProtocolError as err:
                if err.errcode in [502,   # Bad gateway
                                   503,   # Service unavailable
                                   504]:  # Gateway timeout
                    raise RetryableJobError(
                        'A protocol error caused the failure of the job:\n'
                        'URL: %s\n'
                        'HTTP/HTTPS headers: %s\n'
                        'Error code: %d\n'
                        'Error message: %s\n' %
                        (err.url, err.headers, err.errcode, err.errmsg))
                else:
                    raise
        else:
            try:
                _logger.debug("Start calling booking api %s", method)
                headeroauth = OAuth2Session(self.quick.client_key)
                headers = {'Authorization': 'Bearer %s' %self.quick.access_token, 'content-type': 'application/json', 'accept': 'application/json'}

                if method == '/query?query=select%20ID%20from%20customer' or \
                        method == '/query?query=select%20%2A%20from%20vendor' or \
                        method == '/query?query=select%20from%20item' or \
                        method == '/query?query=select%20from%20purchaseorder'or \
                        method == '/query?query=select%20from%20salesreceipt' or \
                        method == '/query?query=select%20from%20account' or \
                        method == '/query?query=select%20from%20term' or \
                        method == '/query?query=select%20ID%20from%20taxrate' or \
                        method == '/query?query=select%20from%20taxcode' or \
                        method == '/query?query=select%20from%20payment' or \
                        method == '/query?query=select%20id%20from%20paymentmethod' or \
                        method == '/query?query=select%20from%20invoice':
                    data = headeroauth.get(self.quick.location+self.quick.company_id +
                                        method+'%20STARTPOSITION%20'+str(arguments[0]['count'])+'%20MAXRESULTS%20' + str(300)+'&minorversion=4', headers=headers)
                else:
                    data = headeroauth.get(self.quick.location+self.quick.company_id +
                                        '/'+method+'?&minorversion=4', headers=headers)

                # https://sandbox-quickbooks.api.intuit.com/v3/company/123145714682589/query?query=select%20ID%20from%20customer&minorversion=4
                if data:
                    if isinstance(arguments, list):
                        while arguments and arguments[-1] is None:
                            arguments.pop()
                    start = datetime.now()

                    try:
                        if 'false' or 'true' or 'null'in data.content:
                            result = data.content.replace(
                                'false', 'False')
                            result = result.replace('true', 'True')
                            result = result.replace('null', 'False')
                            print result
                            result = eval(result)
                        else:
                            result = eval(data.content)
                    except:
                        _logger.error("api.call(%s, %s) failed", method, arguments)
                        raise
                    else:
                        _logger.debug("api.call(%s, %s) returned %s in %s seconds",
                                      method, arguments, result,
                                      (datetime.now() - start).seconds)
                    return result
            except (socket.gaierror, socket.error, socket.timeout) as err:
                raise NetworkRetryableError(
                    'A network error caused the failure of the job: '
                    '%s' % err)
            except xmlrpclib.ProtocolError as err:
                if err.errcode in [502,   # Bad gateway
                                   503,   # Service unavailable
                                   504]:  # Gateway timeout
                    raise RetryableJobError(
                        'A protocol error caused the failure of the job:\n'
                        'URL: %s\n'
                        'HTTP/HTTPS headers: %s\n'
                        'Error code: %d\n'
                        'Error message: %s\n' %
                        (err.url, err.headers, err.errcode, err.errmsg))
                else:
                    raise


    def _call_invoice_old(self, method, arguments):
         # _logger.debug("Start calling student api %s", method)
        headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                             self.quick.resource_owner_key, self.quick.resource_owner_secret,
                             signature_type='auth_header')

        if method == 'update_invoice':
            if headeroauth:
                if not arguments[0]:

                    # api_method =
                    # self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/invoice?minorversion=4'
                else:
                    # api_method =
                    # self.quick.location+self.quick.company_id+'/invoice/' +
                    # str(arguments[0])+'?minorversion=4'
                    api_method = self.quick.location+self.quick.company_id + \
                        '/invoice?operation=update&minorversion=4'
                    # api_method =
                    # self.quick.location+self.quick.company_id+'/invoice/' +
                    # str(arguments[0])+'?operation=update&minorversion=4'
                if not arguments[1]['invoice'].partner_id.quickbook_id:
                    api_method_customer = self.quick.location + \
                        self.quick.company_id+'/customer?minorversion=4'
                # else:
                #     api_method_customer = self.quick.location+self.quick.company_id+'/customer/'+ str(arguments[0])+'?minorversion=4'
                    # result_dict1 = {"DisplayName":
                    # arguments[1]['invoice'].partner_id.name,}
                    result_dict1 = {
                        "BillAddr": {
                            "Line1": arguments[1]['invoice'].partner_id.street or None,
                            "City": arguments[1]['invoice'].partner_id.city or None,
                            "Country": arguments[1]['invoice'].partner_id.country_id.name or None,
                            # "CountrySubDivisionCode": "CA",
                            "PostalCode": arguments[1]['invoice'].partner_id.zip or None,
                        },
                        # "Notes": arguments[1]['invoice'].partner_id.comment,
                        "Title": arguments[1]['invoice'].partner_id.title.name or None,
                        # "GivenName": "James",
                        # "MiddleName": "B",
                        # "FamilyName": "King",
                        # "Suffix": "Jr",
                        # "FullyQualifiedName": arguments[1]['invoice'].partner_id.name,
                        "CompanyName": arguments[1]['invoice'].partner_id.name or None,
                        "DisplayName": arguments[1]['invoice'].partner_id.name or None,
                        "PrimaryPhone": {
                            "FreeFormNumber": arguments[1]['invoice'].partner_id.phone or None,
                        },
                        "PrimaryEmailAddr": {
                            "Address": arguments[1]['invoice'].partner_id.email or None,
                        },
                        "Mobile": {
                            "FreeFormNumber": arguments[1]['invoice'].partner_id.mobile or None,
                        },
                        "WebAddr": {
                            "URI": arguments[1]['invoice'].partner_id.website or None,
                        }

                    }
                    headers = {
                        'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method_customer, data=json.dumps(
                        result_dict1), auth=headeroauth, headers=headers)

                    # r1=requests.post(api_method ,data=json.dumps(wp_user_id),
                    # auth=headeroauth, headers=headers)
                    

                    

                    if r1.status_code == 200:
                        # result = r.content.replace('false', 'False')
                        # result = result.replace('true', 'True')
                        # result = result.replace('null', 'False')
                        arguments[1]['invoice'].partner_id.write(
                            {'quickbook_id': r1.json()['Customer']['Id']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        msg = r1.json()['Fault']['Error']
                        raise Warning(msg)
##########################################################################
                # result_dict1 = {
                #       "Customer": {
                #         "Taxable": false,
                #         "BillAddr": {
                #           "Id": "11",
                #           "Line1": "1045 Main St.",
                #           "City": "Half Moon Bay",
                #           "CountrySubDivisionCode": "CA",
                #           "PostalCode": "94213",
                #           "Lat": "37.4559621",
                #           "Long": "-122.429939"
                #         },
                #         "ShipAddr": {
                #           "Id": "11",
                #           "Line1": "1045 Main St.",
                #           "City": "Half Moon Bay",
                #           "CountrySubDivisionCode": "CA",
                #           "PostalCode": "94213",
                #           "Lat": "37.4559621",
                #           "Long": "-122.429939"
                #         },
                #         "Job": false,
                #         "BillWithParent": false,
                #         "Balance": 0,
                #         "BalanceWithJobs": 0,
                #         "CurrencyRef": {
                #           "value": "USD",
                #           "name": "United States Dollar"
                #         },
                #         "PreferredDeliveryMethod": "Print",
                #         "domain": "QBO",
                #         "sparse": false,
                #         "Id": "11",
                #         "SyncToken": "0",
                #         "MetaData": {
                #           "CreateTime": "2016-09-23T17:04:02-07:00",
                #           "LastUpdatedTime": "2016-09-23T17:04:02-07:00"
                #         },
                #         "GivenName": "Lisa",
                #         "FamilyName": "Gevelber",
                #         "FullyQualifiedName": "Gevelber Photography",
                #         "CompanyName": "Gevelber Photography",
                #         "DisplayName": "Gevelber Photography",
                #         "PrintOnCheckName": "Gevelber Photography",
                #         "Active": true,
                #         "PrimaryPhone": {
                #           "FreeFormNumber": "(415) 222-4345"
                #         },
                #         "PrimaryEmailAddr": {
                #           "Address": "Photography@intuit.com"
                #         },
                #         "WebAddr": {
                #           "URI": "http://gevelberphotography.com"
                #         }
                #       },
                #       "time": "2016-11-02T22:05:48.938-07:00"
                #     }
                # if not arguments[1]['invoice'].invoice_line.account_id.quickbook_id:
##########################################################################
                temp_array = []
                for invoice_line in arguments[1]['invoice'].invoice_line_ids:
                    api_method_acc = self.quick.location + \
                        self.quick.company_id+'/account?minorversion=4'
                    if not invoice_line.product_id.property_account_income_id.quickbook_id:

                        acc_dict = {
                            "AccountType": "Income",
                            "AccountSubType": "SalesOfProductIncome",
                            "Name": invoice_line.product_id.property_account_income_id.name
                        }
                        headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                        r = requests.post(
                            api_method_acc, data=json.dumps(acc_dict), auth=headeroauth, headers=headers)
                        if r.status_code == 200:
                            invoice_line.product_id.property_account_income_id.write(
                                {'quickbook_id': r.json()['Account']['Id']})
                        if r.status_code == 500 or r.status_code == 400:
                            msg = r.json()['Fault']['Error']
                            raise Warning(msg)
                    if not invoice_line.product_id.property_account_expense_id.quickbook_id:

                        acc_dict = {
                            "AccountType": "Cost of Goods Sold",
                            "AccountSubType": "SuppliesMaterialsCogs",
                            "Name": invoice_line.product_id.property_account_expense_id.name
                        }
                        headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                        r = requests.post(
                            api_method_acc, data=json.dumps(acc_dict), auth=headeroauth, headers=headers)
                        if r.status_code == 200:
                            invoice_line.product_id.property_account_expense_id.write(
                                {'quickbook_id': r.json()['Account']['Id']})
                        if r.status_code == 500 or r.status_code == 400:
                            msg = r.json()['Fault']['Error']
                            raise Warning(msg)
                    if not self.quick.asset_account_ref.quickbook_id:

                        acc_dict = {
                            "AccountType": "Other Current Asset",
                            "AccountSubType": "Inventory",
                            "Name": self.quick.asset_account_ref.name
                        }
                        headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                        r = requests.post(
                            api_method_acc, data=json.dumps(acc_dict), auth=headeroauth, headers=headers)
                        if r.status_code == 200:
                            self.quick.asset_account_ref.write(
                                {'quickbook_id': r.json()['Account']['Id']})
                        if r.status_code == 500 or r.status_code == 400:
                            msg = r.json()['Fault']['Error']
                            raise Warning(msg)

    ##########################################################################
                    if not invoice_line.product_id.quickbook_id:
                        api_method_item = self.quick.location + \
                            self.quick.company_id+'/item?minorversion=4'
                        asset_value = self.quick.asset_account_ref.quickbook_id
                        # asset_name = self.quick.asset_account_ref.name
                        product_type = str(invoice_line.product_id.type)
                        if product_type == 'product':
                            type_product = "Inventory"
                            track_all = True
                        elif product_type == 'consu':
                            type_product = "NonInventory"
                            track_all = False
                        elif product_type == 'service':
                            type_product = 'Service'
                            track_all = False

                        result_dict2 = {
                            # "Item": {
                            "Name": invoice_line.product_id.name or None,
                            "Active": invoice_line.product_id.active ,
                            "Description": invoice_line.product_id.description or None,
                            # "FullyQualifiedName": "Garden Supplies",
                            # "Taxable": false,
                            "UnitPrice": invoice_line.product_id.list_price or None,
                            "Type": type_product,
                            "IncomeAccountRef": {
                                "value": invoice_line.product_id.property_account_income_id.quickbook_id or None,
                                # "name": arguments[1]['invoice'].invoice_line.product_id.property_account_income.name
                            },
                            # # "PurchaseCost": arguments[1]['invoice'].invoice_line.product_id.standard_price,
                            "ExpenseAccountRef": {
                                "value": invoice_line.product_id.property_account_expense_id.quickbook_id or None,
                                # "name": arguments[1]['invoice'].invoice_line.product_id.property_account_expense.name
                            },
                            "AssetAccountRef": {
                                "value": asset_value or None,
                                # "name": asset_name
                            },
                            "TrackQtyOnHand": track_all,
                            "QtyOnHand": invoice_line.product_id.qty_available,
                            "InvStartDate": datetime.now().strftime('%Y-%m-%d'),
                            # "domain": "QBO",
                            # "sparse": false,
                            # "Id": "19",
                            # "SyncToken": "0",
                            # "MetaData": {
                            #   "CreateTime": "2016-11-02T23:21:30-07:00",
                            #   "LastUpdatedTime": "2016-11-02T23:21:30-07:00"
                            # }
                            # }
                            # "time": "2016-11-02T23:21:30.534-07:00"
                        }
                        headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                        r2 = requests.post(api_method_item, data=json.dumps(
                            result_dict2), auth=headeroauth, headers=headers)
                        

                        return_dict2 = r2.content

                        print r2.status_code

                        if r2.status_code == 200:
                            # result = r.content.replace('false', 'False')
                            # result = result.replace('true', 'True')
                            # result = result.replace('null', 'False')
                            invoice_line.product_id.write(
                                {'quickbook_id': r2.json()['Item']['Id']})
                        if r2.status_code == 500 or r2.status_code == 400:
                            msg = r2.json()['Fault']['Error']
                            raise Warning(msg)
##########################################################################
                # temp_array = []
                # for invoice_line in arguments[1]['invoice'].invoice_line:
                    temp = {
                        # "TxnDate": arguments[1]['invoice'].date_invoice,

                        "Description": invoice_line.name,
                        "Amount": invoice_line.price_subtotal,
                        "DetailType": "SalesItemLineDetail",
                        "SalesItemLineDetail": {
                            "ItemRef": {
                                      "value": invoice_line.product_id.quickbook_id,
                                      # "name": arguments[1]['invoice'].invoice_line.product_id.name,
                            },
                            "UnitPrice": invoice_line.price_unit,
                            "Qty": invoice_line.quantity,
                        }


                    }
                    temp_array.append(temp)
                result_dict = {
                    # "TxnDate": arguments[1]['invoice'].date_invoice,
                    "Line": temp_array,
                    "CustomerRef": {
                        "value": arguments[1]['invoice'].partner_id.quickbook_id,
                    },

                    "DueDate": arguments[1]['invoice'].date_due,
                    # "TotalAmt": arguments[1]['invoice'].amount_total,
                    "BillEmail": {
                        "Address": arguments[1]['invoice'].partner_id.email
                    },
                }

                if api_method == self.quick.location+self.quick.company_id+'/invoice?operation=update&minorversion=4':
                    ris = self.quick.location+self.quick.company_id + \
                        '/invoice/' + str(arguments[0])+'?minorversion=4'
                    headers = {'accept': 'application/json'}
                    r = requests.get(ris, auth=headeroauth, headers=headers)
                    
                    result_dict.update({
                        "sparse": r.json()['Invoice']['sparse'],
                        "Id": r.json()['Invoice']['Id'],
                        "SyncToken": r.json()['Invoice']['SyncToken'], })
                else:
                    result_dict

                headers = {
                    'content-type': 'application/json', 'accept': 'application/json'}
                r = requests.post(
                    api_method, data=json.dumps(result_dict), auth=headeroauth, headers=headers)


                # return_dict = r.content


                if r.status_code == 200:
                    # result = r.content.replace('false', 'False')
                    # result = result.replace('true', 'True')
                    # result = result.replace('null', 'False')
                    arguments[1]['invoice'].write(
                        {'quickbook_id': r.json()['Invoice']['Id']})

                if r.status_code == 201:
                    arguments[1]['invoice'].write(
                        {'quickbook_id': r.json()['Invoice']['Id']})
                if r.status_code == 500 or r.status_code == 400:
                    msg = r.json()['Fault']['Error']
                    raise Warning(msg)
                if r.status_code == 404:
                    arguments[1]['invoice'].unlink()
                # if isinstance(return_dict, dict):
                #     arguments[1]['invoice'].write({'quickbook_id':return_dict['customer']['id'],'wp_user_id':return_dict['customer']['wp_user_id']})


    def _call_customer(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_customer':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/customer?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/customer?operation=update&minorversion=4'

                result_dict = {
                        "BillAddr": {
                            "Line1": arguments[1]['customer'].street or None,
                            "City": arguments[1]['customer'].city or None,
                            "Country": arguments[1]['customer'].country_id.name or None,
                            # "CountrySubDivisionCode": "CA",
                            "PostalCode": arguments[1]['customer'].zip or None,
                        },
                        # "Notes": arguments[1]['invoice'].partner_id.comment,
                        "Title": arguments[1]['customer'].title.name or None,
                        "GivenName": arguments[1]['customer'].first_name or None,
                        # "MiddleName": arguments[1]['customer'],
                        "FamilyName": arguments[1]['customer'].last_name or None,
                        # "Suffix": "Jr",
                        # "FullyQualifiedName": arguments[1]['invoice'].partner_id.name,
                        "CompanyName": arguments[1]['customer'].company_name or None,
                        "DisplayName": arguments[1]['customer'].name,
                        "PrimaryPhone": {
                            "FreeFormNumber": arguments[1]['customer'].phone or None,
                        },
                        "PrimaryEmailAddr": {
                            "Address": arguments[1]['customer'].email or None,
                        },
                        "Mobile": {
                            "FreeFormNumber": arguments[1]['customer'].mobile or None,
                        },
                        "WebAddr": {
                            "URI": arguments[1]['customer'].website or None,
                        },
                        "SalesTermRef":{
                            "value": arguments[1]['customer'].property_payment_term_id.quickbook_id or None,
                        },

                    }
                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/customer?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/customer/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Customer']['sparse'],
                                "Id": r.json()['Customer']['Id'],
                                "SyncToken": r.json()['Customer']['SyncToken'], })
                        # _logger.debug("Start calling student api %s %s %s ", method, r.status_code, r.text)
                    else:
                        result_dict

                    headers = {'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export Customer api %s %s %s",
                             api_method, r1.status_code, r1.json())
                                        

                    if r1.status_code == 200:
                        arguments[1]['customer'].write(
                                {'quickbook_id': r1.json()['Customer']['Id']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/customer?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/customer/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Customer']['sparse'],
                                "Id": r.json()['Customer']['Id'],
                                "SyncToken": r.json()['Customer']['SyncToken'], })
                        # _logger.debug("Start calling student api %s %s %s ", method, r.status_code, r.text)
                    else:
                        result_dict

                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export Customer api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    
                                       

                    if r1.status_code == 200:
                        arguments[1]['customer'].write(
                                {'quickbook_id': r1.json()['Customer']['Id']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_vendor(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)
        if method == 'update_vendor':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/vendor?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/vendor?operation=update&minorversion=4'

                result_dict = {
                        "BillAddr": {
                            "Line1": arguments[1]['vendor'].street or None,
                            "City": arguments[1]['vendor'].city or None,
                            "Country": arguments[1]['vendor'].country_id.name or None,
                            # "CountrySubDivisionCode": "CA",
                            "PostalCode": arguments[1]['vendor'].zip or None,
                        },
                        # "Notes": arguments[1]['invoice'].partner_id.comment,
                        "Title": arguments[1]['vendor'].title.name or None,
                        "GivenName": arguments[1]['vendor'].first_name,
                        # "MiddleName": "B",
                        "FamilyName": arguments[1]['vendor'].last_name,
                        # "Suffix": "Jr",
                        # "FullyQualifiedName": arguments[1]['invoice'].partner_id.name,
                        "CompanyName": arguments[1]['vendor'].company_name or None,
                        "DisplayName": arguments[1]['vendor'].name,
                        "PrimaryPhone": {
                            "FreeFormNumber": arguments[1]['vendor'].phone or None,
                        },
                        "PrimaryEmailAddr": {
                            "Address": arguments[1]['vendor'].email or None,
                        },
                        "Mobile": {
                            "FreeFormNumber": arguments[1]['vendor'].mobile or None,
                        },
                        "WebAddr": {
                            "URI": arguments[1]['vendor'].website or None,
                        },
                        "TermRef": {
                            "value": arguments[1]['vendor'].property_supplier_payment_term_id.quickbook_id or None,
                        },

                    }
                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/vendor?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/vendor/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Vendor']['sparse'],
                                "Id": r.json()['Vendor']['Id'],
                                "SyncToken": r.json()['Vendor']['SyncToken'], })
                    else:
                        result_dict

                    headers = {'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export Vendor api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    
                                        

                    if r1.status_code == 200:
                        arguments[1]['vendor'].write(
                                {'quickbook_id': r1.json()['Vendor']['Id']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/vendor?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/vendor/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Vendor']['sparse'],
                                "Id": r.json()['Vendor']['Id'],
                                "SyncToken": r.json()['Vendor']['SyncToken'], })
                    else:
                        result_dict

                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export Vendor api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    
                    if r1.status_code == 200:
                        arguments[1]['vendor'].write(
                                {'quickbook_id': r1.json()['Vendor']['Id']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_item(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret, self.quick.resource_owner_key,
                                self.quick.resource_owner_secret, signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_item':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + self.quick.company_id+'/item?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/item?operation=update&minorversion=4'

                if self.quick.asset_account_ref.quickbook_id:
                    asset_value = self.quick.asset_account_ref.quickbook_id
                else:
                    asset_value = None
                        # asset_name = self.quick.asset_account_ref.name
                product_type = str(arguments[1]['item'].type)
                if product_type == 'product':
                    type_product = "Inventory"
                    track_all = True
                elif product_type == 'consu':
                    type_product = "NonInventory"
                    track_all = False
                elif product_type == 'service':
                    type_product = 'Service'
                    track_all = False

                result_dict = {
                        # "Item": {
                            "Name": arguments[1]['item'].name or None,
                            "Description": arguments[1]['item'].description_sale or None,
                            "Active": arguments[1]['item'].active,
                            # "FullyQualifiedName": "Garden Supplies",
                            # "Taxable": false,
                            "UnitPrice": arguments[1]['item'].list_price or None,
                            "Type": type_product,
                            "IncomeAccountRef": {
                                "value": arguments[1]['item'].property_account_income_id.quickbook_id or None,

                                # "name": arguments[1]['invoice'].invoice_line.product_id.property_account_income.name
                            },
                            "PurchaseDesc": arguments[1]['item'].description_purchase or None,
                            "PurchaseCost": arguments[1]['item'].standard_price,
                            "ExpenseAccountRef": {
                                "value": arguments[1]['item'].property_account_expense_id.quickbook_id or None,
                                # "name": arguments[1]['invoice'].invoice_line.product_id.property_account_expense.name
                            },
                            "AssetAccountRef": {
                                "value": asset_value or None,
                                # "name": asset_name
                            },
                            "TrackQtyOnHand": track_all,
                            "QtyOnHand": arguments[1]['item'].qty_available or None,
                            "InvStartDate": arguments[1]['item'].create_date,
                            # 'PurchaseTaxIncluded':arguments[1]['item'].purchase_tax_included,
                            # 'SalesTaxIncluded':arguments[1]['item'].sales_tax_included,
                            # 'AbatementRate' :arguments[1]['item'].abatement_rate,
                            # 'ReverseChargeRate' :arguments[1]['item'].reverse_charge_rate,
                            # 'Taxable':arguments[1]['item'].taxable,
                            'SalesTaxCodeRef':{
                                "value": arguments[1]['item'].taxes_id.quickbook_id or None,
                                # "name": asset_name
                            },
                            # 'PurchaseTaxCodeRef' :arguments[1]['item'].supplier_taxes_id.quickbook_id,
                        # }
                    }
                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/item?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                            '/item/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                            "sparse": r.json()['Item']['sparse'],
                            "Id": r.json()['Item']['Id'],
                            "SyncToken": r.json()['Item']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export Product api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    

                    if r1.status_code == 200:
                        arguments[1]['item'].write(
                                {'quickbook_id': r1.json()['Item']['Id']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                if self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/item?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                            '/item/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                            "sparse": r.json()['Item']['sparse'],
                            "Id": r.json()['Item']['Id'],
                            "SyncToken": r.json()['Item']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export Product api %s %s %s",
                             api_method, r1.status_code, r1.json())


                    if r1.status_code == 200:
                        arguments[1]['item'].write(
                                {'quickbook_id': r1.json()['Item']['Id']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_attachments(self, method, arguments):
        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_item_image':
            if headeroauth:
                if not arguments[0]:

                    api_method = self.quick.location + \
                        self.quick.company_id+'/upload?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/upload?operation=update&minorversion=4'
                result_dict = {
                                'AttachableRef': [{
                                    'IncludeOnSend': False,
                                    'EntityRef': {
                                        'type': 'Item',
                                        'value': arguments[1]['image'].quickbook_id
                                    }
                                }],
                                'ContentType': 'image/jpeg',
                                # + arguments[1]['image'].image,
                                'FileName': arguments[1]['image'].image_name,
                        }
                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/upload?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/attachable/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Attachable']['sparse'],
                                "Id": r.json()['Attachable']['Id'],
                                "SyncToken": r.json()['Attachable']['SyncToken'], })
                    else:
                        result_dict
                    headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export Attachable api %s %s %s",
                             api_method, r1.status_code, r1.json())
                                        

                    if r1.status_code == 200:
                        arguments[1]['image'].write(
                                {'image_id': r1.json()['Attachable']['Id']})

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/upload?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/attachable/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Attachable']['sparse'],
                                "Id": r.json()['Attachable']['Id'],
                                "SyncToken": r.json()['Attachable']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export Attachable api %s %s %s",
                             api_method, r1.status_code, r1.json())


                    if r1.status_code == 200:
                        arguments[1]['image'].write(
                                {'image_id': r1.json()['Attachable']['Id']})

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_salesreceipts(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_salesreceipts':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/salesreceipt?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/salesreceipt?operation=update&minorversion=4'

                temp_array = []
                if arguments[1]['sale'].order_line:
                    for order_line in arguments[1]['sale'].order_line:
                        product_template_id = self.env['product.template'].search(
                            [('name', '=', order_line.product_id.name)])
                        if order_line.tax_id:
                            taxcoderef = "TAX"
                        else:
                            taxcoderef = "NON"
                        temp = {
                                "Description": order_line.name or None,
                                "Amount": order_line.price_subtotal or None,
                                "DetailType": "SalesItemLineDetail",
                                "SalesItemLineDetail": {
                                    "ItemRef": {
                                              "value": product_template_id.quickbook_id or None,
                                              # "name": order_line.product_id..invoice_line.product_id.name,
                                    },
                                    "UnitPrice": order_line.price_unit or None,
                                    "Qty": order_line.product_uom_qty or None,
                                    "TaxCodeRef": {
                                            "value": taxcoderef,
                                        },
                                },
                                "LineNum": order_line.sequence,
                                "Id": order_line.quickbook_id or None,
                            }
                        temp_array.append(temp)

                result_dict = {
                            "Line": temp_array,
                            "CustomerRef": {
                                "value": arguments[1]['sale'].partner_id.quickbook_id,
                            },

                            "TxnDate": arguments[1]['sale'].date_order,
                            # "TotalAmt": arguments[1]['invoice'].amount_total,
                            # "BillEmail": {
                            #     "Address": arguments[1]['sale'].partner_id.email or None
                            # },
                    }
                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/salesreceipt?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                    '/salesreceipt/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                    "sparse": r.json()['SalesReceipt']['sparse'],
                                    "Id": r.json()['SalesReceipt']['Id'],
                                    "SyncToken": r.json()['SalesReceipt']['SyncToken'], })
                    else:
                        result_dict
                    headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export SalesReceipt order api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    

                    if r1.status_code == 200:
                        arguments[1]['sale'].write(
                                {'quickbook_id': r1.json()['SalesReceipt']['Id']})
                        response = r1.json()
                        count = 0
                        for lines in response['SalesReceipt']['Line']:
                            if 'Id' in lines:
                                order_lines = arguments[1]['sale'].order_line
                                order_lines[count].write({'sequence': lines['LineNum'], 'quickbook_id': lines['Id']})
                                count += 1

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/salesreceipt?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                    '/salesreceipt/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                    "sparse": r.json()['SalesReceipt']['sparse'],
                                    "Id": r.json()['SalesReceipt']['Id'],
                                    "SyncToken": r.json()['SalesReceipt']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export SalesReceipt api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    

                    
                    if r1.status_code == 200:
                        arguments[1]['sale'].write(
                                {'quickbook_id': r1.json()['SalesReceipt']['Id']})
                        response = r1.json()
                        count = 0
                        for lines in response['SalesReceipt']['Line']:
                            if 'Id' in lines:
                                order_lines = arguments[1]['sale'].order_line
                                order_lines[count].write({'sequence': lines['LineNum'], 'quickbook_id': lines['Id']})
                                count += 1

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_account(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_account':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/account?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/account?operation=update&minorversion=4'
                result_dict = {
                            "Name" : arguments[1]['account'].name,
                            "AccountType": arguments[1]['account'].user_type_id.name,
                            # "CurrentBalance": arguments[1]['account'].balance,
                        }
                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/account?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/account/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Account']['sparse'],
                                "Id": r.json()['Account']['Id'],
                                "SyncToken": r.json()['Account']['SyncToken'], })
                    else:
                        result_dict
                    headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export Account api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    

                    if r1.status_code == 200:
                        arguments[1]['account'].write(
                                {'quickbook_id': r1.json()['Account']['Id']})

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/account?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/account/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Account']['sparse'],
                                "Id": r.json()['Account']['Id'],
                                "SyncToken": r.json()['Account']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export Account api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    

                    if r1.status_code == 200:
                        arguments[1]['account'].write(
                                {'quickbook_id': r1.json()['Account']['Id']})

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_Term(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_term':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/term?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/term?operation=update&minorversion=4'
                if arguments[1]['term']:
                    if arguments[1]['term'].line_ids[0].days == 0:
                        typed = 'DATE_DRIVEN'
                        due_date = 0
                    else:
                        typed = 'STANDARD'
                        due_date = arguments[1]['term'].line_ids[0].days

                result_dict = {
                            "Name" : arguments[1]['term'].name,
                            "Active": arguments[1]['term'].active,
                            "Type": typed,
                            "DueDays": due_date,

                        }

                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/term?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/term/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Term']['sparse'],
                                "Id": r.json()['Term']['Id'],
                                "SyncToken": r.json()['Term']['SyncToken'], })
                    else:
                        result_dict
                    headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export Term api %s %s %s",
                             api_method, r1.status_code, r1.json())

                    

                    if r1.status_code == 200:
                        arguments[1]['term'].write(
                                {'quickbook_id': r1.json()['Term']['Id']})

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/term?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/term/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Term']['sparse'],
                                "Id": r.json()['Term']['Id'],
                                "SyncToken": r.json()['Term']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(
                            result_dict), headers=headers)
                    _logger.info("Export Term api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    
                    if r1.status_code == 200:
                        arguments[1]['term'].write(
                                {'quickbook_id': r1.json()['Term']['Id']})

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_PaymentMethod(self, method, arguments):

        _logger.debug("Start calling Payment Method api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)
        
        if method == 'update_PaymentMethod':
            if headeroauth:
                if not arguments[0]:
                    api_method = self.quick.location + \
                        self.quick.company_id+'/paymentmethod?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/paymentmethod?operation=update&minorversion=4'
                

                result_dict = {
                            "Name" : arguments[1]['paymentmethod'].name,
                            # "Active": arguments[1]['paymentmethod'].active,
                            "Type": arguments[1]['paymentmethod'].payment_type,

                        }

                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/paymentmethod?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/paymentmethod/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['PaymentMethod']['sparse'],
                                "Id": r.json()['PaymentMethod']['Id'],
                                "SyncToken": r.json()['PaymentMethod']['SyncToken'], })
                    else:
                        result_dict
                    headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export payment Method api %s %s %s",
                             api_method, r1.status_code, r1.json())

                    

                    if r1.status_code == 200:
                        arguments[1]['paymentmethod'].write(
                                {'quickbook_id': r1.json()['PaymentMethod']['Id']})

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/paymentmethod?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/paymentmethod/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['PaymentMethod']['sparse'],
                                "Id": r.json()['PaymentMethod']['Id'],
                                "SyncToken": r.json()['PaymentMethod']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(
                            result_dict), headers=headers)
                    _logger.info("Export Payment Method api %s %s %s",
                             api_method, r1.status_code, r1.json())

                    

                    if r1.status_code == 200:
                        arguments[1]['paymentmethod'].write(
                                {'quickbook_id': r1.json()['PaymentMethod']['Id']})

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_service(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == 'oauth2':
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_taxes':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/taxservice/taxcode?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/term?operation=update&minorversion=4'

                temp_array = []
                if arguments[1]['taxservice'].children_tax_ids:
                    for order_line in arguments[1]['taxservice'].children_tax_ids:
                        if order_line.type_tax_use ==  'sale':
                            apply_on = 'Sales'
                        else:
                            apply_on = 'Purchase'
                        temp = {
                              "TaxRateName": order_line.name,
                              # "TaxRateId": "3",
                              "RateValue": order_line.amount,
                              "TaxAgencyId": "1",
                              "TaxApplicableOn": apply_on,
                            }
                        temp_array.append(temp)

                result_dict = {
                          "TaxCode": 'QBO'+arguments[1]['taxservice'].name,
                          # "TaxCodeId": "1",
                          "TaxRateDetails": temp_array
                        }
                if self.quick.type == 'oauth1':
                    if api_method == self.quick.location+self.quick.company_id+'/taxservice/taxcode?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/taxservice/taxcode/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Term']['sparse'],
                                "Id": r.json()['Term']['Id'],
                                "SyncToken": r.json()['Term']['SyncToken'], })
                    else:
                        result_dict
                    headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export Term api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    

                    if r1.status_code == 200:
                        arguments[1]['taxservice'].write(
                                {'quickbook_id': r1.json()['TaxCodeId']})
                        for child_id in arguments[1]['taxservice'].children_tax_ids:
                            for child_tax_id in r1.json()['TaxRateDetails']:
                                child_id.write({'quickbook_id': child_tax_id['TaxRateId']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                if self.quick.type == 'oauth2':
                    if api_method == self.quick.location+self.quick.company_id+'/taxservice/taxcode?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/taxservice/taxcode/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Term']['sparse'],
                                "Id": r.json()['Term']['Id'],
                                "SyncToken": r.json()['Term']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export Tax Service api %s %s %s",
                             api_method, r1.status_code, r1.json())

                    

                    if r1.status_code == 200:
                        arguments[1]['taxservice'].write(
                                {'quickbook_id': r1.json()['TaxCodeId']})
                        for child_id in arguments[1]['taxservice'].children_tax_ids:
                            for child_tax_id in r1.json()['TaxRateDetails']:
                                child_id.write({'quickbook_id': child_tax_id['TaxRateId']})
                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_purchase(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == "oauth1":
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == "oauth2":
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_purchase':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/purchaseorder?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/purchaseorder?operation=update&minorversion=4'

                temp_array = []
                if arguments[1]['purchase'].order_line:
                    for order_line in arguments[1]['purchase'].order_line:
                        product_template_id = self.env['product.template'].search(
                            [('name', '=', order_line.product_id.name)])

                        temp = {
                                # "TxnDate": arguments[1]['invoice'].date_invoice,

                                "Description": order_line.name or None,
                                "Amount": order_line.price_subtotal,
                                "DetailType": "ItemBasedExpenseLineDetail",
                                "ItemBasedExpenseLineDetail": {
                                    "ItemRef": {
                                              "value": product_template_id.quickbook_id or None,
                                              # "name": order_line.product_id..invoice_line.product_id.name,
                                    },
                                    "UnitPrice": order_line.price_unit,
                                    "Qty": order_line.product_qty,

                                },
                                # "LineNum": order_line.sequence,
                                "Id": order_line.quickbook_id or None,
                            }
                        temp_array.append(temp)
                result_dict = {
                        # "TxnDate": arguments[1]['invoice'].date_invoice,
                            "DocNumber": arguments[1]['purchase'].name,
                            "Line": temp_array,
                            "VendorRef": {
                                "value": arguments[1]['purchase'].partner_id.quickbook_id,
                            },

                            # "DueDate": arguments[1]['purchaseorder'].date_due,
                            # "TotalAmt": arguments[1]['invoice'].amount_total,
                            # "BillEmail": {
                            #     "Address": arguments[1]['purchaseorder'].partner_id.email
                            # },
                    }
                if self.quick.type == "oauth1":
                    if api_method == self.quick.location+self.quick.company_id+'/purchaseorder?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/purchaseorder/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['PurchaseOrder']['sparse'],
                                "Id": r.json()['PurchaseOrder']['Id'],
                                "SyncToken": r.json()['PurchaseOrder']['SyncToken'], })
                    else:
                        result_dict
                    headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export PurchaseOrder api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    

                    if r1.status_code == 200:
                        arguments[1]['purchase'].write(
                                {'quickbook_id': r1.json()['PurchaseOrder']['Id']})
                        response = r1.json()
                        count = 0
                        for lines in response['PurchaseOrder']['Line']:
                            if 'Id' in lines:
                                order_lines = arguments[1]['purchase'].order_line
                                order_lines[count].write({ 'quickbook_id': lines['Id']})
                                count += 1

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == "oauth2":
                    if api_method == self.quick.location+self.quick.company_id+'/purchaseorder?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/purchaseorder/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['PurchaseOrder']['sparse'],
                                "Id": r.json()['PurchaseOrder']['Id'],
                                "SyncToken": r.json()['PurchaseOrder']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export Purchase Order api %s %s %s",
                             api_method, r1.status_code, r1.json())
                    
                                      

                    if r1.status_code == 200:
                        arguments[1]['purchase'].write(
                                {'quickbook_id': r1.json()['PurchaseOrder']['Id']})
                        response = r1.json()
                        count = 0
                        for lines in response['PurchaseOrder']['Line']:
                            if 'Id' in lines:
                                order_lines = arguments[1]['purchase'].order_line
                                order_lines[count].write({ 'quickbook_id': lines['Id']})
                                count += 1

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

    def _call_invoice(self, method, arguments):

        # _logger.debug("Start calling student api %s", method)
        if self.quick.type == 'oauth1':
            headeroauth = OAuth1(self.quick.client_key, self.quick.client_secret,
                                 self.quick.resource_owner_key, self.quick.resource_owner_secret,
                                 signature_type='auth_header')
        elif self.quick.type == "oauth2":
            headeroauth = OAuth2Session(self.quick.client_key)

        if method == 'update_invoice':
            if headeroauth:
                if not arguments[0]:

                    # api_method = self.quick.location+self.quick.company_id+'/item?minorversion=4'
                    api_method = self.quick.location + \
                        self.quick.company_id+'/invoice?minorversion=4'
                else:
                    api_method = self.quick.location+self.quick.company_id+'/invoice?operation=update&minorversion=4'

                temp_array = []
                if arguments[1]['invoice'].invoice_line_ids:
                    for order_line in arguments[1]['invoice'].invoice_line_ids:
                        product_template_id = self.env['product.template'].search(
                            [('name', '=', order_line.product_id.name)])
                        if order_line.invoice_line_tax_ids:
                            taxcoderef = "TAX"
                        else:
                            taxcoderef = "NON"

                        temp = {
                                # "TxnDate": arguments[1]['invoice'].date_invoice,

                                "Description": order_line.name or None,
                                "Amount": order_line.price_subtotal,
                                "DetailType": "SalesItemLineDetail",
                                "SalesItemLineDetail": {
                                    "ItemRef": {
                                              "value": product_template_id.quickbook_id or None,
                                              # "name": order_line.product_id..invoice_line.product_id.name,
                                    },
                                    "UnitPrice": order_line.price_unit,
                                    "Qty": order_line.quantity,
                                    "TaxCodeRef": {
                                            "value": taxcoderef,
                                          }

                                },
                                # "LineNum": order_line.sequence,
                                "Id": order_line.quickbook_id or None,
                            }
                        temp_array.append(temp)
                result_dict = {
                            "TxnDate": arguments[1]['invoice'].date_invoice,
                            "DocNumber": arguments[1]['invoice'].doc_number,
                            "Line": temp_array,
                            "CustomerRef": {
                                "value": arguments[1]['invoice'].partner_id.quickbook_id,
                            },
                            "DueDate": arguments[1]['invoice'].date_due,
                            # "TotalAmt": arguments[1]['invoice'].amount_total,
                            "BillEmail": {
                                "Address": arguments[1]['invoice'].partner_id.email or None
                            },
                            "SalesTermRef":{
                                "value": arguments[1]['invoice'].payment_term_id.quickbook_id or None,
                        },
                    }
                if self.quick.type == "oauth1":
                    if api_method == self.quick.location+self.quick.company_id+'/invoice?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/invoice/' + str(arguments[0])+'?minorversion=4'
                        headers = {'accept': 'application/json'}
                        r = requests.get(ris, auth=headeroauth, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Invoice']['sparse'],
                                "Id": r.json()['Invoice']['Id'],
                                "SyncToken": r.json()['Invoice']['SyncToken'], })
                    else:
                        result_dict
                    headers = {
                            'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = requests.post(api_method, data=json.dumps(
                            result_dict), auth=headeroauth, headers=headers)
                    _logger.info("Export Invoice api %s %s %s",
                             api_method, r1.status_code, r1.json())
                                        

                    if r1.status_code == 200:
                        arguments[1]['invoice'].write(
                                {'quickbook_id': r1.json()['Invoice']['Id']})
                        response = r1.json()
                        count = 0
                        for lines in response['Invoice']['Line']:
                            if 'Id' in lines:
                                order_lines = arguments[1]['invoice'].invoice_line_ids
                                order_lines[count].write({'quickbook_id': lines['Id']})
                                count += 1

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)

                elif self.quick.type == "oauth2":
                    if api_method == self.quick.location+self.quick.company_id+'/invoice?operation=update&minorversion=4':
                        ris = self.quick.location+self.quick.company_id + \
                                '/invoice/' + str(arguments[0])+'?minorversion=4'
                        headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                    'content-type': 'application/json', 'accept': 'application/json'}
                        r = headeroauth.get(ris, headers=headers)
                        
                        result_dict.update({
                                "sparse": r.json()['Invoice']['sparse'],
                                "Id": r.json()['Invoice']['Id'],
                                "SyncToken": r.json()['Invoice']['SyncToken'], })
                    else:
                        result_dict
                    headers = {'Authorization': 'Bearer %s' %self.quick.access_token,
                                'content-type': 'application/json', 'accept': 'application/json'}
                    r1 = headeroauth.post(api_method, data=json.dumps(result_dict), headers=headers)
                    _logger.info("Export Invoice api %s %s %s",
                             api_method, r1.status_code, r1.json())
                                        

                    if r1.status_code == 200:
                        arguments[1]['invoice'].write(
                                {'quickbook_id': r1.json()['Invoice']['Id']})
                        response = r1.json()
                        count = 0
                        for lines in response['Invoice']['Line']:
                            if 'Id' in lines:
                                order_lines = arguments[1]['invoice'].invoice_line_ids
                                order_lines[count].write({'quickbook_id': lines['Id']})
                                count += 1

                    if r1.status_code == 500 or r1.status_code == 400:
                        for errors in r1.json()['Fault']['Error']:
                            msg = errors['Message']
                            details = errors['Detail']
                            raise Warning(details)


class GenericAdapter(WooCRUDAdapter):

    _model_name = None
    _booking_model = None

    def search(self, filters=None):
        """ Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        return self._call('%s.search' % self._booking_model,
                          [filters] if filters else [{}])

    def read(self, id, attributes=None):
        """ Returns the information of a record

        :rtype: dict
        """
        arguments = []
        if attributes:
            # Avoid to pass Null values in attributes. Workaround for
            # is not installed, calling info() with None in attributes
            # would return a wrong result (almost empty list of
            # attributes). The right correction is to install the
            # compatibility patch on Quickbook.
            arguments.append(attributes)
        return self._call('%s/' % self._booking_model + str(id), arguments)

    def search_read(self, filters=None):
        """ Search records according to some criterias
        and returns their information"""
        return self._call('%s.list' % self._booking_model, [filters])

    def create(self, data):
        """ Create a record on the external system """
        return self._call('%s.create' % self._booking_model, [data])

    def write(self, id, data):
        """ Update records on the external system """
        return self._call('%s.update' % self._booking_model,
                          [int(id), data])

    def delete(self, id):
        """ Delete a record on the external system """
        return self._call('%s.delete' % self._booking_model, [int(id)])
