# -*- coding: utf-8 -*-
import cStringIO
import datetime
from itertools import islice
import json
import xml.etree.ElementTree as ET

from openerp import SUPERUSER_ID
import logging
import re

import werkzeug.utils
import urllib2
import werkzeug.wrappers
from PIL import Image

import odoo
from odoo.addons.web.controllers.main import WebClient
#from odoo.addons.web import http
from odoo import http
from odoo.http import request, STATIC_CACHE
from odoo.tools import image_save_for_web
from odoo.tools.translate import _
logger = logging.getLogger(__name__)

# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_SITEMAP = 45000
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)

from datetime import datetime

class Website_cash_flows(odoo.addons.web.controllers.main.Home):

    @http.route(['/cashflows'], type='http', auth="public", website=True)
    def get_mapas(self, category='', search='', **kwargs):
        self._cr, self._uid, self._context, self.pool = request.cr, request.uid, request.context, request.registry

        filtro_data_inicio=''
        filtro_data_fim=''
        filtro_diario=''

        cashflow_obj = request.env['cashflow.report']
        # aux=self.pool['cashflow.wizard']
        # lista=aux.search()
        # for l in lista:
        #
        #     l.open_view_cashflow_reports(aux)

        #abrir reports
        request.env['cashflow.wizard'].open_view_cashflow_reports()
        #        self.pool['cashflow.wizard'].open_view_cashflow_reports()

        if self._uid != None and self._uid==3:
            return request.redirect("/")

        cashflow_obj_ids = cashflow_obj.search([])#self._self._cr, self._self._uid, [], context=self._context)
        #cashflow_obj_browse = cashflow_obj.browse(self._self._cr, self._self._uid, cashflow_obj_ids, context=self._context)

        lista_diarios = []
        self._cr.execute("select distinct(journal_id),date from cashflow_report order by date asc " )
        diarios=self._cr.fetchall()
        for d in diarios:
            self._cr.execute("select type from account_journal where id="+str(d[0]))
            tipo_diario_caixa_ou_banco=self._cr.fetchone()
            if tipo_diario_caixa_ou_banco!=None and tipo_diario_caixa_ou_banco[0]!=None and tipo_diario_caixa_ou_banco[0] in ('bank','cash'):
                lista_diarios.append(d[0])

        lista_datas = []
        self._cr.execute("select distinct(date) from cashflow_report order by date asc " )
        datas=self._cr.fetchall()
        for d in datas:
            lista_datas.append(str(d[0]))
        lista_datas = str(lista_datas).replace("'","").replace("[","").replace("]","")

        lista_entradas = []
        self._cr.execute("select sum(entrada) from cashflow_report group by date order by date")
        entradas=self._cr.fetchall()
        for e in entradas:
            lista_entradas.append(int(e[0]))
        lista_entradas = str(lista_entradas).replace("'","").replace("[","").replace("]","")

        lista_saidas = []
        self._cr.execute("select sum(saida) from cashflow_report group by date order by date")
        saidas=self._cr.fetchall()
        for s in saidas:
            lista_saidas.append(int(s[0]))
        lista_saidas = str(lista_saidas).replace("'","").replace("[","").replace("]","")

        lista_saldos = []
        saldo_valor=0
        self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report group by date order by date")
        saldos=self._cr.fetchall()
        for sa in saldos:
            saldo_valor+=sa[0]
            lista_saldos.append(int(saldo_valor))
        lista_saldos = str(lista_saldos).replace("'","").replace("[","").replace("]","")


        lista_tipos = []
        self._cr.execute("select date, tipo, entrada, saida from cashflow_report group by date, tipo,entrada,saida,id order by date asc, id asc " )
        registos=self._cr.fetchall()
        for l in registos:
            lista_tipos.append(str(l[1]))


        ##################
        #DADODS GRAFICO 4#
        ##################
        accounts_obj = request.env['account.account']
        #1 - vendas brutas
        vendas_brutas=0
        tipo_fluxo_vendas_brutas=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'1')])
        for c in accounts_obj_ids:
            tipo_fluxo_vendas_brutas=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            vendas_brutas1=self._cr.fetchone()
            if vendas_brutas1 != None and vendas_brutas1[0] != None:
                vendas_brutas+=vendas_brutas1[0]

        #7 - despesas de vendas
        despesas_vendas=0
        tipo_fluxo_despesas_vendas=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '7')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_vendas=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_vendas1=self._cr.fetchone()
            if despesas_vendas1 != None and despesas_vendas1[0] != None:
                despesas_vendas+=despesas_vendas1[0]

        #8 - custos operacao
        custos_operacao=0
        tipo_fluxo_custos_operacao=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '8')])
        for c in accounts_obj_ids:
            tipo_fluxo_custos_operacao=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            custos_operacao1=self._cr.fetchone()
            if custos_operacao1 != None and custos_operacao1[0] != None:
                custos_operacao+=custos_operacao1[0]
        #9 - despesas administrativas
        despesas_admin=0
        tipo_fluxo_despesas_admin=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '9')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_admin=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_admin1=self._cr.fetchone()
            if despesas_admin1 != None and despesas_admin1[0] != None:
                despesas_admin+=despesas_admin1[0]
        #10 - despesas tributarias
        despesas_tributarias=0
        tipo_fluxo_despesas_tributarias=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '10')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_tributarias=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_tributarias1=self._cr.fetchone()
            if despesas_tributarias1 != None and despesas_tributarias1[0] != None:
                despesas_tributarias+=despesas_tributarias1[0]
        #2 - Outras entradas
        outras_entradas=0
        tipo_fluxo_outras_entradas=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'2')])
        for c in accounts_obj_ids:
            tipo_fluxo_outras_entradas=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            outras_entradas1=self._cr.fetchone()
            if outras_entradas1 != None and outras_entradas1[0] != None:
                outras_entradas+=outras_entradas1[0]
        #11 - outras saidas
        outras_saidas=0
        tipo_fluxo_outras_saidas=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '11')])
        for c in accounts_obj_ids:
            tipo_fluxo_outras_saidas=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            outras_saidas1=self._cr.fetchone()
            if outras_saidas1 != None and outras_saidas1[0] != None:
                outras_saidas+=outras_saidas1[0]
        #3 - financeiras
        financeirrras=0
        tipo_fluxo_financeirrras=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '3')])
        for c in accounts_obj_ids:
            tipo_fluxo_financeirrras=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            financeirrras1=self._cr.fetchone()
            if financeirrras1 != None and financeirrras1[0] != None:
                financeirrras+=financeirrras1[0]
        #12 - despesas finanaceiras
        despesas_finan=0
        tipo_fluxo_despesas_finan=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'12')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_finan=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_finan1=self._cr.fetchone()
            if despesas_finan1 != None and despesas_finan1[0] != None:
                despesas_finan+=despesas_finan1[0]
        #4 - antecipacoes
        antecipacoes=0
        tipo_fluxo_antecipacoes=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '4')])
        for c in accounts_obj_ids:
            tipo_fluxo_antecipacoes=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            antecipacoes1=self._cr.fetchone()
            if antecipacoes1 != None and antecipacoes1[0] != None:
                antecipacoes+=antecipacoes1[0]
        #13 - despesas de antecipacoes
        despesas_antecipacoes=0
        tipo_fluxo_despesas_antecipacoes=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'13')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_antecipacoes=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_antecipacoes1=self._cr.fetchone()
            if despesas_antecipacoes1 != None and despesas_antecipacoes1[0] != None:
                despesas_antecipacoes+=despesas_antecipacoes1[0]
        #5 - Emprestimos e finan
        empre_financ=0
        tipo_fluxo_oempre_financ=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '5')])
        for c in accounts_obj_ids:
            tipo_fluxo_oempre_financ=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            empre_financ1=self._cr.fetchone()
            if empre_financ1 != None and empre_financ1[0] != None:
                empre_financ+=empre_financ1[0]
        #14 - amort_empres
        amort_empres=0
        tipo_fluxo_amort_empres=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'14')])
        for c in accounts_obj_ids:
            tipo_fluxo_amort_empres=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            amort_empres1=self._cr.fetchone()
            if amort_empres1 != None and amort_empres1[0] != None:
                amort_empres+=amort_empres1[0]
        #6 - patrimon
        patrimon=0
        tipo_fluxo_patrimon=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'6')])
        for c in accounts_obj_ids:
            tipo_fluxo_patrimon=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            patrimon1=self._cr.fetchone()
            if patrimon1 != None and patrimon1[0] != None:
                patrimon+=patrimon1[0]
        #15 - despesas patrim
        despesas_patraimn=0
        tipo_fluxo_despesas_patraimn=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '15')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_patraimn=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_patraimn1=self._cr.fetchone()
            if despesas_patraimn1 != None and despesas_patraimn1[0] != None:
                despesas_patraimn+=despesas_patraimn1[0]

        fluxo_operacional=0
        tipo_fluxo_fluxo_operacional=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_operacional')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_operacional=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_operacional1=self._cr.fetchone()
            if fluxo_operacional1 != None and fluxo_operacional1[0] != None:
                fluxo_operacional+=fluxo_operacional1[0]

        fluxo_outros=0
        tipo_fluxo_fluxo_outros=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_outros')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_outros=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_outros1=self._cr.fetchone()
            if fluxo_outros1 != None and fluxo_outros1[0] != None:
                fluxo_outros+=fluxo_outros1[0]

        fluxo_financeiro=0
        tipo_fluxo_fluxo_financeiro=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_financeiro')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_financeiro=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_financeiro1=self._cr.fetchone()
            if fluxo_financeiro1 != None and fluxo_financeiro1[0] != None:
                fluxo_financeiro+=fluxo_financeiro1[0]

        fluxo_antecipa=0
        tipo_fluxo_fluxo_antecipa=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_antecipa')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_antecipa=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_antecipa1=self._cr.fetchone()
            if fluxo_antecipa1 != None and fluxo_antecipa1[0] != None:
                fluxo_antecipa+=fluxo_antecipa1[0]

        fluxo_emp=0
        tipo_fluxo_fluxo_emp=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_emp')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_emp=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_emp1=self._cr.fetchone()
            if fluxo_emp1 != None and fluxo_emp1[0] != None:
                fluxo_emp+=fluxo_emp1[0]

        fluxo_patrimoniais=0
        tipo_fluxo_fluxo_patrimoniais=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_patrimoniais')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_patrimoniais=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_patrimoniais1=self._cr.fetchone()
            if fluxo_patrimoniais1 != None and fluxo_patrimoniais1[0] != None:
                fluxo_patrimoniais+=fluxo_patrimoniais1[0]

        values = {
            'tipo_fluxo_fluxo_patrimoniais':tipo_fluxo_fluxo_patrimoniais,
            'tipo_fluxo_fluxo_emp':tipo_fluxo_fluxo_emp,
            'tipo_fluxo_fluxo_antecipa':tipo_fluxo_fluxo_antecipa,
            'tipo_fluxo_fluxo_financeiro':tipo_fluxo_fluxo_financeiro,
            'tipo_fluxo_fluxo_outros':tipo_fluxo_fluxo_outros,
            'tipo_fluxo_fluxo_operacional':tipo_fluxo_fluxo_operacional,
            'tipo_fluxo_despesas_patraimn':tipo_fluxo_despesas_patraimn,
            'tipo_fluxo_patrimon':tipo_fluxo_patrimon,
            'tipo_fluxo_amort_empres':tipo_fluxo_amort_empres,
            'tipo_fluxo_oempre_financ':tipo_fluxo_oempre_financ,
            'tipo_fluxo_despesas_antecipacoes':tipo_fluxo_despesas_antecipacoes,
            'tipo_fluxo_antecipacoes':tipo_fluxo_antecipacoes,
            'tipo_fluxo_despesas_finan':tipo_fluxo_despesas_finan,
            'tipo_fluxo_financeirrras':tipo_fluxo_financeirrras,
            'tipo_fluxo_outras_saidas':tipo_fluxo_outras_saidas,
            'tipo_fluxo_outras_entradas':tipo_fluxo_outras_entradas,
            'tipo_fluxo_despesas_tributarias':tipo_fluxo_despesas_tributarias,
            'tipo_fluxo_despesas_admin':tipo_fluxo_despesas_admin,
            'tipo_fluxo_custos_operacao':tipo_fluxo_custos_operacao,
            'tipo_fluxo_despesas_vendas':tipo_fluxo_despesas_vendas,
            'tipo_fluxo_vendas_brutas':tipo_fluxo_vendas_brutas,
            'fluxo_patrimoniais':fluxo_patrimoniais,
            'fluxo_emp':fluxo_emp,
            'fluxo_antecipa':fluxo_antecipa,
            'fluxo_financeiro':fluxo_financeiro,
            'fluxo_outros':fluxo_outros,
            'fluxo_operacional':fluxo_operacional,
            'filtro_data_inicio': filtro_data_inicio,
            'filtro_data_fim': filtro_data_fim,
            'filtro_diario': filtro_diario,
            'journal_id_selection': lista_diarios,
            'outras_entradas': outras_entradas,
            'outras_saidas': outras_saidas,
            'financeirrras': financeirrras,
            'despesas_finan':despesas_finan,
            'antecipacoes':antecipacoes,
            'despesas_antecipacoes': despesas_antecipacoes,
            'empre_financ':empre_financ,
            'amort_empres': amort_empres,
            'patrimon':patrimon,
            'despesas_patraimn':despesas_patraimn,
            'despesas_tributarias':despesas_tributarias,
            'despesas_admin':despesas_admin,
            'custos_operacao':custos_operacao,
            'despesas_vendas':despesas_vendas,
            'vendas_brutas':vendas_brutas,
            'saldo': lista_saldos,
            'saidas': lista_saidas,
            'entradas': lista_entradas,
            'categorias': lista_tipos,
            'datas': lista_datas,
            'registos': cashflow_obj_ids,
        }

        return request.render("opencloud_cashflows.get_mapas", values)

    ## metodo refresh mapas
    @http.route(['/cashflows/refresh'], type='http', auth="user", website=True)
    def refresh_mapa(self, redirect=None, **post):
        self._cr, self._uid, self._context, pool = request.cr, request.uid, request.context, request.registry
        #abrir reports
        request.env['cashflow.wizard'].open_view_cashflow_reports()

        #metodo igual ao d cima
        cashflow_obj = request.env['cashflow.report']

        if self._uid != None and self._uid==3:
            return request.redirect("/")
        filtrou=False
        filtrou_journal=False
        domain = []
        filtro_data_inicio=''
        filtro_data_fim=''
        filtro_diario=False
        filtro_diario_name = ''
        date_start = ''
        date_end = ''
        if 'journal_id' in post and post['journal_id'] and post['journal_id']!=False and post['journal_id']!='Diario...' and post['journal_id']!='Journal...':
            filtrou_journal=True
            post_diario = str(post['journal_id'])
            filtro_diario_name = post_diario
            self._cr.execute("select id from account_journal where name='"+str(post_diario)+"'")
            id_diarios=self._cr.fetchone()
            if id_diarios!=None and id_diarios[0]!=None:
                filtro_diario=id_diarios[0]


