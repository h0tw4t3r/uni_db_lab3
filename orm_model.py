import datetime
import sqlalchemy
from sqlalchemy import and_

import base
from cinema import Cinema
from film import Film
from session import Session


class ORMModelPostgre(object):

    def __init__(self, conn_parameters=None):

        self._tables = {}
        self._foreign_keys = []
        self._session = base.Session()

    # Додати таблиці до моделі
    def add_tables(self, tables):
        for table in tables:
            self._tables[table.__tablename__] = table

    # Властивість, що містить назви таблиць
    @property
    def tables(self):
        return list(self._tables.keys())

    # Додати дані про зовнішній ключ
    def add_foreign_key(self, key_parameters):
        if len(key_parameters) != 4:
            return
        if (key_parameters.get('fk_table') is not None
                and key_parameters.get('fk_column') is not None
                and key_parameters.get('ref_table') is not None
                and key_parameters.get('ref_column')):
            self._foreign_keys.append(key_parameters)

    # Властивість, що містить дані про зовнішні ключі
    @property
    def foreign_keys(self):
        return self._foreign_keys

    # Взяти назви стовпів з таблиці
    def get_columns(self, table_name):
        return self._tables[table_name].__table__.columns.keys()

    # Взяти тип стовпця з таблиці
    def get_column_type(self, table, column_name):
        for c in self._tables[table].__table__.columns:
            if column_name == c.name:
                return c.type.python_type

    # Взяти типи стовпців з таблиці
    def get_column_types(self, table):
        # return self._tables[table].__table__.columns.keys()
        return [c.type.python_type for c in self._tables[table].__table__.columns]

    # Генерувати рядкові дані
    def generate_str(self, quantity, str_len):

        if str_len <= 0:
            return ''
        op = 'chr(trunc(65 + random()*25)::int)'
        parameters = op
        for i in range(1, str_len):
            parameters += ' || ' + op

        query = 'SELECT {0} from generate_series({1},{2})'.format(parameters, 1, quantity)
        print(query)
        cursor = self._conn.cursor()
        cursor.execute(query)
        str_res = [str0[0] for str0 in cursor.fetchall()]
        return str_res

    # Генерувати числові дані
    def generate_numbers(self, quantity, max_value):

        query = 'SELECT trunc(random()*{0})::int from generate_series({1},{2})'.format(max_value, 1, quantity)
        print(query)
        cursor = self._conn.cursor()
        cursor.execute(query)
        numbers = [num[0] for num in cursor.fetchall()]
        return numbers


    # Генерувати дані, що містять дату
    def generate_date(self, quantity, days=90, shift=0, start_date=None):

        if start_date is None:
            start_date = "NOW()"
        query = "select to_char(NOW() + (random() * (NOW() + '{0} days' - NOW())) + '{1} days', 'DD/MM/YYYY') " \
                "from generate_series({2},{3})" \
            .format(days, shift, 1, quantity)
        cursor = self._conn.cursor()
        cursor.execute(query)
        dates = [date0[0] for date0 in cursor.fetchall()]
        return dates

    # Фільми, що будуть показувати після дати та тривалістю у рамках заданого
    def search_query2(self, after_date, min_duration, max_duration):
        date_obj = datetime.datetime.strptime(after_date, '%Y-%m-%d').date()
        query = self._session.query(Film.f_name, Film.f_duration, Cinema.c_name, Session.start_date) \
            .join(Session.film).join(Session.cinemas) \
            .filter(Film.f_duration.between(min_duration, max_duration)) \
            .filter(Session.start_date > date_obj)
        return query.all()

    # Фільми, що будуть показувати після дати у кінотеатрі
    def search_query1(self, after_date, cinema):
        date_obj = datetime.datetime.strptime(after_date, '%Y-%m-%d').date()
        query = self._session.query(Film.f_name, Film.f_genre, Session.start_date, Session.hall_name) \
            .join(Session.film).join(Session.cinemas) \
            .filter(Cinema.c_name == cinema) \
            .filter(Session.start_date > date_obj)
        return query.all()

    # Фільми, назви яких містять словосполучення та відповідного жанру
    def search_query3(self, str_seq, str_genre):

        query = self._session.query(Film.f_name, Film.f_genre, Film.f_duration, Film.release_year)\
            .filter(and_(Film.f_name.ilike('%'+str_seq+'%'),
                         Film.f_genre.ilike('%'+str_genre+'%')))
        return query.all()

    def roll_back(self):
        self._session.rollback()

    # Створити запис
    def create_item(self, table_name, columns, item):

        obj = self._tables[table_name]()
        for i in range(len(columns)):
            obj.__dict__[columns[i]] = item[i]
        self._session.add(obj)
        self._session.commit()

    # Створити декілька записів
    def create_items(self, table_name, columns, items):

        for j in range(len(items)):
            obj = self._tables[table_name]()
            for i in range(len(columns)):
                obj.__dict__[columns[i]] = items[j][i]
            self._session.add(obj)
        self._session.commit()

    # Взяти дані про запис з бази
    def read_item(self, table_name, columns, item_id):
        col_names = []
        tbl_entity = self._tables[table_name]
        for i in range(len(columns)):
            col_names.append(tbl_entity.__dict__[columns[i]])

        query = self._session.query(*col_names).filter(tbl_entity.id == item_id)
        return query.all()

    # Прочитати дані таблиці з бази
    def read_items(self, table_name, columns):
        tbl_entity = self._tables[table_name]
        if columns is not None:
            col_names = []
            for i in range(len(columns)):
                col_names.append(tbl_entity.__dict__[columns[i]])
            query = self._session.query(*col_names)
        else:
            query = self._session.query(tbl_entity)
        return query.all()

    # Оновити запис
    def update_item(self, table_name, columns, item, item_id):

        tbl_entity = self._tables[table_name]

        update_values = dict(zip(columns, item))
        self._session.query(tbl_entity) \
            .filter(tbl_entity.id == item_id) \
            .update(update_values)

        self._session.commit()

    # Видалити запис за ключем
    def delete_item(self, table_name, item_id):
        tbl_entity = self._tables[table_name]
        self._session.query(tbl_entity).filter(tbl_entity.id == item_id).delete()
        self._session.commit()

    # Закрити підключення до бази даних
    def __del__(self):
        self._session.close()


