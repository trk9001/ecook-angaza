import datetime
from processes.db import Database
from processes.helper import Helper
from processes.vars import ANGAZA_DATA_TYPES


query_params = []
daily_usage_data_query_params = []
db = Database()
helper = Helper()
today = datetime.date.today()
delta = datetime.timedelta(days=1)
from_date = today - delta
unit_numbers = db.get_unitnumbers()

# Iterate all the unit numbers to get data against a unit number.
for unit_number in unit_numbers:
    data = list()
    daily_usage_data_unorganized = list()
    daily_usage_data = {}
    last_usage_data = db.get_usagedata(
        unit_number=str(unit_number['unit_number']),
        data_type='228',
        order_by='when_datetime',
        descending=True,
        limit=1
    )

    # Calling API to Angaza.
    helper. get_usage_data(
        unit_number=unit_number['unit_number'],
        from_when_dt='{}T01:00:00+00:00'.format(from_date),
        to_when_dt='{}T00:00:00+00:00'.format(today),
        variable=data
    )

    if len(data) > 0:
        data = sorted(
            data,
            key=lambda item: item['when']
        )

        # Convert unreadable data from angaza to readable data.
        for item in data:
            when_date = helper.convert_to_datetime(item['when']).date()

            temp_data = {
                'when_date': str(when_date)
            }
            temp_data[ANGAZA_DATA_TYPES[item['type']]] = 0

            for jitem in data:
                if item['type'] == jitem['type']:
                    if item['type'] == 228:
                        temp_data[ANGAZA_DATA_TYPES[item['type']]] = jitem['value']
                    elif when_date == helper.convert_to_datetime(jitem['when']).date():
                        temp_data[ANGAZA_DATA_TYPES[item['type']]] += jitem['value']

            daily_usage_data_unorganized.append(temp_data)
        
        # Get all data for the same date.
        for item in daily_usage_data_unorganized:
            keys = item.keys()

            for i in keys:
                daily_usage_data[i] = item[i]

        # Stove on/off calculation.
        if 'stove_on_off_count' in daily_usage_data:

            if last_usage_data:
                daily_usage_data['stove_on_off_count'] = daily_usage_data['stove_on_off_count'] - float(last_usage_data[0]['data_value'])
        
        # Prepare data to insert in to the DB.
        for item in data:
            query_params.append(
                (
                    unit_number['unit_number'],
                    datetime.datetime.strptime(item['when'], '%Y-%m-%dT%H:%M:%Sz'),
                    item['type'],
                    item['value'],
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                )
            )

        daily_usage_data['daily_power_consumption'] = daily_usage_data['daily_power_consumption'] / 1000 if daily_usage_data['daily_power_consumption'] > 0 else daily_usage_data['daily_power_consumption']
        daily_usage_data['average_power_consumption_per_use'] = 0
        daily_usage_data['average_cooking_time_per_use'] = 0

        daily_usage_data['daily_cooking_time'] = daily_usage_data['left_stove_cooktime'] + daily_usage_data['right_stove_cooktime']

        if 'stove_on_off_count' in daily_usage_data and daily_usage_data['stove_on_off_count'] > 0:
            daily_usage_data['average_power_consumption_per_use'] = daily_usage_data['daily_power_consumption'] / daily_usage_data['stove_on_off_count']
            daily_usage_data['average_cooking_time_per_use'] = daily_usage_data['daily_cooking_time'] / daily_usage_data['stove_on_off_count']

        daily_usage_data_query_params.append(
            (
                unit_number['unit_number'],
                daily_usage_data['average_battery_voltage'] if 'average_battery_voltage' in daily_usage_data else 0.00,
                daily_usage_data['max_battery_voltage'] if 'max_battery_voltage' in daily_usage_data else 0.00,
                daily_usage_data['min_battery_voltage'] if 'min_battery_voltage' in daily_usage_data else 0.00,
                daily_usage_data['battery_critical_state_count'] if 'battery_critical_state_count' in daily_usage_data else 0.00,
                daily_usage_data['one_hour_samples_count'] if 'one_hour_samples_count' in daily_usage_data else 0.00,
                daily_usage_data['lock_mode_entry_count'] if 'lock_mode_entry_count' in daily_usage_data else 0.00,
                daily_usage_data['factory_mode_entry_count'] if 'factory_mode_entry_count' in daily_usage_data else 0.00,
                daily_usage_data['gsm_sync_button_count'] if 'gsm_sync_button_count' in daily_usage_data else 0.00,
                daily_usage_data['stove_on_off_count'] if 'stove_on_off_count' in daily_usage_data else 0.00,
                daily_usage_data['daily_power_consumption'] if 'daily_power_consumption' in daily_usage_data else 0.00,
                daily_usage_data['left_stove_cooktime'] if 'left_stove_cooktime' in daily_usage_data else 0.00,
                daily_usage_data['right_stove_cooktime'] if 'right_stove_cooktime' in daily_usage_data else 0.00,
                daily_usage_data['daily_cooking_time'] if 'daily_cooking_time' in daily_usage_data else 0.00,
                daily_usage_data['average_power_consumption_per_use'] if 'average_power_consumption_per_use' in daily_usage_data else 0.00,
                daily_usage_data['average_cooking_time_per_use'] if 'average_cooking_time_per_use' in daily_usage_data else 0.00,
                daily_usage_data['when_date'] if 'when_date' in daily_usage_data else 0.00,
                daily_usage_data['others'] if 'others' in daily_usage_data else 0.00,
                datetime.datetime.now(),
                datetime.datetime.now(),
            )
        )

if len(query_params) > 0:
    db.set_usagedata(data=query_params)

if len(daily_usage_data_query_params) > 0:
    db.set_dailyusagedata(data=daily_usage_data_query_params)