########################################
        if ('date_dia' in post and post['date_dia'] and (post['date_dia']!=False or post['date_dia']!='')) and ('date_end' not in post or post['date_end']==''):
            filtrou=True
            date_start = datetime.strptime((post['date_dia']), "%Y-%m-%d")
            date_start=str(date_start.date())
            # date_end= datetime.strptime((post['date_end']), "%Y-%m-%d")
            # date_end=str(date_end.date())
            filtro_data_inicio=date_start
            filtro_data_fim=''

        if ('date_end' in post and post['date_end'] and post['date_end']!=False and post['date_end']!='') and ('date_dia' not in post or post['date_dia']==''):
            filtrou=True
            date_end= datetime.strptime((post['date_end']), "%Y-%m-%d")
            date_end=str(date_end.date())
            filtro_data_inicio=''
            filtro_data_fim=date_end

        if ('date_end' in post and post['date_end'] and post['date_end']!=False and post['date_end']!='') and ('date_dia' in post and post['date_dia'] and post['date_dia']!=False and post['date_dia']!=''):
            filtrou=True
            date_start = datetime.strptime((post['date_dia']), "%Y-%m-%d")
            date_start=str(date_start.date())
            date_end= datetime.strptime((post['date_end']), "%Y-%m-%d")
            date_end=str(date_end.date())
            filtro_data_inicio=date_start
            filtro_data_fim=date_end

        # if date_start=='' and date_end=='':
        #     date_start= "01-01-"+str(ano_atual)
        #     date_end= "31-12-"+str(ano_atual)
        #     date_start_domain= str(ano_atual)+"-01-01"
        #     date_end_domain= str(ano_atual)+"-12-31"

