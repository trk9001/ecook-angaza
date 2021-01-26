import datetime, re, math
from dateutil.relativedelta import relativedelta
from mysql.connector import connect
from angaza import Angaza

def convert_to_datetime(item, format='%Y-%m-%dT%H:%M:%Sz'):
    return datetime.datetime.strptime(item, format)


def get_usage_data(unit_number: int, from_when_dt: str, to_when_dt: str=str(), offset: int = 0, variable = []):
    data = angaza.get_usage_data(
        unit_number=unit_number,
        from_when_dt=from_when_dt,
        offset=offset
    )

    if to_when_dt != '':
        data = angaza.get_usage_data(
            unit_number=unit_number,
            from_when_dt=from_when_dt,
            to_when_dt=to_when_dt,
            offset=offset
        )

    if '_embedded' in data and len(data['_embedded']['item']) > 0:
        variable += data['_embedded']['item']

        if '_links' in data and 'next' in data['_links']:
            link = data['_links']['next']['href']
            offset = re.search('&offset=(.*)', link)

            if offset and offset > 0:
                if to_when_dt != '':
                    get_usage_data(unit_number=unit_number, from_when_dt=from_when_dt, to_when_dt=to_when_dt, offset=offset, variable=variable)
                else:
                    get_usage_data(unit_number=unit_number, from_when_dt=from_when_dt, offset=offset, variable=variable)

    return variable

DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'Atec$2020'
DB_NAME = 'db_angaza'

TYPES = {
    219: 'serial_number',
    220: 'average_battery_voltage',
    221: 'max_battery_voltage',
    222: 'min_battery_voltage',
    223: 'battery_critical_state_count',
    224: '1_hour_samples_count',
    225: 'lock_mode_entry_count',
    226: 'factory_mode_entry_count',
    227: 'gsm_sync_button_count',
    228: 'stove_on_off_count',
    229: 'daily_power_consumption',
    230: 'left_stove_cooktime',
    231: 'right_stove_cooktime',
    232: 'others'
}
query_params = []
daily_usage_data_query_params = []
current_date = datetime.date.today()
current_month = current_date.month
current_year = current_date.year
current_day = current_date.day
angaza = Angaza()
db = connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
select_cursor = db.cursor(dictionary=True)
query = 'INSERT INTO reports_usagedata (unit_number, when_datetime, data_type, data_value, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)'
daily_usage_data_query = 'INSERT INTO reports_dailyusagedata (serial_number, average_battery_voltage, max_battery_voltage, min_battery_voltage, battery_critical_state_count, one_hour_samples_count, lock_mode_entry_count, factory_mode_entry_count, gsm_sync_button_count, stove_on_off_count, daily_power_consumption, left_stove_cooktime, right_stove_cooktime, daily_cooking_time, average_power_consumption_per_use, average_cooking_time_per_use, when_date, others, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

select_cursor.execute('SELECT * FROM reports_unitnumber')

unit_numbers = select_cursor.fetchall()

angaza.set_auth(username='atec_iot', password='U*p9fJi31$$X')

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

    while to_month.year <= current_year and to_month.date() <= current_date and not end:
        data = list()
        daily_usage_data_unorganized = list()
        daily_usage_data_without_stove_calculation = []
        daily_usage_data_counter = 0
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

        get_usage_data(
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
            
            for item in data:
                when_date = convert_to_datetime(item['when']).date()

                if not (item['type'], when_date) in done_type:
                    done_type.append((item['type'], when_date))

                    temp_data = {
                        'when_date': str(when_date)
                    }
                    temp_data[TYPES[item['type']]] = 0

                    for jitem in data:
                        if item['type'] == jitem['type'] and when_date == convert_to_datetime(jitem['when']).date():
                            if item['type'] == 228:
                                temp_data[TYPES[item['type']]] = jitem['value']
                            elif when_date == convert_to_datetime(jitem['when']).date():
                                temp_data[TYPES[item['type']]] += jitem['value']

                    daily_usage_data_unorganized.append(temp_data)


            done_type = []
            daily_usage_data = []
            stove_on_off_count = 0

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

if len(query_params) > 0:
    cursor = db.cursor()
    step = 25000
    start_position = 0
    end_position = step
    
    for _ in range(0, math.ceil(len(query_params) / step)):
        temp_query_params = query_params[start_position:end_position]
        
        cursor.executemany(
            query,
            temp_query_params
        )

        start_position += step
        end_position += step
    db.commit()

if len(daily_usage_data_query_params) > 0:
    cursor = db.cursor()
    step = 25000
    start_position = 0
    end_position = step
    
    for _ in range(0, math.ceil(len(daily_usage_data_query_params) / step)):
        temp_query_params = daily_usage_data_query_params[start_position:end_position]
        
        cursor.executemany(
            daily_usage_data_query,
            temp_query_params
        )

        start_position += step
        end_position += step
    db.commit()

print('Total ' + str(len(query_params)) + ' data was inserted')
