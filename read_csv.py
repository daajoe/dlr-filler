import csv
from datetime import datetime, date
from collections import OrderedDict
from utils import days2workingdays


class Timesheet(object):
    def __init__(self, filename='data.csv', daily_contract_hours=8):
        self.filename = filename
        self.daily_contract_hours = daily_contract_hours

    @staticmethod
    def quarter(x):
        return round(x * 4) / 4

    @staticmethod
    def compute_dates(values, row):
        date = datetime.strptime(row['date'], '%d.%m.%Y')
        start_tm = datetime.strptime(row['start'], '%H:%M')
        end_tm = datetime.strptime(row['end'], '%H:%M')
        break_tm = datetime.strptime(row['break'], '%H:%M')
        null = datetime.strptime("0:00", '%H:%M')
        delta = end_tm - start_tm
        delta2 = break_tm - null
        return Timesheet.quarter(float((delta - delta2).seconds) / 3600 + values.get(date, 0)), date

    def read_csv(self):
        with open(self.filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')

            entries = {}
            absence = {}
            others = {}
            for row in reader:
                if not row['type'] and (not row['client'] or row['client'].upper() == 'DLR'):
                    val, date = Timesheet.compute_dates(entries, row)
                    entries[date] = val
                elif row['client'] and row['client'].upper() != 'DLR':
                    val, date = Timesheet.compute_dates(others, row)
                    others[date] = val
                else:
                    date = datetime.strptime(row['date'], '%d.%m.%Y')
                    absence[date] = row['type']
            return OrderedDict(sorted(entries.items(), key=lambda t: t[0])), absence, others

    @staticmethod
    def get_month_year(values):
        years = set()
        months = set()
        for date in values:
            years.add(date.year)
            months.add(date.month)
        return sorted(years), sorted(months)

    def __compute_daily_hours(self):
        project_hours, absence_hours, other_hours = self.read_csv()
        absence_hours = {k: float(self.daily_contract_hours) for k, v in absence_hours.iteritems()}

        productive_hours = {}
        for k in set(other_hours.keys() + project_hours.keys()):
            productive_hours[k] = project_hours.get(k, 0) + other_hours.get(k, 0)

        years, months = Timesheet.get_month_year(project_hours)

        non_working_days = filter(lambda x: x[1] == False, days2workingdays(years, months).iteritems())
        for day, _ in non_working_days:
            project_hours[day] = other_hours[day] = productive_hours[day] = absence_hours[day] = 'X'
        # print absence_hours

        return {'years': years, 'months': months, 'project_hours': project_hours, 'other_hours': other_hours,
                'productive_hours': productive_hours, 'absence_hours': absence_hours}

    def __compute_monthly_hours(self, values):
        ret = {}
        for year in values['years']:
            for month in values['months']:
                current_month = lambda d: dict(filter(
                    lambda x: x[0].year == year and x[0].month == month and (type(x[1]) in (int, float) or x[1] == 'X'),
                    d.iteritems()))
                current_month_v = lambda d: dict(filter(
                    lambda x: x[0].year == year and x[0].month == month and type(x[1]) in (int, float),
                    d.iteritems()))
                d = {'project_hours': current_month(values['project_hours']),
                     'other_hours': current_month(values['other_hours']),
                     'productive_hours': current_month(values['productive_hours']),
                     'absence_hours': current_month(values['absence_hours']),
                     'total_project_hours': sum([e for e in current_month_v(values['project_hours']).itervalues()]),
                     'total_other_hours': sum([e for e in current_month_v(values['other_hours']).itervalues()]),
                     'total_productive_hours': sum([e for e in current_month_v(values['productive_hours']).itervalues()]),
                     'total_absence_hours': sum([e for e in current_month_v(values['absence_hours']).itervalues()])}
                ret[(year, month)] = d
        return ret

    def compute_hours(self):
        values = self.__compute_daily_hours()
        return self.__compute_monthly_hours(values)
