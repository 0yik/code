# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp import exceptions
from subprocess import Popen, PIPE, STDOUT
import shlex
import os
import boto3


def _unescape(text):
    '''Replaces all encoded characters by urlib with plain utf8 string.'''

    from urllib import unquote_plus
    return unquote_plus(text.encode('utf8'))


class AmazonSqsConfig(models.Model):
    _name = "amazon.sqs"

    name = fields.Char('Name', required=True)
    queue_name = fields.Char(
        ' Sale Queue Name', default=lambda self: self._get_default_name(), required=True)
    purchase_queue = fields.Char(
        'Purchase Queue Name', default=lambda self: self._get_default_name(), required=False)
    delivery_queue = fields.Char(
        'Delivery Queue Name', default=lambda self: self._get_default_name(), required=False)
    aws_access_key_id = fields.Char('AWS Access Key ID', required=True)
    aws_secret_access_key = fields.Char('AWS Secret Access Key', required=True)
    default_region = fields.Char('Default region name', required=True)
    default_output_format = fields.Char(
        'Default Output Format', default=lambda self: self._get_default_name())

    _sql_constraints = [
        ('uniq_name', 'unique(queue_name)',
         "A Queue already exists with this name . Queue name must be unique !"),
    ]

    @api.model
    def _get_default_name(self):
        return " "

    @api.model
    def create(self, vals):
        self.map_aws_configure(vals)
        return super(AmazonSqsConfig, self).create(vals)
        
    @api.multi
    def write(self, vals):
        vals = self.map_values(vals)
        self.map_aws_configure(vals)
        return super(AmazonSqsConfig, self).write(vals)

    def test_connection(self):
        """ Test connection to aws queue """
        sqs = boto3.resource(
            'sqs',
            region_name=self.default_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        try:
            # queue = sqs.create_queue(QueueName='MumsDevIn', Attributes={'DelaySeconds': '5'})
            queue_name = sqs.get_queue_by_name(QueueName=self.queue_name)

        except Exception, e:

            raise Warning(
                _('Check your AWS Access Key ID, AWS Secret Access Key, Region Name and Queue name'))

        raise Warning(_('Test Success'))

        return True

    def map_aws_configure(self, vals):
        cmd = "aws configure"
        args = shlex.split(cmd)
        p = Popen(args, stdin=PIPE, shell=True)
        p.communicate(os.linesep.join([
            vals['aws_access_key_id'],
            vals['aws_secret_access_key'],
            vals['default_region'],
            vals['default_output_format']]))
        
    def map_values(self, vals):
        if vals.has_key('name'):
            vals['name'] = _unescape(vals['name'])
        else:
            vals['name'] = self.name

        if vals.has_key('default_region'):
            vals['default_region'] = _unescape(vals['default_region'])
        else:
            vals['default_region'] = self.default_region

        if vals.has_key('aws_access_key_id'):
            vals['aws_access_key_id'] = _unescape(vals['aws_access_key_id'])
        else:
            vals['aws_access_key_id'] = self.aws_access_key_id

        if vals.has_key('aws_secret_access_key'):
            vals['aws_secret_access_key'] = _unescape(
                vals['aws_secret_access_key'])
        else:
            vals['aws_secret_access_key'] = self.aws_secret_access_key

        if vals.has_key('queue_name'):
            vals['queue_name'] = _unescape(vals['queue_name'])
        else:
            vals['queue_name'] = self.queue_name

        if vals.has_key('default_output_format'):
            vals['default_output_format'] = _unescape(
                vals['default_output_format'])
        else:
            vals['default_output_format'] = self.default_output_format
        return vals        
