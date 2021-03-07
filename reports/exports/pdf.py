import math
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse, Http404
from reports.models import UnitNumber
from .base import Base


class Pdf(Base):
    def export(self, data):
        total = {}
        total_cost_list = []
        template = get_template('reports/exports/pdf.html')

        for item in data:
            obj = UnitNumber.objects.get(unit_number=item.serial_number)

            try:
                cost = math.ceil((item.daily_power_consumption * obj.country.cost) * 100) / 100
                item.cost = cost

                if cost > 0:
                    total_cost_list.append(cost)
            except:
                item.cost = 0.00

        total['total_items'] = data.count()
        total['daily_power_consumption'] = sum(
            [item.daily_power_consumption for item in data]
        )
        total['left_stove_cooktime'] = sum(
            [item.left_stove_cooktime for item in data]
        )
        total['right_stove_cooktime'] = sum(
            [item.right_stove_cooktime for item in data]
        )
        total['daily_cooking_time'] = sum(
            [item.daily_cooking_time for item in data]
        )
        total['total_cost'] = math.ceil(sum(total_cost_list) * 100) / 100

        html_string = template.render({
            'data': data,
            'total': total
        })
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode('utf-8')), result)

        if pdf.err:
            return self.response(file=None)

        return self.response(file=result)

    def response(self, file):
        if file is not None:
            return HttpResponse(file.getvalue(), content_type='application/pdf')

        return Http404()