# Тестування модуля
if __name__ == '__main__':
    model = ORMModelPostgre()
    model.add_tables([Film, Cinema, Session])

    model.update_item('Films', ['f_genre'], ['Comedy'], 7)

    print(Film.__table__.c['f_name'].type)
    ttt = Film.__table__.c['f_name'].type.python_type
    if ttt is str:
        print('Yes it is')

    print(convert(Film.__table__.c['f_name'].type))
    print(Film.__table__.c['f_name'].type.__class__)
    ttt2 = Session.__table__.c['film_id'].type.__class__
    print(str(ttt2))
    if ttt2 is sqlalchemy.Integer:
        print('Yes')
    print(ttt2)

    print(model.get_column_types("Sessions"))
    print(model.get_columns("Sessions"))

    print('-----')
    rows = model.search_query1('2020-09-16', 'Kiev')
    print(rows)
    print('-----')
    rows = model.search_query2('2020-09-16', 113, 116)
    print(rows)
    print('-----')
    rows = model.search_query3('e', 'a')
    print(rows)
    '''
    model = ORMModelPostgre()
    tbl_name = "Sessions"
    item0 = model.read_item(tbl_name, None, 10)
    print(item0)
    column = "testID"

    column_type = model.get_column_type(tbl_name, column)
    print(column_type)

    column_types = model.get_column_types(tbl_name)
    print(column_types)

    model.generate_numbers(5, 10)
    model.generate_str(5, 5)
    model.generate_date(90, 30)

    rows = model.search_query1('20-09-16', 'Kiev')
    print(rows)

    rows = model.search_query2('20-09-16', 60, 116)
    print(rows)

    rows = model.search_query3('er', 'Fan')
    print(rows)
    '''
