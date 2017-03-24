#!/usr/bin/env python

# TODO: GPL

import StringIO
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
# TODO: change to a4paper
from reportlab.lib.pagesizes import A4
from utils import get_month_name

i = 0


class PDFMonthlyTimeSheet(object):
    def __init__(self, topic, name, number, template="muster.pdf"):
        self.__packet = StringIO.StringIO()
        # create a new PDF with Reportlab
        self.__can = canvas.Canvas(self.__packet, pagesize=A4)
        self.s = 187
        self.offset = 18

        self.topic = topic
        self.name = name
        self.number = number

        self.output = PdfFileWriter()

    def __put_hours(self, values, y_offset):
        for key, value in values.iteritems():
            day = int(key.day)
            i = self.s + self.offset * day
            self.__can.drawString(i, y_offset, str(value))

    def __put_total_hours(self, total_hours, y_offset):
        self.__can.drawString(self.s + self.offset * 32, y_offset, str(total_hours))

    def __put_large_string(self, string, x, y):
        self.__can.setFont("Helvetica", 18)
        self.__can.drawString(x, y, string)
        self.__can.setFont("Helvetica", 8)

    def fill_pdf(self, values, month):
        self.__can.setFont("Helvetica", 12)
        self.__can.rotate(90)
        self.__can.setFont("Helvetica", 8)

        self.__put_hours(values['project_hours'], -325)
        self.__put_hours(values['other_hours'], -343)
        self.__put_hours(values['productive_hours'], -360)
        self.__put_hours(values['absence_hours'], -400)

        self.__put_total_hours(values['total_project_hours'], -325)
        self.__put_total_hours(values['total_other_hours'], -343)
        self.__put_total_hours(values['total_productive_hours'], -360)
        self.__put_total_hours(values['total_absence_hours'], -400)

        self.__put_large_string(self.topic, 68, -190)
        self.__put_large_string(self.name, 345, -235)
        self.__put_large_string(self.number, 640, -70)
        self.__put_large_string(get_month_name(month, "de_DE.UTF-8"), 68, -235)
        self.__can.showPage()

    def write_pdf(self, template="muster.pdf", outputname="destination.pdf"):
        self.__can.save()
        self.__packet.seek(0)
        self.new_pdf = PdfFileReader(self.__packet)
        for page in range(self.new_pdf.numPages):
            existing_pdf = PdfFileReader(file(template, "rb"))
            self.page = existing_pdf.getPage(0)
            self.output.addPage(self.page)
            self.output.getPage(page).mergePage(self.new_pdf.getPage(page))
        output_stream = file(outputname, "wb")
        self.output.write(output_stream)
        output_stream.close()
