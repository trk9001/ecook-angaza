from mysql.connector import connect
from angaza import Angaza

DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'db_integration_angaza_data'

angaza = Angaza()
db = connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

angaza.set_auth(username='atec_iot', password='U*p9fJi31$$X')
data = angaza.get_usage_data(
    unit_number=74878232,
    from_when_dt='2020-08-20T00:00:00+00:00',
    to_when_dt='2020-08-21T00:00:00+00:00'
)
query_params = []

for item in data['samples']:
    query_params.append(
        ('74878232', item['when'], item['type'], item['value'])
    )


cursor = db.cursor()
query = 'INSERT INTO reports_usagedata (unit_number, when, type, value) VALUES (%s, %s, %s, %s)'

cursor.executemany(
    query,
    query_params
)
