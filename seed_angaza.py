import datetime, time
from dateutil.relativedelta import relativedelta
from processes.db import Database
from processes.helper import Helper
from processes.vars import ANGAZA_DATA_TYPES


query_params = []
daily_usage_data_query_params = []
db = Database()
helper = Helper()
current_date = datetime.date.today()
current_month = current_date.month
current_year = current_date.year
current_day = current_date.day
unit_numbers = db.get_unitnumbers()

# Iterate all the unit numbers to get data against a unit number.
for unit_number in unit_numbers:
    separator = str()
    end = False
    last_usage_data = None
    i = 1
    next = relativedelta(months=1)
    from_month = datetime.datetime.strptime('2020-12-01', '%Y-%m-%d')
    to_month = from_month + next
    message = 'Fetching data of unit number - ' + str(unit_number['unit_number'])

    print(message)

    # Fetch data from Angaza by 1 month till yesterday.
    while to_month.year <= current_year and to_month.date() <= current_date and not end:
        data = list()
        daily_usage_data_unorganized = list()
        daily_usage_data_without_stove_calculation = []
        done_type = []
        done_prev_usage_data = False

        if i > 1:
            to_month = (from_month + next) - relativedelta(days=1)
        else:
            to_month = from_month + next

        if to_month.date() > current_date:
            end = True
            to_month = datetime.datetime.today() - relativedelta(days=1)
            
        print('Running from ' + datetime.datetime.strftime(from_month, '%Y-%m-%d') + ' to ' + datetime.datetime.strftime(to_month, '%Y-%m-%d'))
        
        # Calling API to Angaza.
        helper. get_usage_data(
            unit_number=unit_number['unit_number'],
            from_when_dt='{}T01:00:00+00:00'.format(datetime.datetime.strftime(from_month, '%Y-%m-%d')),
            to_when_dt='{}T01:00:00+00:00'.format(datetime.datetime.strftime(to_month, '%Y-%m-%d')),
            variable=data
        )

        print(str(len(data)) + ' data found')

        if len(data) > 0:
            data = sorted(
                data,
                key=lambda item: item['when']
            )

            # Convert unreadable data from angaza to readable data.
            for item in data:
                when_date = helper.convert_to_datetime(item['when']).date()

                if not (item['type'], when_date) in done_type:
                    done_type.append((item['type'], when_date))

                    temp_data = {
                        'when_date': str(when_date)
                    }
                    temp_data[ANGAZA_DATA_TYPES[item['type']]] = 0

                    for jitem in data:
                        if item['type'] == jitem['type'] and when_date == helper.convert_to_datetime(jitem['when']).date():
                            if item['type'] == 228:
                                temp_data[ANGAZA_DATA_TYPES[item['type']]] = jitem['value']
                            elif when_date == helper.convert_to_datetime(jitem['when']).date():
                                temp_data[ANGAZA_DATA_TYPES[item['type']]] += jitem['value']

                    daily_usage_data_unorganized.append(temp_data)


            done_type = []
            daily_usage_data = []
            stove_on_off_count = 0

            # Get all data for the same date.
            for item in daily_usage_data_unorganized:
                if not item['when_date'] in done_type:
                    done_type.append(item['when_date'])
                    temp_data = {}

                    for jitem in daily_usage_data_unorganized:
                        if item['when_date'] == jitem['when_date']:
                            jitem_keys = jitem.keys()

                            for jk in jitem_keys:
                                temp_data[jk] = jitem[jk]

                    daily_usage_data_without_stove_calculation.append(temp_data)

            # Stove on/off calculation.
            for item in daily_usage_data_without_stove_calculation:
                if 'stove_on_off_count' in item:
                    temp = item['stove_on_off_count']

                    if not done_prev_usage_data and last_usage_data is not None:
                        done_prev_usage_data = True
                        item['stove_on_off_count'] = item['stove_on_off_count'] - last_usage_data['value']
                    else:
                        item['stove_on_off_count'] = item['stove_on_off_count'] - stove_on_off_count

                    stove_on_off_count = temp

                daily_usage_data.append(item)

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

            for item in daily_usage_data:
                item['daily_power_consumption'] = item['daily_power_consumption'] / 1000 if item['daily_power_consumption'] > 0 else item['daily_power_consumption']
                item['average_power_consumption_per_use'] = 0
                item['average_cooking_time_per_use'] = 0

                item['daily_cooking_time'] = item['left_stove_cooktime'] + item['right_stove_cooktime']

                if 'stove_on_off_count' in item and item['stove_on_off_count'] > 0:
                    item['average_power_consumption_per_use'] = item['daily_power_consumption'] / item['stove_on_off_count']
                    item['average_cooking_time_per_use'] = item['daily_cooking_time'] / item['stove_on_off_count']

                daily_usage_data_query_params.append(
                    (
                        unit_number['unit_number'],
                        item['average_battery_voltage'] if 'average_battery_voltage' in item else 0.00,
                        item['max_battery_voltage'] if 'max_battery_voltage' in item else 0.00,
                        item['min_battery_voltage'] if 'min_battery_voltage' in item else 0.00,
                        item['battery_critical_state_count'] if 'battery_critical_state_count' in item else 0.00,
                        item['one_hour_samples_count'] if 'one_hour_samples_count' in item else 0.00,
                        item['lock_mode_entry_count'] if 'lock_mode_entry_count' in item else 0.00,
                        item['factory_mode_entry_count'] if 'factory_mode_entry_count' in item else 0.00,
                        item['gsm_sync_button_count'] if 'gsm_sync_button_count' in item else 0.00,
                        item['stove_on_off_count'] if 'stove_on_off_count' in item else 0.00,
                        item['daily_power_consumption'] if 'daily_power_consumption' in item else 0.00,
                        item['left_stove_cooktime'] if 'left_stove_cooktime' in item else 0.00,
                        item['right_stove_cooktime'] if 'right_stove_cooktime' in item else 0.00,
                        item['daily_cooking_time'] if 'daily_cooking_time' in item else 0.00,
                        item['average_power_consumption_per_use'] if 'average_power_consumption_per_use' in item else 0.00,
                        item['average_cooking_time_per_use'] if 'average_cooking_time_per_use' in item else 0.00,
                        item['when_date'] if 'when_date' in item else 0.00,
                        item['others'] if 'others' in item else 0.00,
                        datetime.datetime.now(),
                        datetime.datetime.now(),
                    )
                )

            last_usage_data_filter = list(filter(lambda item: item['type'] == 228, data))
            last_usage_data = sorted(last_usage_data_filter, key=lambda item: item['when'], reverse=True)
            last_usage_data = last_usage_data[0] if len(last_usage_data) > 0 else None

        from_month = to_month + relativedelta(days=1)
        i+=1

    for _ in range(len(message)):
        separator += '-'

    print(separator)

    time.sleep(1)

if len(query_params) > 0:
    db.set_usagedata(data=query_params)

if len(daily_usage_data_query_params) > 0:
    db.set_dailyusagedata(data=daily_usage_data_query_params)

print('Total ' + str(len(query_params)) + ' data was inserted')
