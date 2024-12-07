from telebot.handler_backends import State, StatesGroup
from models import *
import datetime as dt
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

print(redis_client.set(name='test', value=1))
print(redis_client.get(name='test'))

class UserStates(StatesGroup):
    '''Class for defining states'''

    #General states
    main_menu = State()
    # services = State()
    # masters = State()
    my_bookings = State()
    choose_day = State()
    choose_hour = State()
    booking = State()
    main_master = State()

    #States for registration a master
    name = State()
    experience = State()
    info = State()
    reg_services = State()
    add_new_service = State()
    set_work_to = State()
    days = State()
    month = State()
    hour_breaks = State()
    sent_message = State()
    set_days_off = State()
    share_contact = State()

    #States for getting info about client
    get_client_date = State()
    get_client_time = State()


def perevir_unique_clients(phone_number):

    with db:

        try:
            clients = Client.select().where(Client.phone_number == phone_number)
            for client in clients:
                if client.phone_number == phone_number:
                    return True
            return False
        except:
            return False

def days_to(day_to):
    """Генерація списку днів до конкретного дня"""

    end_date = dt.datetime.strptime(day_to, "%d.%m.%Y").date()
    today = dt.datetime.today().date()
    date_list = [(today + dt.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, (end_date - today).days + 1)]

    return date_list

def sort_days(day_to):
    """Сортування днів по місяцях і тижнях"""

    days = days_to(day_to)

    MONTHS = ['Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
              'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень']

    sorted_days = {}


    for day in days:
        month_of_day = MONTHS[int(day.split('-')[1])-1]
        week_of_day = dt.datetime.strptime(day, '%Y-%m-%d').date().isocalendar()[1]
        if month_of_day in sorted_days:
            if week_of_day in sorted_days[month_of_day]:
                sorted_days[month_of_day][week_of_day].append(day)
            else:
                sorted_days[month_of_day][week_of_day] = [day]
        else:
            sorted_days[month_of_day] = {}
            sorted_days[month_of_day][week_of_day] = [day]


    return sorted_days

redis_client.close()