# -*- coding: utf-8 -*-

import logging
from odoo.exceptions import except_orm

_logger = logging.getLogger(__name__)


class AbstractMethodError(Exception):
    def __str__(self):
        return 'Abstract Method'

    def __repr__(self):
        return 'Abstract Method'


class DataGetterType(type):
    """ Meta class for currency getters.
        Automaticaly registers new data getter on class definition
    """
    getters = {}

    def __new__(mcs, name, bases, attrs):
        cls = super(DataGetterType, mcs).__new__(mcs, name, bases, attrs)
        if getattr(cls, 'code', None):
            mcs.getters[cls.code] = cls
        return cls

    @classmethod
    def get(mcs, code, *args, **kwargs):
        """ Get getter by code
        """
        return mcs.getters[code](*args, **kwargs)


class DataGetterInterface(object):
    """ Abstract class of data getter

        To create new getter, just subclass this class
        and define class variables 'code' and 'name'
        and implement *get_products* method

        For example::

            from odoo.addons.marketplaces \
                import DataGetterInterface

            class MySuperDataGetter(DataGetterInterface):
                code = "lazada"
                name = "Lazada"

                def get_products(self):
                    # your code that fills self.updated_products

                    # and return result
                    return self.updated_products, self.log_info

    """
    __metaclass__ = DataGetterType

    # attributes required for data getters
    code = None  # code for service selection
    name = None  # displayed name

    app_id = None
    app_secret = None

    log_info = ' '

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    def get_url(self, url):
        """Return a string of a get url query"""
        try:
            import urllib
            objfile = urllib.urlopen(url)
            rawfile = objfile.read()
            objfile.close()
            return rawfile
        except ImportError:
            raise except_orm(
                'Error !',
                self.MOD_NAME + 'Unable to import urllib !'
            )
        except IOError:
            raise except_orm(
                'Error !',
                self.MOD_NAME + 'Web Service does not exist !'
            )

    def get_products(self):
        """Interface method that will retrieve the currency
           This function has to be reinplemented in child
        """
        raise AbstractMethodError