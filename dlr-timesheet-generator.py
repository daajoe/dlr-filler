#!/usr/bin/env python
# TODO: add GPL
from read_csv import Timesheet
from collections import OrderedDict

def read_config():
    from ConfigParser import SafeConfigParser

    config = SafeConfigParser()
    config.read('dlr-filler.ini')
    return config

config = read_config()
state = config.get('main', 'state')
data_file = config.get('main', 'data_file')
topic = config.get('project', 'topic')
number = config.get('project', 'number')
contract_hours = config.get('user', 'contract_hours')
others = config.get('user', 'others')
name = config.get('user', 'name')
filename = 'data.csv'

# 0 .. None
# 1 .. remaining

# TODO: put commandline parameter handling
# TODO: cleaning

t = Timesheet(filename=filename,daily_contract_hours=contract_hours)


from pdf_output import PDFMonthlyTimeSheet

o = PDFMonthlyTimeSheet(topic, name, number)


for k, values in OrderedDict(sorted(t.compute_hours().items(), key=lambda t: t[0])).iteritems():
    o.fill_pdf(values=values,month=k[1])

o.write_pdf()
exit(0)