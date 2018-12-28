from odoo import fields,models,api, tools, SUPERUSER_ID
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    @api.model
    def retrieve_sales_dashboard(self):
        """ Fetch data to setup Sales Dashboard """
        result = {
            'meeting': {
                'today': 0,
                'next_7_days': 0,
            },
            'activity': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'closing': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'done': {
                'this_month': 0,
                'last_month': 0,
            },
            'won': {
                'this_month': 0,
                'last_month': 0,
            },
            'nb_opportunities': 0,
        }
        
        opportunities = self.search([('type', '=', 'opportunity'), ('user_id', '=', self._uid)])
        if self.env.user.has_group('head_of_sale.group_head_of_sale'):
            opportunities = self.search([('type', '=', 'opportunity')])
        for opp in opportunities:
            # Expected closing
            if opp.date_deadline:
                date_deadline = fields.Date.from_string(opp.date_deadline)
                if date_deadline == date.today():
                    result['closing']['today'] += 1
                if date.today() <= date_deadline <= date.today() + timedelta(days=7):
                    result['closing']['next_7_days'] += 1
                if date_deadline < date.today():
                    result['closing']['overdue'] += 1
            # Next activities
            if opp.next_activity_id and opp.date_action:
                date_action = fields.Date.from_string(opp.date_action)
                if date_action == date.today():
                    result['activity']['today'] += 1
                if date.today() <= date_action <= date.today() + timedelta(days=7):
                    result['activity']['next_7_days'] += 1
                if date_action < date.today():
                    result['activity']['overdue'] += 1
            # Won in Opportunities
            if opp.date_closed:
                date_closed = fields.Date.from_string(opp.date_closed)
                if date.today().replace(day=1) <= date_closed <= date.today():
                    if opp.planned_revenue:
                        result['won']['this_month'] += opp.planned_revenue
                elif  date.today() + relativedelta(months=-1, day=1) <= date_closed < date.today().replace(day=1):
                    if opp.planned_revenue:
                        result['won']['last_month'] += opp.planned_revenue

        result['nb_opportunities'] = len(opportunities)

        # crm.activity is a very messy model so we need to do that in order to retrieve the actions done.
        
        self._cr.execute("""
            SELECT
                m.id,
                m.subtype_id,
                m.date,
                l.user_id,
                l.type
            FROM mail_message M
                LEFT JOIN crm_lead L ON (M.res_id = L.id)
                INNER JOIN crm_activity A ON (M.subtype_id = A.subtype_id)
            WHERE
                (M.model = 'crm.lead') AND (L.user_id = %s) AND (L.type = 'opportunity')
        """, (self._uid,))
        activites_done = self._cr.dictfetchall()
        if self.env.user.has_group('head_of_sale.group_head_of_sale'):
            self._cr.execute("""
                SELECT
                    m.id,
                    m.subtype_id,
                    m.date,
                    l.user_id,
                    l.type
                FROM mail_message M
                    LEFT JOIN crm_lead L ON (M.res_id = L.id)
                    INNER JOIN crm_activity A ON (M.subtype_id = A.subtype_id)
                WHERE
                    (M.model = 'crm.lead') AND (L.type = 'opportunity')
            """)
            activites_done = self._cr.dictfetchall()

        for activity in activites_done:
            if activity['date']:
                date_act = fields.Date.from_string(activity['date'])
                if date.today().replace(day=1) <= date_act <= date.today():
                    result['done']['this_month'] += 1
                elif date.today() + relativedelta(months=-1, day=1) <= date_act < date.today().replace(day=1):
                    result['done']['last_month'] += 1

        # Meetings
        min_date = fields.Datetime.now()
        max_date = fields.Datetime.to_string(datetime.now() + timedelta(days=8))
        meetings_domain = [
            ('start', '>=', min_date),
            ('start', '<=', max_date),
            ('partner_ids', 'in', [self.env.user.partner_id.id])
        ]
        if self.env.user.has_group('head_of_sale.group_head_of_sale'):
            meetings_domain = [
                ('start', '>=', min_date),
                ('start', '<=', max_date),
            ]
        meetings = self.env['calendar.event'].search(meetings_domain)
        for meeting in meetings:
            if meeting['start']:
                start = datetime.strptime(meeting['start'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
                if start == date.today():
                    result['meeting']['today'] += 1
                if date.today() <= start <= date.today() + timedelta(days=7):
                    result['meeting']['next_7_days'] += 1

        result['done']['target'] = self.env.user.target_sales_done
        result['won']['target'] = self.env.user.target_sales_won
        result['currency_id'] = self.env.user.company_id.currency_id.id

        return result
