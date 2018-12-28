# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.translate import _
from odoo import tools
from odoo import api, fields, models, tools
from odoo.osv import expression
import datetime as dt
import calendar
from datetime import date, timedelta as td, datetime
#from odoo.osv.orm import setup_modifiers
from lxml import etree

class cashflow_type(models.Model):#osv.osv):
    _name = 'cashflow.type'
    _description = 'Tipo de Conta Cashflow'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if not args:
            args = []
        domain = ['|', ('code', operator, name), ('name', operator, name)]
        ids = self.search(expression.AND([domain, args]), limit=limit)
        return ids.name_get()
        # return self.name_get(ids)

    @api.multi
    def name_get(self):#, cr, uid, ids, context=None):
        # if not ids:
        #     return []
        # if isinstance(ids, (int, long)):
        #             ids = [ids]
        # reads = self.read(self._cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in self:
            name = record['name']
            if record['code']:
                name = record['code'] + ' - ' + name
            res.append((record['id'], name))
        return res

    name = fields.Char(string="Nome", required=True)
    code = fields.Char(string="Código", required=True)
    type = fields.Selection([('fluxo_operacional', 'Fluxo Operacional'),('fluxo_outros', 'Fluxo Outros'),
                            ('fluxo_financeiro', 'Fluxo Financeiros'),('fluxo_antecipa', 'Fluxo Antecipações'),
                            ('fluxo_emp', 'Fluxo Empréstimos'),('fluxo_patrimoniais', 'Fluxo Patrimoniais')], string='Tipo')

cashflow_type()

class cashflow_wizard(models.Model):#osv.osv):
    _name = 'cashflow.wizard'
    _description = 'Relatorio de Cashflows'

    @api.model
    def _default_dia_inicio(self):
        date = dt.date.today()
        start_date = dt.datetime(date.year, date.month, 1)
        return start_date

    @api.model
    def _default_dia_fim(self):
        date = dt.date.today()
        end_date = dt.datetime(date.year, date.month, calendar.mdays[date.month])
        return end_date

    data_inicio = fields.Date(string="Data Inicio", required=True, default=_default_dia_inicio)
    data_fim = fields.Date(string="Data Fim", required=True, default=_default_dia_fim)
    journal_id = fields.Many2one('account.journal', string='Banco', domain="[('type', 'in', ['bank','cash'])]")

    @api.multi
    def open_view_cashflow_reports(self):#, cr, uid, ids, context=None):
        if self._context is None:
          self._context = {}



        try:
            form = self.read(self._cr)#, uid, ids, context=context)[0]
        except:
            data_atual = datetime.now()
            form = {'data_inicio': data_atual, 'data_fim': data_atual}
        ## verificar se a tabela do report cashflow já está preenchida
        self._cr.execute("select id from cashflow_report limit 1")
        historico= self._cr.fetchone()

        if historico!=None and historico[0]!=None:
            ## se estiver preenchida apagar todos os registos
            self._cr.execute("delete from cashflow_report")

        data_inicio=form['data_inicio']
        data_fim=form['data_fim']

        data_inicio2=form['data_inicio']
        data_fim2=form['data_fim']

        dados_tree={}
        name='Documento'
        debit=0
        credit=0
        date=data_inicio
        journal_id=1
        account_id=9
        partner_id=1
        reconciled=False
        diarios = []

        #IR BUSCAR AS FATURAS POR PAGAR
        self._cr.execute("select residual,type,number,date_due,journal_id,account_id,partner_id,id, amount_total from account_invoice where state in ('draft','open')")
        faturas=self._cr.fetchall()
        for l in faturas:
            #recebimentos
            if l[1] in ('out_invoice', 'in_refund'):
                if l[0] != 0:
                    debit=l[0]
                else:
                    debit=l[8]

                credit=0
                tipo='entrada'
            #pagamentos
            else:
                debit=0
                if l[0] != 0:
                    credit=l[0]
                else:
                    credit=l[8]
                tipo='saida'

            name=l[2]
            data_atual = datetime.now()

            data_atual=str(data_atual).split()
            if l[3] != None:
                date=l[3]
            else:
                date=data_atual[0]



            # data_atual = data_atual[0].strptime('%Y-%m-%d')
            data_fatura= datetime.strptime(str(date),'%Y-%m-%d')
            data_final = datetime.strptime(str(data_atual[0]),'%Y-%m-%d')
            if data_fatura <= data_final:
                date = data_final

            journal_id=l[4]
            account_id=l[5]
            partner_id=l[6]

            dados_tree['name']=name
            dados_tree['tipo']=tipo
            dados_tree['entrada']=debit
            dados_tree['saida']=credit
            dados_tree['date']=date
            dados_tree['journal_id']=journal_id
            dados_tree['account_id']=account_id
            dados_tree['invoice_id']=l[7]
            dados_tree['reconciled']=reconciled
            dados_tree['partner_id']=partner_id

            #registo = self.pool.get('cashflow.report').create(cr, uid, dados_tree)
            registo = self.env['cashflow.report'].create(dados_tree)

            if l and l[4] and str(l[4]) not in diarios:
                try:
                    diarios.append(l[4])
                except:
                    e=123

            diarios= str(diarios).replace('[','(').replace(']',')')

        #IR BUSCAR PAGAMENTOS e FATURAS AOS ACCOUNT_MOVE_LINES
        if diarios!=[]:
            self._cr.execute("select debit,credit,ref,date_maturity,journal_id,account_id,partner_id,date,name,move_id from account_move_line where move_id in (select id from account_move where state='posted') and journal_id not in "+str(diarios))
        else:
            self._cr.execute("select debit,credit,ref,date_maturity,journal_id,account_id,partner_id,date,name,move_id from account_move_line where move_id in (select id from account_move where state='posted')")
        move_lines=self._cr.fetchall()
        for l in move_lines:
            self._cr.execute("select internal_type from account_account where id="+str(l[5]))
            conta=self._cr.fetchone()
            if conta!=None and conta[0]!=None:
                if conta[0] == 'liquidity':
                    debit=l[0]
                    credit=l[1]
                    tipo='saida'
                    if debit>0:
                        tipo='entrada'

                    name = _(l[2]) + ' ' + _(l[8])
                    if l[9]!=None:
                        self._cr.execute("select name from account_move where id="+str(l[9]))
                        movimento=self._cr.fetchone()
                        if movimento!=None and movimento[0]!=None:
                            name = _(l[2]) + ' ' + _(l[8]) + _(movimento[0])
                    date=l[7]
                    journal_id=l[4]
                    account_id=l[5]
                    partner_id=l[6]

                    dados_tree['tipo']=tipo
                    dados_tree['name']=name
                    dados_tree['entrada']=debit
                    dados_tree['saida']=credit
                    dados_tree['date']=date
                    dados_tree['journal_id']=journal_id
                    dados_tree['move_id']=l[9]
                    dados_tree['account_id']=account_id
                    dados_tree['reconciled']=reconciled
                    dados_tree['partner_id']=partner_id

                    #registo = self.pool.get('cashflow.report').create(cr, uid, dados_tree)
                    registo = self.env['cashflow.report'].create(dados_tree)


        ctx = self._context.copy()
        ctx['total1']=1


        #self.pool.get('cashflow.report').update_saldos(cr,uid,ids,context)
        self.env['cashflow.report'].update_saldos()


        return True


        # return {
        #   # 'domain': "[('auction_id', '=', "+str(data['leilao'][0])+")]",
        #   'name': _('Relatório de Cashflow'),
        #   'view_type': 'form',
        #   'view_mode': 'graph,tree',
        #   'res_model': 'cashflow.report',
        #   'type': 'ir.actions.act_window',
        #   'context': ctx,
        # }

