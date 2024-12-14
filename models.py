import peewee as pw

db = pw.SqliteDatabase('massage_studio.db')


class BaseModel(pw.Model):
    class Meta:
        database = db

class Master(BaseModel):
    """Майстер"""

    master_id = pw.PrimaryKeyField(null = False)
    name = pw.TextField(null = False)
    user_id = pw.IntegerField(null = False)
    info = pw.TextField(null = False)
    experience = pw.FloatField(null = False)
    phone_number = pw.IntegerField(null = False)
    work_to = pw.DateField(null = True, formats=['%d.%m.%Y'])

    class Meta:
        order_by = 'master_id'
        db_table = 'Masters'


class Service(BaseModel):
    """Послуга"""

    service_id = pw.PrimaryKeyField(null = False)
    title = pw.TextField(null = False)
    cost = pw.IntegerField(null = False)
    duration = pw.IntegerField(null = False)

    class Meta:
        order_by = 'service_id'
        db_table = 'Services'


class Service_has_master(BaseModel):
    """"Зв'язок багато до багатьох між Service та Master"""

    relation_id = pw.PrimaryKeyField(null = False)
    service_id = pw.ForeignKeyField(Service, null = False)
    master_id = pw.ForeignKeyField(Master, null = False)

    class Meta:
        order_by = 'relation_id'
        db_table = 'Services_have_masters'


class Client(BaseModel):
    """Клієнт"""

    client_id = pw.PrimaryKeyField(null = False)
    phone_number = pw.TextField(null = False)
    name = pw.TextField(null = False)

    class Meta:
        order_by = 'client_id'
        db_table = 'Clients'


class Booking(BaseModel):
    """Запис"""

    booking_id = pw.PrimaryKeyField(null = False)
    date = pw.DateField(null = False, formats=['%d.%m.%Y'])
    start_time = pw.TimeField(null = False, formats=['%H:%M'])
    end_time = pw.TimeField(null = False, formats=['%H:%M'])
    duration = pw.IntegerField(null = False)

    client_id = pw.ForeignKeyField(Client, backref = 'bookings', null = False)
    master_id = pw.ForeignKeyField(Master, backref = 'bookings', null = False)
    service_id = pw.ForeignKeyField(Service, backref='bookings', null = False)

    class Meta:
        order_by = 'booking_id'
        db_table = 'Bookings'


class Day_off(BaseModel):
    """Вихідні дні"""

    day_off = pw.DateField(null = False, formats=['%d.%m.%Y'])
    master_id = pw.ForeignKeyField(Master, backref='days_off', null = False)

    class Meta:
        db_table = 'Days_off'

class Break_hours(BaseModel):
    """Перерви/робочі години"""

    hour = pw.TimeField(null = False, formats=['%H:%M'])
    day = pw.DateField(null = False, formats=['%d.%m.%Y'])
    master_id = pw.ForeignKeyField(Master, backref='break_hours', null = False)

    class Meta:
        db_table = 'Break_hours'

def create_tables():
    with db:
        db.create_tables([Booking, Master, Client, Service, Service_has_master, Day_off, Break_hours])

# create_tables()