# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ReportAgedPartnerBalance(models.Model):

    _inherit = 'account.move.line'

    @api.model
    def list_journals(self):
        '''returns the list of journal to selection widget'''
        journals = dict(self.env['account.journal'].name_search('',[]))
        ids = journals.keys()
        result = []
        for journal in self.env['account.journal'].browse(ids):
            result.append((journal.id,journals[journal.id],journal.type))
        return result