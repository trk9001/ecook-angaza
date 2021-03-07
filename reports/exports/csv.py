import csv
import os
import math
from django.http import HttpResponse

from .base import Base
from reports.models import UnitNumber


class Csv(Base):
    def export(self, data):
        total_cost_list = []
        file_name = 'data.csv'
        file_to_write = f'assets/files/{file_name}'

        if os.path.exists(file_to_write):
            os.remove(file_to_write)

        with open(file_to_write, 'w') as file:
            fieldnames = [
                'Serial Number',
                'Date',
                'Daily Power Consumption (KWh)',
                'Cost ($)',
                'Left Stove Cooking Time',
                'Right Stove Cooking Time',
                'Daily Cooking Time',
                'Stove On/Off Count',
                'Average Power Consumption per use',
                'Average Cooking time per use'
            ]
            write = csv.DictWriter(file, fieldnames=fieldnames)

            write.writeheader()

            if data.count() > 0:
                for item in data:
                    obj = UnitNumber.objects.get(unit_number=item.serial_number)

                    try:
                        cost = math.ceil((item.daily_power_consumption * obj.country.cost) * 100) / 100
                        item.cost = cost

                        if cost > 0:
                            total_cost_list.append(cost)
                    except:
                        item.cost = 0.00

                    write.writerow(
                        {
                            'Serial Number': item.serial_number,
                            'Date': item.when_date,
                            'Daily Power Consumption (KWh)': item.daily_power_consumption,
                            'Cost ($)': item.cost,
                            'Left Stove Cooking Time': item.left_stove_cooktime,
                            'Right Stove Cooking Time': item.right_stove_cooktime,
                            'Daily Cooking Time': item.daily_cooking_time,
                            'Stove On/Off Count': item.stove_on_off_count,
                            'Average Power Consumption per use': item.average_power_consumption_per_use,
                            'Average Cooking time per use': item.average_cooking_time_per_use
                        }
                    )

                write.writerow(
                    {
                        'Serial Number': 'Total Items',
                        'Date': data.count(),
                        'Daily Power Consumption (KWh)': sum(
                            [item.daily_power_consumption for item in data]
                        ),
                        'Cost ($)': math.ceil(sum(total_cost_list) * 100) / 100,
                        'Left Stove Cooking Time': sum(
                            [item.left_stove_cooktime for item in data]
                        ),
                        'Right Stove Cooking Time': sum(
                            [item.right_stove_cooktime for item in data]
                        ),
                        'Daily Cooking Time': sum(
                            [item.daily_cooking_time for item in data]
                        )
                    }
                )

        return self.response(file=file_to_write)

    def response(self, file):
        with open(file, 'r') as f:
            response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'inline; filename={os.path.basename(file)}'

            return response