cashflow_wizard()

class cashflow_report(models.Model):
    _name = 'cashflow.report'
    _description = 'Cashflow Report'
    _order = "date asc, id asc"

    @api.multi
    def update_saldos(self):#, cr, uid, ids, context=None):
            if self._context is None:
              self._context = {}

            self._cr.execute("select id,date from cashflow_report order by date asc, id asc")
            reports=self._cr.fetchall()
            for r in reports:
                self._cr.execute("select sum(entrada),sum(saida) from cashflow_report where id<="+str(r[0])+" and date<='"+str(r[1])+"'")
                somas=self._cr.fetchone()
                soma = somas[0] - somas[1]
                self._cr.execute("update cashflow_report set saldo="+str(soma)+" where id="+str(r[0]))

            return True

    name = fields.Char(string="Descrição")
    entrada = fields.Float(string="Entrada", default=0.0)
    saida = fields.Float(string="Saida", default=0.0)
    saldo = fields.Float(string="Saldo", default=0.0, copy=False)
    date = fields.Date(string='Date', required=True, index=True, default=fields.Date.context_today, store=True, copy=False)
    journal_id = fields.Many2one('account.journal', string='Journal', index=True, store=True, copy=False)
    invoice_id = fields.Many2one('account.invoice', string='Invoice', index=True, store=True, copy=False)
    move_id = fields.Many2one('account.move', string='Movimento', index=True, store=True, copy=False)
    account_id = fields.Many2one('account.account', string='Account', required=True, index=True, ondelete="cascade", domain=[('deprecated', '=', False)], default=lambda self: self._context.get('account_id', False))
    reconciled = fields.Boolean(string='Reconclied', store=True)
    partner_id = fields.Many2one('res.partner', string='Partner', index=True, ondelete='restrict')
    tipo = fields.Selection([('entrada', 'Entrada'),('saida', 'Saída')], string='Tipo')


cashflow_report()
