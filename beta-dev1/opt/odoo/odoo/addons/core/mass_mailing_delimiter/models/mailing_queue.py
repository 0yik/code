# -*- coding: utf-8 -*-

import uuid
import boto3
import json
import gearman
from odoo import models, fields, api

# Let's use Amazon S3
class mailing_queue(models.Model):
    _name = 'mailing.queue'

    state      = fields.Selection([
        ('draft', 'Draft'),
        ('connected', 'Connected'),
        ('failed', 'Failed'),
    ], default='draft', string="Status")
    name       = fields.Char('Name', required=True)
    unique_key = fields.Char('Unique key')

    # Check connection to SQS server
    @api.multi
    def action_test_connection(self):
        for record in self:
            if record.name:
                record.state = 'connected'
            else:
                record.state = 'failed'
        return True

    @api.model
    def get_servers(self):
        result = []
        servers = self.search([('state', '=', 'connected')])
        for server in servers:
            result.append(server.name)
        return result

    @api.model
    def get_client(self, servers):
        client = gearman.GearmanClient(servers)
        return client

    @api.model
    def send_message_action(self, action, data):
        servers     = self.get_servers()
        client      = self.get_client(servers)
        client.submit_job(action, data, priority=gearman.PRIORITY_HIGH, background=True)

        print '----SENT MESSAGE:%s' % (action)
        return True