##########################################
        # if ('date_dia' in post and post['date_dia'] and (post['date_dia']!=False or post['date_dia']!='')) or ('date_end' in post and post['date_end'] and (post['date_end']!=False or post['date_end']!='')):
        #     filtrou=True
        #     date_start = datetime.strptime((post['date_dia']), "%Y-%m-%d")
        #     date_start=str(date_start.date())
        #     date_end= datetime.strptime((post['date_end']), "%Y-%m-%d")
        #     date_end=str(date_end.date())
        #     filtro_data_inicio=date_start
        #     filtro_data_fim=date_end

        if filtrou==True and filtrou_journal==False:
            if date_end =='' and date_start != '':
                domain = [('date','>=',date_start)]

            if date_end !='' and date_start == '':
                domain = [('date','<=',date_end)]

            if date_end !='' and date_start != '':
                domain = [('date','<=',date_end),('date','>=',date_start)]

        if filtrou==True and filtrou_journal==True:
            if date_end =='' and date_start != '':
                domain = [('journal_id','=', filtro_diario),('date','>=',date_start)]

            if date_end !='' and date_start == '':
                domain = [('journal_id','=', filtro_diario),('date','<=',date_end)]

            if date_end !='' and date_start != '':
                domain = [('journal_id','=', filtro_diario),('date','<=',date_end),('date','>=',date_start)]

        if filtrou==False and filtrou_journal==True:
            domain = [('journal_id','=', filtro_diario)]


        cashflow_obj_ids = cashflow_obj.search(domain)
        #cashflow_obj_browse = cashflow_obj.browse(self._cr, self._uid, cashflow_obj_ids, context=self._context)

        lista_diarios = []
        lista_diarios_names = []
        self._cr.execute("select distinct(journal_id),date from cashflow_report order by date asc " )
        if filtrou==True and filtrou_journal==False:
            if date_end =='' and date_start != '':
                self._cr.execute("select distinct(journal_id),date from cashflow_report where date >= '"+str(date_start)+"' order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select distinct(journal_id),date from cashflow_report where date <= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select distinct(journal_id),date from cashflow_report where date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' order by date asc" )

        if filtrou==True and filtrou_journal==True:
            if date_end =='' and date_start != '':
                self._cr.execute("select distinct(journal_id),date from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select distinct(journal_id),date from cashflow_report where journal_id="+str(filtro_diario)+" and date <= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select distinct(journal_id),date from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' order by date asc" )


        if filtrou==False and filtrou_journal==True:
            self._cr.execute("select distinct(journal_id),date from cashflow_report where journal_id="+str(filtro_diario)+" order by date asc" )
        diarios=self._cr.fetchall()
        for d in diarios:
            self._cr.execute("select type from account_journal where id="+str(d[0]))
            tipo_diario_caixa_ou_banco=self._cr.fetchone()
            if tipo_diario_caixa_ou_banco!=None and tipo_diario_caixa_ou_banco[0]!=None and tipo_diario_caixa_ou_banco[0] in ('bank','cash'):
                lista_diarios.append(d[0])

        lista_datas = []
        self._cr.execute("select distinct(date) from cashflow_report order by date asc " )
        if filtrou==True and filtrou_journal==False:
            if date_end =='' and date_start != '':
                self._cr.execute("select distinct(date) from cashflow_report where date >= '"+str(date_start)+"' order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select distinct(date) from cashflow_report where date <= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select distinct(date) from cashflow_report where date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' order by date asc" )

        if filtrou==True and filtrou_journal==True:
            if date_end =='' and date_start != '':
                self._cr.execute("select distinct(date) from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select distinct(date) from cashflow_report where journal_id="+str(filtro_diario)+" and date <= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select distinct(date) from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' order by date asc" )
        if filtrou==False and filtrou_journal==True:
            self._cr.execute("select distinct(date) from cashflow_report where journal_id="+str(filtro_diario)+" order by date asc" )
        datas=self._cr.fetchall()
        for d in datas:
            lista_datas.append(str(d[0]))
        lista_datas = str(lista_datas).replace("'","").replace("[","").replace("]","")

        lista_entradas = []
        self._cr.execute("select sum(entrada) from cashflow_report group by date order by date")
        if filtrou==True and filtrou_journal==False:
            if date_end =='' and date_start != '':
                self._cr.execute("select sum(entrada) from cashflow_report where date >= '"+str(date_start)+"' group by date order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select sum(entrada) from cashflow_report where date <= '"+str(date_end)+"' group by date order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select sum(entrada) from cashflow_report where date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' group by date order by date asc" )

        if filtrou==True and filtrou_journal==True:
            if date_end =='' and date_start != '':
                self._cr.execute("select sum(entrada) from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' group by date order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select sum(entrada) from cashflow_report where journal_id="+str(filtro_diario)+" and date <= '"+str(date_end)+"' group by date order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select sum(entrada) from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' group by date order by date asc" )
        if filtrou==False and filtrou_journal==True:
            self._cr.execute("select sum(entrada) from cashflow_report where journal_id="+str(filtro_diario)+" group by date order by date asc" )
        entradas=self._cr.fetchall()
        for e in entradas:
            lista_entradas.append(int(e[0]))
        lista_entradas = str(lista_entradas).replace("'","").replace("[","").replace("]","")

        lista_saidas = []
        self._cr.execute("select sum(saida) from cashflow_report group by date order by date")
        if filtrou==True and filtrou_journal==False:
            if date_end =='' and date_start != '':
                self._cr.execute("select sum(saida) from cashflow_report where date >= '"+str(date_start)+"' group by date order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select sum(saida) from cashflow_report where date <= '"+str(date_end)+"' group by date order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select sum(saida) from cashflow_report where date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' group by date order by date asc" )

        if filtrou==True and filtrou_journal==True:
            if date_end =='' and date_start != '':
                self._cr.execute("select sum(saida) from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' group by date order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select sum(saida) from cashflow_report where journal_id="+str(filtro_diario)+" and date <= '"+str(date_end)+"' group by date order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select sum(saida) from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' group by date order by date asc" )
        if filtrou==False and filtrou_journal==True:
            self._cr.execute("select sum(saida) from cashflow_report where journal_id="+str(filtro_diario)+" group by date order by date asc" )
        saidas=self._cr.fetchall()
        for s in saidas:
            lista_saidas.append(int(s[0]))
        lista_saidas = str(lista_saidas).replace("'","").replace("[","").replace("]","")

        lista_saldos = []
        saldo_valor=0
        self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report group by date order by date")
        if filtrou==True and filtrou_journal==False:
            if date_end =='' and date_start != '':
                self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report where date >= '"+str(date_start)+"' group by date order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report where date <= '"+str(date_end)+"' group by date order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report where date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' group by date order by date asc" )

        if filtrou==True and filtrou_journal==True:
            if date_end =='' and date_start != '':
                self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' group by date order by date asc" )#+"' and date<= '"+str(date_end)+"' order by date asc" )

            if date_end !='' and date_start == '':
                self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report where journal_id="+str(filtro_diario)+" and date <= '"+str(date_end)+"' group by date order by date asc" )

            if date_end !='' and date_start != '':
                self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report where journal_id="+str(filtro_diario)+" and date >= '"+str(date_start)+"' and date<= '"+str(date_end)+"' group by date order by date asc" )
        if filtrou==False and filtrou_journal==True:
            self._cr.execute("select sum(entrada)-sum(saida) from cashflow_report where journal_id="+str(filtro_diario)+" group by date order by date asc" )
        saldos=self._cr.fetchall()
        for sa in saldos:
            saldo_valor+=sa[0]
            lista_saldos.append(int(saldo_valor))
        lista_saldos = str(lista_saldos).replace("'","").replace("[","").replace("]","")


        lista_tipos = []
        self._cr.execute("select date, tipo, entrada, saida from cashflow_report group by date, tipo,entrada,saida,id order by date asc, id asc " )
        registos=self._cr.fetchall()
        for l in registos:
            lista_tipos.append(str(l[1]))

        ##################
        #DADODS GRAFICO 4#
        ##################
        accounts_obj = request.env['account.account']
        #1 - vendas brutas
        vendas_brutas=0
        tipo_fluxo_vendas_brutas=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'1')])
        for c in accounts_obj_ids:
            tipo_fluxo_vendas_brutas=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            vendas_brutas1=self._cr.fetchone()
            if vendas_brutas1 != None and vendas_brutas1[0] != None:
                vendas_brutas+=vendas_brutas1[0]
        #7 - despesas de vendas
        despesas_vendas=0
        tipo_fluxo_despesas_vendas=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '7')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_vendas=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_vendas1=self._cr.fetchone()
            if despesas_vendas1 != None and despesas_vendas1[0] != None:
                despesas_vendas+=despesas_vendas1[0]
        #8 - custos operacao
        custos_operacao=0
        tipo_fluxo_custos_operacao=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '8')])
        for c in accounts_obj_ids:
            tipo_fluxo_custos_operacao=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            custos_operacao1=self._cr.fetchone()
            if custos_operacao1 != None and custos_operacao1[0] != None:
                custos_operacao+=custos_operacao1[0]
        #9 - despesas administrativas
        despesas_admin=0
        tipo_fluxo_despesas_admin=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '9')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_admin=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_admin1=self._cr.fetchone()
            if despesas_admin1 != None and despesas_admin1[0] != None:
                despesas_admin+=despesas_admin1[0]
        #10 - despesas tributarias
        despesas_tributarias=0
        tipo_fluxo_despesas_tributarias=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '10')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_tributarias=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_tributarias1=self._cr.fetchone()
            if despesas_tributarias1 != None and despesas_tributarias1[0] != None:
                despesas_tributarias+=despesas_tributarias1[0]
        #2 - Outras entradas
        outras_entradas=0
        tipo_fluxo_outras_entradas=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'2')])
        for c in accounts_obj_ids:
            tipo_fluxo_outras_entradas=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            outras_entradas1=self._cr.fetchone()
            if outras_entradas1 != None and outras_entradas1[0] != None:
                outras_entradas+=outras_entradas1[0]
        #11 - outras saidas
        outras_saidas=0
        tipo_fluxo_outras_saidas=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '11')])
        for c in accounts_obj_ids:
            tipo_fluxo_outras_saidas=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            outras_saidas1=self._cr.fetchone()
            if outras_saidas1 != None and outras_saidas1[0] != None:
                outras_saidas+=outras_saidas1[0]
        #3 - financeiras
        financeirrras=0
        tipo_fluxo_financeirrras=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '3')])
        for c in accounts_obj_ids:
            tipo_fluxo_financeirrras=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            financeirrras1=self._cr.fetchone()
            if financeirrras1 != None and financeirrras1[0] != None:
                financeirrras+=financeirrras1[0]
        #12 - despesas finanaceiras
        despesas_finan=0
        tipo_fluxo_despesas_finan=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'12')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_finan=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_finan1=self._cr.fetchone()
            if despesas_finan1 != None and despesas_finan1[0] != None:
                despesas_finan+=despesas_finan1[0]
        #4 - antecipacoes
        antecipacoes=0
        tipo_fluxo_antecipacoes=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '4')])
        for c in accounts_obj_ids:
            tipo_fluxo_antecipacoes=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            antecipacoes1=self._cr.fetchone()
            if antecipacoes1 != None and antecipacoes1[0] != None:
                antecipacoes+=antecipacoes1[0]
        #13 - despesas de antecipacoes
        despesas_antecipacoes=0
        tipo_fluxo_despesas_antecipacoes=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'13')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_antecipacoes=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_antecipacoes1=self._cr.fetchone()
            if despesas_antecipacoes1 != None and despesas_antecipacoes1[0] != None:
                despesas_antecipacoes+=despesas_antecipacoes1[0]
        #5 - Emprestimos e finan
        empre_financ=0
        tipo_fluxo_oempre_financ=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '5')])
        for c in accounts_obj_ids:
            tipo_fluxo_oempre_financ=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            empre_financ1=self._cr.fetchone()
            if empre_financ1 != None and empre_financ1[0] != None:
                empre_financ+=empre_financ1[0]
        #14 - amort_emempre_financ1pres
        amort_empres=0
        tipo_fluxo_amort_empres=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'14')])
        for c in accounts_obj_ids:
            tipo_fluxo_amort_empres=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            amort_empres1=self._cr.fetchone()
            if amort_empres1 != None and amort_empres1[0] != None:
                amort_empres+=amort_empres1[0]
        #6 - patrimon
        patrimon=0
        tipo_fluxo_patrimon=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=' ,'6')])
        for c in accounts_obj_ids:
            tipo_fluxo_patrimon=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            patrimon1=self._cr.fetchone()
            if patrimon1 != None and patrimon1[0] != None:
                patrimon+=patrimon1[0]
        #15 - despesas patrim
        despesas_patraimn=0
        tipo_fluxo_despesas_patraimn=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.code','=', '15')])
        for c in accounts_obj_ids:
            tipo_fluxo_despesas_patraimn=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            despesas_patraimn1=self._cr.fetchone()
            if despesas_patraimn1 != None and despesas_patraimn1[0] != None:
                despesas_patraimn+=despesas_patraimn1[0]

        fluxo_operacional=0
        tipo_fluxo_fluxo_operacional=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_operacional')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_operacional=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_operacional1=self._cr.fetchone()
            if fluxo_operacional1 != None and fluxo_operacional1[0] != None:
                fluxo_operacional+=fluxo_operacional1[0]

        fluxo_outros=0
        tipo_fluxo_fluxo_outros=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_outros')],)
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_outros=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_outros1=self._cr.fetchone()
            if fluxo_outros1 != None and fluxo_outros1[0] != None:
                fluxo_outros+=fluxo_outros1[0]

        fluxo_financeiro=0
        tipo_fluxo_fluxo_financeiro=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_financeiro')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_financeiro=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_financeiro1=self._cr.fetchone()
            if fluxo_financeiro1 != None and fluxo_financeiro1[0] != None:
                fluxo_financeiro+=fluxo_financeiro1[0]

        fluxo_antecipa=0
        tipo_fluxo_fluxo_antecipa=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_antecipa')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_antecipa=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_antecipa1=self._cr.fetchone()
            if fluxo_antecipa1 != None and fluxo_antecipa1[0] != None:
                fluxo_antecipa+=fluxo_antecipa1[0]

        fluxo_emp=0
        tipo_fluxo_fluxo_emp=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_emp')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_emp=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_emp1=self._cr.fetchone()
            if fluxo_emp1 != None and fluxo_emp1[0] != None:
                fluxo_emp+=fluxo_emp1[0]

        fluxo_patrimoniais=0
        tipo_fluxo_fluxo_patrimoniais=0
        accounts_obj_ids = accounts_obj.search([('cashflow_type_id.type','=', 'fluxo_patrimoniais')])
        for c in accounts_obj_ids:
            tipo_fluxo_fluxo_patrimoniais=c.cashflow_type_id.type
            self._cr.execute("SELECT COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance "
            +"FROM account_move_line l, account_move m WHERE l.account_id = "+str(c.id)+"  AND l.move_id = m.id AND m.state = 'posted'" )
            fluxo_patrimoniais1=self._cr.fetchone()
            if fluxo_patrimoniais1 != None and fluxo_patrimoniais1[0] != None:
                fluxo_patrimoniais+=fluxo_patrimoniais1[0]

        values = {
            'tipo_fluxo_fluxo_patrimoniais':tipo_fluxo_fluxo_patrimoniais,
            'tipo_fluxo_fluxo_emp':tipo_fluxo_fluxo_emp,
            'tipo_fluxo_fluxo_antecipa':tipo_fluxo_fluxo_antecipa,
            'tipo_fluxo_fluxo_financeiro':tipo_fluxo_fluxo_financeiro,
            'tipo_fluxo_fluxo_outros':tipo_fluxo_fluxo_outros,
            'tipo_fluxo_fluxo_operacional':tipo_fluxo_fluxo_operacional,
            'tipo_fluxo_despesas_patraimn':tipo_fluxo_despesas_patraimn,
            'tipo_fluxo_patrimon':tipo_fluxo_patrimon,
            'tipo_fluxo_amort_empres':tipo_fluxo_amort_empres,
            'tipo_fluxo_oempre_financ':tipo_fluxo_oempre_financ,
            'tipo_fluxo_despesas_antecipacoes':tipo_fluxo_despesas_antecipacoes,
            'tipo_fluxo_antecipacoes':tipo_fluxo_antecipacoes,
            'tipo_fluxo_despesas_finan':tipo_fluxo_despesas_finan,
            'tipo_fluxo_financeirrras':tipo_fluxo_financeirrras,
            'tipo_fluxo_outras_saidas':tipo_fluxo_outras_saidas,
            'tipo_fluxo_outras_entradas':tipo_fluxo_outras_entradas,
            'tipo_fluxo_despesas_tributarias':tipo_fluxo_despesas_tributarias,
            'tipo_fluxo_despesas_admin':tipo_fluxo_despesas_admin,
            'tipo_fluxo_custos_operacao':tipo_fluxo_custos_operacao,
            'tipo_fluxo_despesas_vendas':tipo_fluxo_despesas_vendas,
            'tipo_fluxo_vendas_brutas':tipo_fluxo_vendas_brutas,
            'fluxo_patrimoniais':fluxo_patrimoniais,
            'fluxo_emp':fluxo_emp,
            'fluxo_antecipa':fluxo_antecipa,
            'fluxo_financeiro':fluxo_financeiro,
            'fluxo_outros':fluxo_outros,
            'fluxo_operacional':fluxo_operacional,
            'filtro_data_inicio': filtro_data_inicio,
            'filtro_data_fim': filtro_data_fim,
            'filtro_diario': filtro_diario_name,
            'journal_id_selection': lista_diarios,
            'outras_entradas': outras_entradas,
            'outras_saidas': outras_saidas,
            'financeirrras': financeirrras,
            'despesas_finan':despesas_finan,
            'antecipacoes':antecipacoes,
            'despesas_antecipacoes': despesas_antecipacoes,
            'empre_financ':empre_financ,
            'amort_empres': amort_empres,
            'patrimon':patrimon,
            'despesas_patraimn':despesas_patraimn,
            'despesas_tributarias':despesas_tributarias,
            'despesas_admin':despesas_admin,
            'custos_operacao':custos_operacao,
            'despesas_vendas':despesas_vendas,
            'vendas_brutas':vendas_brutas,
            'saldo': lista_saldos,
            'saidas': lista_saidas,
            'entradas': lista_entradas,
            'categorias': lista_tipos,
            'datas': lista_datas,
            'registos': cashflow_obj_ids,
        }

        return request.render("opencloud_cashflows.get_mapas", values)
