from telebot.handler_backends import State, StatesGroup
from models import *
import datetime as dt
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

print(redis_client.set(name='test', value=1))
print(redis_client.get(name='test'))

STATES = ("main_menu", "my_bookings", "choose_day", "choose_hour", "booking", "main_master", "name", "experience",
    "info", "reg_services", "add_new_service", "set_work_to", "days", "month", "hour_breaks", "sent_message",
    "set_days_off", "share_contact", "get_client_date", "get_client_time")


#FSM(Finite State Machine) using Redis
def set_user_state(user_id, state):
    """Встановлення стану користувача"""

    if state in STATES:
        redis_client.set(f'user:{user_id}:state', state)

def get_user_state(user_id):
    """Подивитись стан користувача"""

    return redis_client.get(f'user:{user_id}:state')

def set_user_data(user_id, key, value):
    """Встановити якусь тимчасову інформацію користувача"""

    if key in STATES:
        redis_client.hset(f'user:{user_id}:data', key, value)

def get_user_data(user_id, key):
    """Отримати збережену інформацію користувача"""

    return redis_client.hget(f'user:{user_id}:data', key)

def clear_user_data(user_id):
    """Почистити збережену інформацію користувача з redis"""

    redis_client.delete(f'user:{user_id}:data')


def clear_user_state(user_id):
    """Почистити стан користувача з redis"""

    redis_client.delete(f'user:{user_id}:state')



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