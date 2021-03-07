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
        quick_statistics = {}
        total_cost_list = []
        total_cost = 0.00
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

            total_cost = math.ceil(sum(total_cost_list) * 100) / 100

            quick_statistics['average_cost'] = total_cost / data.count()
            quick_statistics['average_cost'] = math.ceil(quick_statistics['average_cost'] * 100) / 100
            quick_statistics['average_cost_exclude_zero'] = total_cost / len(total_cost_list) \
                if len(total_cost_list) > 0 else 0.00
            quick_statistics['average_cost_exclude_zero'] = math.ceil(
                quick_statistics['average_cost_exclude_zero'] * 100
            ) / 100

            daily_power_consumption_list = [item.daily_power_consumption for item in data]
            daily_power_consumption_list_exclude_zero_list = [item.daily_power_consumption for item in data if
                                                              item.daily_power_consumption > 0]
            quick_statistics['average_power_consumption'] = sum(daily_power_consumption_list) / len(
                daily_power_consumption_list)
            quick_statistics['average_power_consumption'] = math.ceil(
                quick_statistics['average_power_consumption'] * 100) / 100
            quick_statistics['average_power_consumption_exclude_zero'] = sum(
                daily_power_consumption_list_exclude_zero_list) / len(daily_power_consumption_list_exclude_zero_list) \
                if len(daily_power_consumption_list_exclude_zero_list) > 0 else 0
            quick_statistics['average_power_consumption_exclude_zero'] = math.ceil(
                quick_statistics['average_power_consumption_exclude_zero'] * 100) / 100

            left_stove_cooktime = [item.left_stove_cooktime for item in data]
            left_stove_cooktime_exclude_zero_list = [item.left_stove_cooktime for item in data if
                                                     item.left_stove_cooktime > 0]
            quick_statistics['average_left_stove_cooktime'] = sum(left_stove_cooktime) / len(left_stove_cooktime)
            quick_statistics['average_left_stove_cooktime'] = math.ceil(
                quick_statistics['average_left_stove_cooktime'] * 100) / 100
            quick_statistics['average_left_stove_cooktime_exclude_zero'] = sum(
                left_stove_cooktime_exclude_zero_list) / len(left_stove_cooktime_exclude_zero_list) \
                if len(left_stove_cooktime_exclude_zero_list) > 0 else 0
            quick_statistics['average_left_stove_cooktime_exclude_zero'] = math.ceil(
                quick_statistics['average_left_stove_cooktime_exclude_zero'] * 100) / 100

            right_stove_cooktime = [item.right_stove_cooktime for item in data]
            right_stove_cooktime_exclude_zero_list = [item.right_stove_cooktime for item in data if
                                                      item.right_stove_cooktime > 0]
            quick_statistics['average_right_stove_cooktime'] = sum(right_stove_cooktime) / len(right_stove_cooktime)
            quick_statistics['average_right_stove_cooktime'] = math.ceil(
                quick_statistics['average_right_stove_cooktime'] * 100) / 100
            quick_statistics['average_right_stove_cooktime_exclude_zero'] = sum(
                right_stove_cooktime_exclude_zero_list) / len(right_stove_cooktime_exclude_zero_list) \
                if len(right_stove_cooktime_exclude_zero_list) > 0 else 0
            quick_statistics['average_right_stove_cooktime_exclude_zero'] = math.ceil(
                quick_statistics['average_right_stove_cooktime_exclude_zero'] * 100) / 100

            daily_cooking_time = [item.daily_cooking_time for item in data]
            daily_cooking_time_exclude_zero_list = [item.daily_cooking_time for item in data if
                                                    item.daily_cooking_time > 0]
            quick_statistics['average_cooking_time'] = sum(daily_cooking_time) / len(daily_cooking_time)
            quick_statistics['average_cooking_time'] = math.ceil(quick_statistics['average_cooking_time'] * 100) / 100
            quick_statistics['average_cooking_time_exclude_zero'] = sum(daily_cooking_time_exclude_zero_list) / len(
                daily_cooking_time_exclude_zero_list) \
                if len(daily_cooking_time_exclude_zero_list) > 0 else 0
            quick_statistics['average_cooking_time_exclude_zero'] = math.ceil(
                quick_statistics['average_cooking_time_exclude_zero'] * 100) / 100
            quick_statistics['percentage_of_days_used'] = (len(daily_cooking_time_exclude_zero_list) / len(
                daily_cooking_time)) * 100
            quick_statistics['percentage_of_days_used'] = math.ceil(
                quick_statistics['percentage_of_days_used'] * 100) / 100

            stove_on_off_count = [item.stove_on_off_count for item in data]
            stove_on_off_count_exclude_zero_list = [item.stove_on_off_count for item in data if
                                                    item.stove_on_off_count > 0]
            quick_statistics['average_stove_on_off_count'] = sum(stove_on_off_count) / len(stove_on_off_count)
            quick_statistics['average_stove_on_off_count'] = math.ceil(
                quick_statistics['average_stove_on_off_count'] * 100) / 100
            quick_statistics['average_stove_on_off_count_exclude_zero'] = sum(
                stove_on_off_count_exclude_zero_list) / len(stove_on_off_count_exclude_zero_list) \
                if len(stove_on_off_count_exclude_zero_list) > 0 else 0
            quick_statistics['average_stove_on_off_count_exclude_zero'] = math.ceil(
                quick_statistics['average_stove_on_off_count_exclude_zero'] * 100) / 100

            quick_statistics['average_power_consumption_per_use'] = math.ceil(
                (quick_statistics['average_power_consumption'] / quick_statistics['average_stove_on_off_count']) * 100
            ) / 100
            quick_statistics['average_power_consumption_per_use_exclude_zero'] = math.ceil(
                (quick_statistics['average_power_consumption_exclude_zero'] /
                 quick_statistics['average_stove_on_off_count_exclude_zero']) * 100
            ) / 100

            quick_statistics['average_cooking_time_per_use'] = math.ceil(
                (quick_statistics['average_cooking_time'] / quick_statistics['average_stove_on_off_count']) * 100) / 100
            quick_statistics['average_cooking_time_per_use_exclude_zero'] = math.ceil(
                (quick_statistics['average_cooking_time_exclude_zero'] /
                 quick_statistics['average_stove_on_off_count_exclude_zero']) * 100
            ) / 100

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
        total['total_cost'] = total_cost

        html_string = template.render({
            'data': data,
            'total': total,
            'quick_statistics': quick_statistics
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
