from models import *
from utils import *
import datetime as dt



#GETTERS


def get_all_services():
    """Отримати всі послуги, які є"""

    with db:
        serv_price = []

        servs = Service.select()

        for serv in servs:
            serv_price.append([])
            serv_price[-1].append(serv.service_id)
            serv_price[-1].append(serv.title)
            serv_price[-1].append(serv.cost)

    return serv_price

def get_all_masters():
    """Подивитися всіх майстрів"""

    with db:
        mstrs = []

        masters = Master.select()

        for master in masters:
            mstrs.append([])
            mstrs[-1].append(master.master_id)
            mstrs[-1].append(master.name)
            mstrs[-1].append(master.user_id)
            mstrs[-1].append(master.info)
            mstrs[-1].append(master.experience)
            mstrs[-1].append(master.phone_number)
            mstrs[-1].append(master.work_to)

    return mstrs



def get_all_bookings_with_client(client_id):
    """Отримати всі записи клієнта"""

    with db:
        ides = []

        bookings = Booking.select().where(Booking.client_id == client_id)

        for booking in bookings:
            ides.append(booking.booking_id)

    return ides

def get_all_bookings_with_master(master_id):
    """Отримати всі записи майстра"""

    with db:
        ides = []

        bookings = Booking.select().where(Booking.master_id == master_id)

        for booking in bookings:
            ides.append(booking.booking_id)

    return ides

def get_all_bookings():
    """Отримати всі записи, які тільки є в БД"""

    with db:
        ides = []

        bookings = Booking.select()

        for booking in bookings:
            ides.append(booking.booking_id)

    return ides

def get_booking(booking_id):
    """Отримати інформацію про запис"""

    with db:
        info = []

        bookings = Booking.select().where(Booking.booking_id == booking_id)

        for booking in bookings:
            info.append(booking.date)
            info.append(booking.start_time)
            info.append(booking.end_time)
            info.append(booking.duration)
            info.append(booking.service_id)
            info.append(booking.master_id)
            info.append(booking.client_id)

    return info


def get_all_masters_with_service(serv_id):
    """Отримати всіх майстрів з вказаною послугою"""

    with db:
        mstrs = []

        masters = Service_has_master.select().where(Service_has_master.service_id == serv_id)

        for master in masters:
            mstrs.append(master.master_id)

    return mstrs


def get_master(master_id):
    """Отримати всю інфу про майстра з його айді"""

    with db:
        mstrs = []

        masters = Master.select().where(Master.master_id == master_id)

        for master in masters:
            mstrs.append(master.master_id)
            mstrs.append(master.name)
            mstrs.append(master.user_id)
            mstrs.append(master.info)
            mstrs.append(master.experience)
            mstrs.append(master.phone_number)

    return mstrs



def get_all_services_with_master(mast_id):
    """Отримати всі послуги з вказаного майстра"""

    with db:
        servs = []

        services = Service_has_master.select().where(Service_has_master.master_id == mast_id)

        for service in services:
            servs.append(service.service_id)

    return servs


def get_service(service_id):
    """Отримати всю інфу про послугу з послуг"""

    with db:
        servs = []

        services = Service.select().where(Service.service_id == service_id)

        for service in services:
            servs.append(service.service_id)
            servs.append(service.title)
            servs.append(service.cost)

    return servs


def get_client_id(phone_number):
    """Отримати client_id"""

    with db:
        clients = Client.select().where(Client.phone_number == phone_number)

        for client in clients:
            client_id = client.client_id

    return client_id


def get_master_id_with_user_id(user_id):
    """Отримати master_id знаючи user_id"""

    with db:
        try:
            masters = Master.select().where(Master.user_id == user_id)

            for master in masters:
                master_id = master.master_id

        except Exception as e:
            print(e)


    return master_id


def get_client(client_id):
    """Отримати інформацію про клієнта за його id"""

    with db:
        clients = Client.select().where(Client.client_id == client_id)

        client_info = []

        for client in clients:
            client_info.append(client.phone_number)
            client_info.append(client.name)

    return client_info

def get_existance_master(user_id):
    """Визначити чи користувач з вказаним id є майстром"""

    with db:
        masters = Master.select().where(Master.user_id == user_id)

        if len(masters) == 0:
            return False
        else:
            return True

def get_service_id_with_title(title):
    """Отримати service_id використовуючи назву послуги"""

    with db:
        services = Service.select().where(Service.title == title)

        print(services, title)

        for service in services:
            service_id = service.service_id

    return service_id

def get_master_work_to(master_id):
    """Отримати термін роботи майстра"""

    with db:
        masters = Master.select().where(Master.master_id == master_id)

        for master in masters:
            work_to = master.work_to

    return work_to

def get_days_off(master_id):
    """Отримати всі вихідні дні майстра"""

    with db:
        days_off = Day_off.select().where(Day_off.master_id == master_id)

        days = []

        for day in days_off:
            days.append(day.day_off)

    return days

def get_all_days_off():
    """Отримати всі вихідні дні які є в БД"""

    with db:
        days_off = Day_off.select()

        days = []

        for day in days_off:
            days.append(day.day_off)

    return days

def get_duration(service_id):
    """Отримати час, за який певний майстер робить певну послугу"""

    with db:
        services = Service.select().where(Service.service_id == service_id)

        for service in services:
            return service.duration

