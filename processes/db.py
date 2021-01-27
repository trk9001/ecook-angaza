import math
from typing import Dict, List, Union
from mysql.connector import connect
from .vars import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_INSERT_STEP


class Database:
    def connect(self):
        return connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

    def get_unitnumbers(self) -> List:
        db = self.connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM reports_unitnumber')
        data = cursor.fetchall()

        db.close()

        return data

    def get_usagedata(self, unit_number=str(), data_type=str(), order_by=str(), descending: bool=False, limit: int=0) -> Union[List, Dict]:
        db = self.connect()
        cursor = db.cursor(dictionary=True)
        query = 'SELECT * FROM reports_usagedata'
        where_clause = str()

        if unit_number != '':
            if where_clause != '':
                where_clause += ' AND unit_number = "' + unit_number + '"'
            else:
                where_clause += ' WHERE unit_number = "' + unit_number + '"'

        if data_type != '':
            if where_clause != '':
                where_clause += ' AND data_type = "' + data_type + '"'
            else:
                where_clause += ' WHERE data_type = "' + data_type + '"'

        if where_clause != '':
            query += where_clause

        if order_by != '':
            query += ' ORDER BY ' + order_by

            if descending:
                query += ' DESC'
            else:
                query += ' ASC'

        if limit > 0:
            query += ' LIMIT ' + str(limit)

        cursor.execute(query)
        data = cursor.fetchall()

        db.close()

        return data

    def set_usagedata(self, data: List) -> None:
        db = self.connect()
        cursor = db.cursor()
        step = DB_INSERT_STEP
        start_position = 0
        end_position = step
        query = """
        INSERT INTO reports_usagedata
        (unit_number, when_datetime, data_type, data_value, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for _ in range(0, math.ceil(len(data) / step)):
            data = data[start_position:end_position]
            
            cursor.executemany(
                query,
                data
            )

            start_position += step
            end_position += step

        db.commit()
        db.close()

    def set_dailyusagedata(self, data: List) -> None:
        db = self.connect()
        cursor = db.cursor()
        step = DB_INSERT_STEP
        start_position = 0
        end_position = step
        query = """
        INSERT INTO reports_dailyusagedata
        (serial_number, average_battery_voltage, max_battery_voltage, min_battery_voltage, battery_critical_state_count,
        one_hour_samples_count, lock_mode_entry_count, factory_mode_entry_count, gsm_sync_button_count,
        stove_on_off_count, daily_power_consumption, left_stove_cooktime, right_stove_cooktime,
        daily_cooking_time, average_power_consumption_per_use, average_cooking_time_per_use,
        when_date, others, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for _ in range(0, math.ceil(len(data) / step)):
            data = data[start_position:end_position]
            
            cursor.executemany(
                query,
                data
            )

            start_position += step
            end_position += step

        db.commit()
        db.close()
