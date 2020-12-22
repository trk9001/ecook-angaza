import datetime, re
from dateutil.relativedelta import relativedelta
from mysql.connector import connect
from angaza import Angaza

query_params = []

def get_usage_data(unit_number: int, from_when_dt: str, to_when_dt: str, offset: int = 0):
    data = angaza.get_usage_data(
        unit_number=unit_number,
        from_when_dt=from_when_dt,
        to_when_dt=to_when_dt,
        offset=offset
    )

    if '_embedded' in data and len(data['_embedded']['item']) > 0:
        for item in data['_embedded']['item']:
            query_params.append(
                (
                    unit_number,
                    datetime.datetime.strptime(item['when'], '%Y-%m-%dT%H:%M:%Sz'),
                    item['type'],
                    item['value'],
                    datetime.datetime.now(),
                    datetime.datetime.now(),
                )
            )

        if '_links' in data and 'next' in data['_links']:
            link = data['_links']['next']['href']
            offset = re.search('&offset=(.*)', link)

            if offset and offset > 0:
                get_usage_data(unit_number=unit_number, from_when_dt=from_when_dt, to_when_dt=to_when_dt, offset=offset)

DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'db_integration_angaza_data'

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
    from_month = datetime.datetime.strptime('2020-01-01', '%Y-%m-%d')
    message = 'Fetching data of unit number - ' + str(unit_number['unit_number'])

    print(message)

    for _ in range(1, 12):
        next = relativedelta(months=1)
        to_month = from_month + next

        if to_month.year == current_year and to_month.month <= current_month:
            print('Running from ' + datetime.datetime.strftime(from_month, '%Y-%m-%d') + ' to ' + datetime.datetime.strftime(to_month, '%Y-%m-%d'))

            get_usage_data(
                unit_number=unit_number['unit_number'],
                from_when_dt='{}T01:00:00+00:00'.format(datetime.datetime.strftime(from_month, '%Y-%m-%d')),
                to_when_dt='{}T01:00:00+00:00'.format(datetime.datetime.strftime(to_month, '%Y-%m-%d')),
            )

            from_month = to_month
        else:
            break

    if from_month.month  < current_day:
        print('Running from ' + datetime.datetime.strftime(from_month, '%Y-%m-%d') + ' to ' + str(current_date))
        
        get_usage_data(
            unit_number=unit_number['unit_number'],
            from_when_dt='{}T01:00:00+00:00'.format(datetime.datetime.strftime(from_month, '%Y-%m-%d')),
            to_when_dt='{}T01:00:00+00:00'.format(str(current_date)),
        )

    for _ in range(len(message)):
        separator += '-'

    print(separator)

cursor = db.cursor()
cursor.executemany(
    query,
    query_params
)
db.commit()
