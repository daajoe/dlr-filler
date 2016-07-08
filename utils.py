from calendar import TimeEncoding, month_name

# from so:#13037370 by Lauritz V. Thaulow
from datetime import date


def get_month_name(month_no, locale):
    with TimeEncoding(locale) as encoding:
        s = month_name[month_no]
        if encoding is not None:
            s = s.decode(encoding)
        return s


from workalendar.europe import Berlin
from calendar import monthrange


def days2workingdays(years, months):
    cal = Berlin()
    days = {}
    for year in years:
        for month in months:
            for day in xrange(1, monthrange(year, month)[1] + 1):
                d = date(year, month, day)
                days[d] = cal.is_working_day(d)
    return days
