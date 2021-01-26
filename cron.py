import datetime, re
from mysql.connector import connect
from angaza import Angaza

query_params = []

def get_usage_data(unit_number: int, from_when_dt: str, offset: int = 0):
    data = angaza.get_usage_data(
        unit_number=unit_number,
        from_when_dt=from_when_dt,
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
                get_usage_data(unit_number=unit_number, from_when_dt=from_when_dt, offset=offset)

DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'Atec$2020'
DB_NAME = 'db_angaza'

today = datetime.date.today()
delta = datetime.timedelta(days=1)
from_date = today - delta
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
    print('Fetching data of unit number - ' + str(unit_number['unit_number']) + ' for ' + datetime.datetime.strftime(from_date, '%Y-%m-%d'))

    select_cursor.execute('SELECT * FROM reports_usagedata WHERE unit_number = "'+ str(unit_number['unit_number']) +'" AND data_type = "228" ORDER BY when_datetime DESC LIMIT 1')

    get_usage_data(
        unit_number=unit_number['unit_number'],
        from_when_dt='{}T01:00:00+00:00'.format(from_date)
    )

cursor = db.cursor()
cursor.executemany(
    query,
    query_params
)
db.commit()

print('Total ' + str(len(query_params)) + ' data was inserted')
