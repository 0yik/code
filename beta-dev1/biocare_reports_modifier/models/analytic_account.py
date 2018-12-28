# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from dateutil.relativedelta import relativedelta


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def get_year_increment(self, st_date):
        return fields.Date.from_string(st_date) + relativedelta(months=+11)

    def get_year_increment_dynamic(self, st_date, end_date):
        return fields.Date.from_string(end_date)

AnalyticAccount()

class BoAccountAnalyticLine(models.Model):
    _inherit = 'bo.account.analytic.line'


    def get_data_dynamic_report(self):
        ## function that report dynamic for give criteria
        data = []
        st_date = ''
        en_date = ''
        line_obj = self
        if not st_date and not en_date:
            st_date = fields.Date.from_string(self.tree_interval_date1)
            en_date = st_date + relativedelta(months=+12)
            # en_date = st_date + relativedelta(years=1)
            # en_date = st_date + relativedelta(days=+365)
        if not st_date and not en_date:
            raise exceptions.ValidationError(
                _('Start date and end date not found. Please contact your admin.'))
        # when interval is twice weekly then we will find the difference
        # for the two date
        interval = 0
        increment_type = '' # define day, month for increment date next year
        if line_obj.book_interval == 'weekly':
            interval = 7
            increment_type = 'days'
            en_date = st_date + relativedelta(months=+11)
        elif line_obj.book_interval == 'twice_weekly':
            diff = fields.Date.from_string(line_obj.tree_interval_date2) - fields.Date.from_string(line_obj.tree_interval_date1)
            interval = diff.days
            increment_type = 'days'
            en_date = st_date + relativedelta(months=+11)
        elif line_obj.book_interval == 'fortnightly':
            interval = 15
            increment_type = 'days'
            en_date = st_date + relativedelta(months=+11)
        elif line_obj.book_interval == 'monthly':
            interval = 1
            increment_type = 'months'
        elif line_obj.book_interval == 'bi_mothly':
            interval = 2
            increment_type = 'months'
        elif line_obj.book_interval == 'quarterly':
            interval = 3
            increment_type = 'months'
        else:
            interval = 6
            increment_type = 'months'
        next_interval_date = st_date
        next_interval_date_month_get = st_date
        track_key = {}
        array_index = 0
        while (next_interval_date_month_get < en_date ):
            if next_interval_date_month_get.strftime("%b-%y") not in track_key:
                data.append({'months': next_interval_date_month_get.strftime("%b-%y"),
                         'dates': []
                         })
                track_key[next_interval_date_month_get.strftime("%b-%y")] = array_index
                array_index +=1
                next_interval_date_month_get = next_interval_date_month_get + relativedelta(months=+1)
        count = 1

        while (next_interval_date < en_date):
            if next_interval_date.strftime("%b-%y") not in track_key:
                data.append({'dates': [{str(count): next_interval_date.strftime("%d")}],
                             'months': next_interval_date.strftime("%b-%y")
                                 })
                track_key[next_interval_date.strftime("%b-%y")] = array_index
                array_index +=1
                if increment_type == 'days':
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(days=+interval)
                    next_month = next_interval_date.strftime("%b")
                else:
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(months=+interval)
                    next_month = next_interval_date.strftime("%b")

                if previous_month != next_month:
                   count = 1
                else:
                   count += 1
            else:
                which_key = track_key[next_interval_date.strftime("%b-%y")]
                data[which_key]['dates'].append({str(count): next_interval_date.strftime("%d")})
                if increment_type == 'days':
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(days=+interval)
                    next_month = next_interval_date.strftime("%b")
                else:
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(months=+interval)
                    next_month = next_interval_date.strftime("%b")
                if previous_month != next_month:
                    count = 1
                else:
                    count += 1

        '''
        while (next_interval_date < en_date):
                print "ddddd", track_key[next_interval_date.strftime("%b-%y")]
                which_key = track_key[next_interval_date.strftime("%b-%y")]
                data[which_key]['dates'].append({str(count): next_interval_date.strftime("%d")})
                if increment_type == 'days':
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(days=+interval)
                    next_month = next_interval_date.strftime("%b")
                else:
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(months=+interval)
                    next_month = next_interval_date.strftime("%b")
                if previous_month != next_month:
                    count = 1
                else:
                    count += 1
        '''
        length_arr = []
        for val in data:
            length_arr.append(len(val['dates']))
        max_length = max(length_arr)
        for val in data:
            while(len(val['dates']) != max_length):
                temp_length = len(val['dates'])
                val['dates'].append({str(temp_length+1): ''})
        data.append({'max_lenght': [a for a in range(max_length+1)] , 'months': '', 'dates': []})

        return data

    def line_data(self, form_data):
        ## function that report dynamic for give criteria
        data = []
        st_date = form_data['form']['start_date']
        en_date = form_data['form']['end_date']
        line_obj = self
        if st_date and en_date:
            st_date = fields.Date.from_string(st_date)
            # en_date = st_date + relativedelta(months=+12)
            en_date = fields.Date.from_string(en_date)
        if not st_date and not en_date:
            st_date = fields.Date.from_string(line_obj.tree_interval_date1)
            en_date = st_date + relativedelta(months=+12)
        if not st_date and not en_date:
            raise exceptions.ValidationError(
                _('Start date and end date not found. Please contact your admin.'))
        # when interval is twice weekly then we will find the difference
        # for the two date
        interval = 0
        increment_type = '' # define day, month for increment date next year
        if line_obj.book_interval == 'weekly':
            interval = 7
            increment_type = 'days'
        elif line_obj.book_interval == 'twice_weekly':
            diff = fields.Date.from_string(line_obj.tree_interval_date2) - fields.Date.from_string(line_obj.tree_interval_date1)
            interval = diff.days
            increment_type = 'days'
        elif line_obj.book_interval == 'fortnightly':
            interval = 15
            increment_type = 'days'
        elif line_obj.book_interval == 'monthly':
            interval = 1
            increment_type = 'months'
        elif line_obj.book_interval == 'bi_mothly':
            interval = 2
            increment_type = 'months'
        elif line_obj.book_interval == 'quarterly':
            interval = 3
            increment_type = 'months'
        else:
            interval = 6
            increment_type = 'months'
        next_interval_date = st_date
        next_interval_date_month_get = st_date
        track_key = {}
        array_index = 0
        while (next_interval_date_month_get < en_date ):
            if next_interval_date_month_get.strftime("%b-%y") not in track_key:
                if not len(track_key) == 12:
                    data.append({'months': next_interval_date_month_get.strftime("%b-%y"),
                             'dates': []
                             })
                    track_key[next_interval_date_month_get.strftime("%b-%y")] = array_index
                    array_index +=1
                    next_interval_date_month_get = next_interval_date_month_get + relativedelta(months=+1)
        count = 1
        while (next_interval_date < en_date):
            if next_interval_date.strftime("%b-%y") not in track_key:
                data.append({'dates': [{str(count): next_interval_date.strftime("%d")}],
                             'months': next_interval_date.strftime("%b-%y")
                                 })
                track_key[next_interval_date.strftime("%b-%y")] = array_index
                array_index +=1
                if increment_type == 'days':
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(days=+interval)
                    next_month = next_interval_date.strftime("%b")
                else:
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(months=+interval)
                    next_month = next_interval_date.strftime("%b")

                if previous_month != next_month:
                   count = 1
                else:
                   count += 1
            else:
                which_key = track_key[next_interval_date.strftime("%b-%y")]
                data[which_key]['dates'].append({str(count): next_interval_date.strftime("%d")})
                if increment_type == 'days':
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(days=+interval)
                    next_month = next_interval_date.strftime("%b")
                else:
                    previous_month = next_interval_date.strftime("%b")
                    next_interval_date = next_interval_date + relativedelta(months=+interval)
                    next_month = next_interval_date.strftime("%b")
                if previous_month != next_month:
                    count = 1
                else:
                    count += 1

        length_arr = []
        for val in data:
            length_arr.append(len(val['dates']))
        max_length = max(length_arr)
        for val in data:
            while(len(val['dates']) != max_length):
                temp_length = len(val['dates'])
                val['dates'].append({str(temp_length+1): ''})
        data.append({'max_lenght': [a for a in range(max_length+1)] , 'months': '', 'dates': []})
        return data