def get_break_hours_master(master_id):
    """Отримаати перерви майстра"""

    with db:
        dictionary = {}

        hours = Break_hours.select().where(Break_hours.master_id == master_id)

        for hour in hours:
            if hour.day not in dictionary:
                dictionary[hour.day] = []
            dictionary[hour.day].append(hour.hour)

    return dictionary

def get_all_break_hours():
    """Отримати всі перерви які є в БД"""

    with db:
        dictionary = {}

        hours = Break_hours.select()

        for hour in hours:
            if hour.day not in dictionary:
                dictionary[hour.day] = []
            dictionary[hour.day].append([hour.hour])

    return dictionary


#SETTERS

def set_master(name, user_id, info, experience, phone_number):
    """Створення майстра"""

    with db:
        try:
            Master(name = name, user_id = user_id, info = info, experience = experience, work_to=None, phone_number=phone_number).save()
        except Exception as e:
            print(e)

def set_booking(date_time, service_id, master_id, client_id):
    """Створення замовлення"""
    try:

        date = date_time.strftime('%d.%m.%Y')
        start_time = date_time.strftime('%H:%M')
        duration = get_duration(service_id)
        end_time = (date_time + dt.timedelta(minutes=duration)).strftime('%H:%M')

        print(date, start_time, end_time, duration)

        with db:
            Booking(date = date, start_time = start_time, end_time = end_time, duration = duration,
                    service_id = service_id, client_id = client_id, master_id = master_id).save()
    except Exception as e:
        print(e)


def set_client(phone_number, name):
    """Створення слієнта"""

    with db:
        if perevir_unique_clients(phone_number) == False:
            Client(phone_number=phone_number, name=name).save()


def set_service(title, cost, duration):
    """Створення послуги"""

    with db:
        Service(title = title, cost = cost, duration=duration).save()


def set_service_master_relation(master_id, service_id):
    """Створення зв'язку між послугою і майстром"""

    with db:
        Service_has_master(master_id = master_id, service_id = service_id).save()


def set_master_name(user_id, name):
    """Зміна імені використовуючи user_id"""

    with db:
        Master.update(name = name).where(Master.user_id == user_id).execute()


def set_master_info(user_id, info):
    """Зміна імені використовуючи user_id"""

    with db:
        Master.update(info=info).where(Master.user_id == user_id).execute()


def set_master_experience(user_id, experience):
    """Зміна імені використовуючи user_id"""

    with db:
        Master.update(experience=experience).where(Master.user_id == user_id).execute()


def set_master_work_to(user_id, work_to):
    """Зміна терміну роботи майстра використовуючи user_id"""


    with db.atomic():
        query = Master.update(work_to=work_to).where(Master.user_id == user_id)
        query.execute()

def set_day_off(day_off, master_id):
    """Встановлення вихідного дня"""

    day_off = day_off.strftime('%d.%m.%Y')

    with db:
        Day_off(day_off=day_off, master_id=master_id).save()

def set_break_hour(hour, day, master_id):
    """Встановити перерву майстра"""

    hour = hour.replace('-', '.')

    with db:
        Break_hours(hour = hour, day = day, master_id = master_id).save()


#DELETE
def delete_master_from_db(master_id):
    """Видалення майстра з БД"""

    with db:
        master = Master.get(Master.master_id == master_id)
        master.delete_instance(recursive=True)


def delete_outdated_bookings():
    """Видалення застарілих замовлень"""

    with db:
        bookings = Booking.get(dt.datetime.strptime(Booking.date, '%Y-%m-%d').date() < dt.date.today())
        for booking in bookings:
            booking.delete_instance()


def delete_outdated_break_hours():
    """Видалення застарілих перерв"""

    with db:
        break_hours = Break_hours.get(dt.datetime.strptime(Break_hours.day, '%Y-%m-%d').date() < dt.date.today())
        for break_hour in break_hours:
            break_hours.delete_instance()


def delete_outdated_days_off():
    """Видалення застарілих вихідних днів"""

    with db:
        days_off = Day_off.get(dt.datetime.strptime(Day_off.day_off, '%Y-%m-%d').date() < dt.date.today())
        for day_off in days_off:
            day_off.delete_instance()

# def set_service():
#
#     with db:
#         Service(title='Депіляція', cost=100).save()
#
# def set_master():
#
#     with db:
#         Master(name = 'Катя', specialty = 'майстер шугарінгу', experience = 2,
#                instagram = 'https://www.instagram.com/s/aGlnaGxpZ2h0OjE3OTE3Mjc0NTE4MTMyNDU1?story_media_id=1774058401556804354_2885737264&igsh=MWtlbnY0d2R5ZGVwcw==').save()
#
# def set_serv_has_mstr():
#
#     with db:
#         Service_has_Master(service_id = 1, master_id = 3).save()
#
#
# def set_schedule():
#
#     with db:
#         Schedule(master_id=3, date=dt.date(year=2024, month=1, day=3), t08_09=0, t09_10=None, t10_11=None, t11_12=0,
#                  t12_13=0, t13_14=0, t14_15=None, t15_16=0, t16_17=0, t17_18=0, t18_19=None, t19_20=None).save()

# see_services_and_prices()
# add_service()
# add_master()
# add_serv_has_mstr()
# add_schedule()