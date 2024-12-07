import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from io import BytesIO
import numpy
import datetime as dt
import database as db

matplotlib.use('Agg')


def create_schedule_images(bookings):
    """Розприділяє замовлення по тижнях"""

    future_bookings = []

    for booking in bookings:
        if dt.datetime.strptime(booking['date'], '%Y-%m-%d').date() >= dt.date.today():
            future_bookings.append(booking)

    days_bookings = []
    already_exist = False

    for booking in future_bookings:
        for x in range(len(days_bookings)):
            booking_day = dt.datetime.strptime(booking['date'], '%Y-%m-%d').date()
            day = dt.datetime.strptime(days_bookings[x][0], '%Y-%m-%d').date()
            if booking_day == day:
                days_bookings[x][1].append(booking)
                already_exist = True
        if not already_exist:
            days_bookings.append([booking['date'], [booking]])
        else:
            already_exist = False

    weeks_bookings = []
    already_exist = False

    for day in days_bookings:
        for x in range(len(weeks_bookings)):
            booking_week = dt.datetime.strptime(day[0], '%Y-%m-%d').date().isocalendar()[1]
            if booking_week == weeks_bookings[x][0]:
                weeks_bookings[x][1].append(day)
                already_exist = True
        if not already_exist:
            weeks_bookings.append([dt.datetime.strptime(day[0], '%Y-%m-%d').date().isocalendar()[1], [day]])
        else:
            already_exist = False

    try:
        img_streams = []
        for week in weeks_bookings:
            img_streams.append(create_week_schedule_image(week[1]))
        return img_streams
    except Exception as e:
        print(f'Error in the second stage of create_schedule_images: {e}')


def create_week_schedule_image(bookings):
    """Створення фото розкладу на тиждень"""

    fig, ax = plt.subplots()

    start_time = 8
    end_time = 20
    fig.set_size_inches(10, 6)
    ax.set_xlim(start_time, end_time)
    ax.set_ylim(0, 7)
    days = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця', 'Субота']

    for y_pos in range(0, 6):
        ax.text(start_time - 0.5, 6 - y_pos, days[y_pos], ha='right', va='center', fontsize=12)


    for day_bookings in bookings:
        week_day = dt.datetime.strptime(day_bookings[0], '%Y-%m-%d').date().isocalendar()[2]
        # print(week_day)
        # while y_pos != 7-week_day:
        #     print(y_pos)
        #     ax.text(start_time - 0.5, y_pos, days[6-y_pos], ha='right', va='center', fontsize=12)
        #     y_pos -= 1
        # print(days[week_day-1])
        # ax.text(start_time - 0.5, 6-week_day, days[week_day-1], ha='right', va='center', fontsize=12)
        # y_pos -= 1

        for booking in day_bookings[1]:
            # print(booking)
            title = booking['service_title']
            start = booking['start_time']
            end = booking['end_time']
            duration = booking['duration']
            start_hour = int(start.split(":")[0]) + int(start.split(":")[1]) / 60
            end_hour = int(end.split(":")[0]) + int(end.split(":")[1]) / 60
            ax.add_patch(Rectangle((start_hour, 6.5 - week_day), duration/60, 0.8, edgecolor='black', facecolor='lightblue'))
            ax.text(start_hour + duration / 2, 6 - week_day, title, ha='center', va='center', fontsize=10)


    # Налаштування осей
    ax.set_xlabel('Час (години)')
    ax.set_ylabel('Дні тижня')
    ax.set_xticks(range(start_time, end_time + 1))
    ax.set_yticks([])

    # Зберігаємо зображення в пам'яті
    img_stream = BytesIO()
    plt.savefig(img_stream, format='png')
    plt.close()
    img_stream.seek(0)

    return img_stream


def generate_date_list(end_date_str):
    end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    today = dt.datetime.today().date()
    date_list = [(today + dt.timedelta(days=i)).isoformat() for i in range(1, (end_date - today).days + 1)]
    return date_list

def get_schedule_of_master(master_id):
    """Отримати дні, в які можна записатись до майстра"""

    work_to = db.get_master_work_to(master_id)
    days = generate_date_list(work_to)

    days_off = db.get_days_off(master_id)

    days = [day for day in days if day not in days_off]

    return days

def get_day_of_master(master_id, day, duration):
    """Отримати вільні години майстра в конкретний день"""

    all_hours = [x/2 for x in range(16, 41)]
    work_hours = db.get_break_hours_master(master_id)
    work_hours_float = [int(hour[:2]) + int(hour[3:5])/60 for hour in list(work_hours.values())[0]]

    all_hours = [hour for hour in all_hours if hour in work_hours_float]

    all_bookings = db.get_all_bookings_with_master(master_id)
    all_bookings_info = []
    for booking in all_bookings:
        all_bookings_info.append(db.get_booking(booking))

    for booking in all_bookings_info:
        if booking[0] != day:
            all_bookings_info.remove(booking)

    hours_to_remove = [20]

    for booking in all_bookings_info:
        for hour in all_hours:
            if float_time(booking[1]) <= hour < float_time(booking[2]):
                hours_to_remove.append(hour)

    duration = duration/60

    del_hour = 0.5
    second_remove = []
    while del_hour < duration:
        for hour in hours_to_remove:
            second_remove.append(hour-del_hour)
        del_hour += 0.5

    all_hours = [hour for hour in all_hours if hour not in hours_to_remove]
    all_hours = [hour for hour in all_hours if hour not in second_remove]


    hours_list = []
    for hour in all_hours:
        if hour % 1 == 0:
            hours_list.append(str(int(hour))+':00')
        elif hour % 1 == 0.5:
            hours_list.append(str(int(hour-0.5))+':30')

    return hours_list

def float_time(time):
    """Перевести час у float щоб можна було порівняти простіше
    для функції get_day_of_master()"""

    fl_time, minutes, seconds = time.split(':')
    fl_time = float(fl_time) + float(minutes)/60

    return fl_time