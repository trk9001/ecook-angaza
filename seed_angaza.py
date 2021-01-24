import datetime, re, math
from dateutil.relativedelta import relativedelta
from mysql.connector import connect
from angaza import Angaza

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
DB_PASSWORD = 'root'
DB_NAME = 'db_integration_angaza_data'

query_params = []
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

select_cursor.execute('SELECT * FROM reports_unitnumber')

unit_numbers = select_cursor.fetchall()

angaza.set_auth(username='atec_iot', password='U*p9fJi31$$X')

for unit_number in unit_numbers:
    separator = str()
    end = False
    i = 1
    next = relativedelta(months=1)
    from_month = datetime.datetime.strptime('2020-01-01', '%Y-%m-%d')
    to_month = from_month + next
    message = 'Fetching data of unit number - ' + str(unit_number['unit_number'])

    print(message)

    while to_month.year <= current_year and to_month.date() <= current_date and not end:
        data = list()

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

print('Total ' + str(len(query_params)) + ' data was inserted')
