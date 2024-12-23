import telebot
import datetime
import schedule as plot
import config
import database as dbpy
from utils import *
from telebot import types


bot = telebot.TeleBot(config.TOKEN)

redis_client.flushdb()


@bot.message_handler(commands=['start'])
def start(message):
    dbpy.delete_outdated_bookings()
    dbpy.delete_outdated_break_hours()
    dbpy.delete_outdated_days_off()

    if dbpy.get_existance_master(message.chat.id):
        set_user_state(message.chat.id, 'main_master')

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        change_info = types.KeyboardButton(text='Змінити інформацію про себе')
        change_services = types.KeyboardButton(text='Послуги, які я надаю')
        schedule = types.KeyboardButton(text='Мій розклад')
        term = types.KeyboardButton(text='Сформувати свій графік')
        new_service = types.KeyboardButton(text='Надаю нову послугу')
        keyboard.add(change_info, change_services, schedule, term, new_service)

        bot.send_message(message.chat.id, 'Доброго вам дня', reply_markup=keyboard)
    else:
        set_user_state(message.chat.id, 'main_menu')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        working_hours_button = types.KeyboardButton('Коли ви працюєте?')
        available_serv = types.KeyboardButton(text='Доступні послуги')
        my_book = types.KeyboardButton(text='Мої записи')
        keyboard.add(working_hours_button, available_serv, my_book)
        bot.send_message(message.chat.id,
                         f'Вітаю, {message.from_user.first_name}! Я бот масажної студії. Виберіть те, що вас цікавить.')
        bot.send_message(message.chat.id, 'Я з радістю допоможу вам записатись до нас', reply_markup=keyboard)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id)=='main_menu')
def main_menu(message):
    '''Гловне меню'''
    if message.text == 'Головне меню':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        working_hours_button = types.KeyboardButton('Коли ви працюєте?')
        available_serv = types.KeyboardButton(text='Доступні послуги')
        my_book = types.KeyboardButton(text='Мої записи')

        keyboard.add(working_hours_button, available_serv, my_book)
        bot.send_message(message.chat.id, 'Звісно, що вас цікавить?', reply_markup=keyboard)

    elif message.text == 'Коли ви працюєте?':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back_button = types.KeyboardButton(text='Головне меню')
        keyboard.add(back_button)
        bot.send_message(message.chat.id, 'Ми працюємо\nПн-Пт  з 8:00 до 20:00\nСб-Нд  вихідний', reply_markup=keyboard)


    elif message.text == 'Доступні послуги':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back_button = types.KeyboardButton(text='Головне меню')
        keyboard.add(back_button)
        bot.send_message(message.chat.id, 'Секунду, дізнаюсь інформацію...', reply_markup=keyboard)

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        services = []
        serv_price = dbpy.get_all_services()
        msg = 'Ось послуги, які ми пропонуємо:\n'
        for sp in serv_price:
            services.append(types.InlineKeyboardButton(
                text=sp[1],
                callback_data='serv_' + str(sp[0])))
            msg = msg + sp[1] + '  ---  ' + str(sp[2]) + '\n'
        [keyboard.add(b) for b in services]

        bot.send_message(message.chat.id, msg, reply_markup=keyboard)

    elif message.text == 'Мої записи':
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        reg_button = types.KeyboardButton(text="Поділитись своїм номером телефону", request_contact=True)
        keyboard.add(reg_button)
        bot.send_message(message.chat.id,
                         "Для цього поділіться, будь-ласка, своїм номер телефону",
                         reply_markup=keyboard)

        set_user_data(message.chat.id, 'booking', 'false')
    else:
        if message.text[0] == '/':
            clear_user_state(message.chat.id)
            bot.send_message(message.chat.id, 'Повторіть, будь ласка, команду')
        else:
            bot.send_message(message.chat.id, 'Ви ввели неправильно!')


@bot.message_handler(commands=['delete'])
def delete_master(message):
    """Видалення майстра з БД, який звільнився"""

    try:
        master_id = dbpy.get_master_id_with_user_id(message.chat.id)
        master = dbpy.get_master(master_id)

        if master[5] == config.main_phone_number:
            masters = dbpy.get_all_masters()

            keyboard = types.InlineKeyboardMarkup()
            buttons = [types.InlineKeyboardButton(text=master[1], callback_data=f'delete_{master[0]}')
                       for master in masters]
            for btn in buttons:
                keyboard.add(btn)

            bot.send_message(message.chat.id, 'Виберіть майстра, який є звільнений', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Вибачте, але у вас немає права на цю дію')
    except:
        bot.send_message(message.chat.id, 'Вибачте, але вам  не доступна ця функція')



@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    dbpy.set_client(message.contact.phone_number, message.contact.first_name)
    client_id = dbpy.get_client_id(message.contact.phone_number)

    if get_user_state(message.chat.id) == 'share_contact':
        """Завершення реєстрації: збереження всієї інформації в БД"""

        try:
            name = get_user_data(message.chat.id, 'name')
            info = get_user_data(message.chat.id, 'info')
            experience = get_user_data(message.chat.id, 'experience')
            services = get_user_data(message.chat.id, 'reg_services')

            dbpy.set_master(name=name, user_id=message.chat.id,
                            info=info, experience=experience,
                            phone_number=message.contact.phone_number)

            master_id = dbpy.get_master_id_with_user_id(message.chat.id)

            for service in services:
                service_id = dbpy.get_service_id_with_title(service)
                dbpy.set_service_master_relation(master_id, service_id)

            set_user_state(message.chat.id, 'set_work_to')

            bot.send_message(message.chat.id,
                             'Напишіть, будь ласка, до якого дня включно ви плануєте працювати(день.місяць.рік)')
        except:
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            share_contact_button = types.KeyboardButton(text="Поділитись своїм номером телефону", request_contact=True)
            keyboard.add(share_contact_button)

            bot.send_message(message.chat.id,
                             "Для закінчення вашої реєстрації поділіться, будь-ласка, своїм номером телефону",
                             reply_markup=keyboard)
    else:
        data_booking = get_user_data(message.chat.id, 'booking')
        service_id = get_user_data(message.chat.id, 'service_id')
        master_id = get_user_data(message.chat.id, 'master_id')

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        working_hours_button = types.KeyboardButton('Коли ви працюєте?')
        available_serv = types.KeyboardButton(text='Доступні послуги')
        my_book = types.KeyboardButton(text='Мої записи')
        keyboard.add(working_hours_button, available_serv, my_book)

        if data_booking == 'true':
            dt = get_user_data(message.chat.id, 'date_time')
            date_time = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M')
            dbpy.set_booking(date_time, service_id, master_id, client_id)

            bot.send_message(message.chat.id, 'Вітаю, ви записались!', reply_markup=keyboard)

            set_user_state(message.chat.id, 'main_menu')
        else:
            try:
                client_id = dbpy.get_client_id(message.contact.phone_number)
                bookings = dbpy.get_all_bookings_with_client(client_id)

                info=[]
                for booking in bookings:
                    info.append(dbpy.get_booking(booking))


                msgs = []
                for i in info:
                    master_info = dbpy.get_master(i[5])
                    service_info = dbpy.get_service(i[4])

                    date = i[0]
                    time = i[1]

                    msgs.append(f'Дата: {date}\nЧас на котру потрібно підійти: {time}\nІм\'я вашого майстра: '
                                f'{master_info[1]}\nПослуга, за якою ви звертаєтесь до нас: {service_info[1]}\nЦіна: {service_info[2]}грн')

                msg = 'Ось інформація про ваші записи:\n' + '\n\n'.join(msgs)
                bot.send_message(message.chat.id, msg, reply_markup=keyboard)
            except:
                bot.send_message(message.chat.id, 'У вас немає запису', reply_markup=keyboard)

        set_user_state(message.chat.id, 'main_menu')


# FOR MASTERS

@bot.message_handler(commands=['registration', 'reg'])
def become_master(message):
    """Реєстрація майстра"""

    bot.send_message(message.chat.id,
                     'Привіт. Я бот масажної студії. Щоб зареєструватись тобі потрібно дати відповіді на кілька запитань.')
    bot.send_message(message.chat.id, 'Для початку реєстрації, введіть, будь ласка, пароль')


    bot.register_next_step_handler(message, verify_password)


def verify_password(message):
    """Перевірка правильності паролю, доступ до реєстрації"""

    if message.text == config.password:
        set_user_state(message.chat.id, 'name')
        bot.send_message(message.chat.id, 'Як тебе звати? (Яке ім\'я буде відображатись користувачам)')
    else:
        bot.send_message(message.chat.id, 'Вибачте, але пароль не правильний')
        bot.register_next_step_handler(message, verify_password)

@bot.message_handler(func=lambda message: get_user_state(message.chat.id)=='name')
def becoming_master_name(message):
    """Бот зберігає собі ім'я майстра і задає йому запитання про досвід"""

    set_user_state(message.chat.id, 'reg_services')
    bot.send_message(message.chat.id, 'Який у вас досвід? (лише цифрою в роках)')

    set_user_data(message.chat.id, 'name', message.text)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id)=='reg_services')
def choosing_services(message):
    """Бот зберігає досвід майстра і задає йому запитання щодо його досвіду
    Бот виводить повідомлення з варіантами послуг і можливістю створити нову послугу"""

    keyboard = types.InlineKeyboardMarkup()
    services = dbpy.get_all_services()
    btn = []

    if get_user_data(message.chat.id, 'reg_services') == None:
        number = 0
        set_user_data(message.chat.id, 'experience', message.text)
    else:
        number = len(get_user_data(message.chat.id, 'reg_services'))

    if number == 0:
        set_user_data(message.chat.id, 'reg_services', [])
        info = []
    else:
        info = get_user_data(message.chat.id, 'reg_services')


    for service in services:
        if service[1] not in info:
            btn.append(types.InlineKeyboardButton(text=service[1], callback_data='reg_serv_' + service[1]))

    [keyboard.add(b) for b in btn]

    keyboard.add(types.InlineKeyboardButton(text='Додати нову послугу', callback_data='add_new_service'))

    if number >= 1:
        keyboard.add(types.InlineKeyboardButton(text='Більше я не надаю послуг', callback_data='end_registration'))

    bot.send_message(message.chat.id, 'Виберіть які послуги ви надаєте', reply_markup=keyboard)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id)=='info')
def becoming_master_end(message):
    """Збереження опису і перенаправлення для поширення свого номеру телефона"""

    set_user_state(message.chat.id, 'share_contact')
    set_user_data(message.chat.id, 'info', message.text)

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    share_contact_button = types.KeyboardButton(text="Поділитись своїм номером телефону", request_contact=True)
    keyboard.add(share_contact_button)

    bot.send_message(message.chat.id,
                     "Для закінчення вашої реєстрації поділіться, будь-ласка, своїм номером телефону",
                     reply_markup=keyboard)

def add_new_service_main_master(message):
    """Функція для додавання нових послуг уже існуюючого майстра"""

    keyboard = types.InlineKeyboardMarkup()
    services = dbpy.get_all_services()
    btn = []
    if get_user_data(message.chat.id, 'reg_services') == None:
        services_master = dbpy.get_services_of_master(message.chat.id)
        info = [dbpy.get_service(service)[1] for service in services_master]
        set_user_data(message.chat.id, 'reg_services', info)
    else:
        info = get_user_data(message.chat.id, 'reg_services')

    for service in services:
        if service[1] not in info:
            btn.append(types.InlineKeyboardButton(text=service[1], callback_data='reg_serv_' + service[1]))

    [keyboard.add(b) for b in btn]

    keyboard.add(types.InlineKeyboardButton(text='Додати нову послугу', callback_data='add_new_service'))
    keyboard.add(types.InlineKeyboardButton(text='Більше не хочу додавати', callback_data='end_adding_services'))
    bot.send_message(message.chat.id, 'Виберіть послуги які ви хочете надавати', reply_markup=keyboard)

@bot.message_handler(func=lambda message: get_user_state(message.chat.id)=='main_master')
def main_master_menu(message):
    if message.text == 'Змінити інформацію про себе':
        keyboard = types.InlineKeyboardMarkup()
        change_name = types.InlineKeyboardButton(text='Ім\'я', callback_data='change_name')
        change_info = types.InlineKeyboardButton(text='Опис', callback_data='change_info')
        change_experience = types.InlineKeyboardButton(text='Досвід', callback_data='change_experience')
        keyboard.add(change_name, change_experience, change_info)

        bot.send_message(message.chat.id, 'Що саме Ви хочете змінити?', reply_markup=keyboard)
    elif message.text == 'Послуги, які я надаю':
        master_id = dbpy.get_master_id_with_user_id(message.chat.id)
        service_ids = dbpy.get_all_services_with_master(master_id)
        msg = ''

        for service_id in service_ids:
            service = dbpy.get_service(service_id)
            msg = msg + service[1] + ' -- ' + str(service[2]) + '\n'

        msg = 'Ось послуги, які ви надаєте:\n' + msg

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    elif message.text == 'Мій розклад':
        master_id = dbpy.get_master_id_with_user_id(message.chat.id)
        booking_ids = dbpy.get_all_bookings_with_master(master_id)
        bookings = [dbpy.get_booking(booking_id) for booking_id in booking_ids]
        bookings_by_name = []


        for booking in bookings:
            bookings_by_name.append({})
            service = dbpy.get_service(booking[-3])
            client = dbpy.get_client(booking[-1])

            bookings_by_name[-1]['date'] = booking[0]
            bookings_by_name[-1]['start_time'] = booking[1]
            bookings_by_name[-1]['end_time'] = booking[2]
            bookings_by_name[-1]['duration'] = booking[3]
            bookings_by_name[-1]['service_title'] = service[1]
            bookings_by_name[-1]['cost'] = service[2]
            bookings_by_name[-1]['phone_number'] = client[0]
            bookings_by_name[-1]['client_name'] = client[1]

        img_streams = plot.create_schedule_images(bookings_by_name)

        for img_stream in img_streams:
            bot.send_photo(message.chat.id, img_stream)


        keyboard = types.InlineKeyboardMarkup()
        btn = []
        for booking in bookings_by_name:
            breaking = True
            for button in btn:
                if button.text == booking['date']:
                    breaking = False
            if breaking:
                btn.append(types.InlineKeyboardButton(text=booking['date'],
                                                      callback_data='master_booking_date_' + booking['date']))

        for button in btn:
            keyboard.add(button)

        set_user_state(message.chat.id, 'get_client_date')
        set_user_data(message.chat.id, 'get_client_date', bookings_by_name)

        if len(btn) > 0:
            bot.send_message(message.chat.id, 'Щоб отримати інформацію про клієнта, будь ласка, виберіть його замовлення',
                             reply_markup=keyboard)
        else:
            set_user_state(message.chat.id, 'main_master')
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            back = types.KeyboardButton(text='Повернутись на головний екран')
            keyboard.add(back)
            bot.send_message(message.chat.id, 'Ваш розклад пустий', reply_markup=keyboard)
    elif message.text == 'Сформувати свій графік':
        set_user_state(message.chat.id, 'set_work_to')

        bot.send_message(message.chat.id, 'Напишіть, будь ласка, до якого дня включно ви плануєте працювати(день.місяць.рік)')
    elif message.text == 'Повернутись на головний екран':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        change_info = types.KeyboardButton(text='Змінити інформацію про себе')
        change_services = types.KeyboardButton(text='Послуги, які я надаю')
        schedule = types.KeyboardButton(text='Мій розклад')
        term = types.KeyboardButton(text='Сформувати свій графік')
        new_service = types.KeyboardButton(text='Надаю нову послугу')
        keyboard.add(change_info, change_services, schedule, term, new_service)

        bot.send_message(message.chat.id, 'Вас повернуто на головний екран', reply_markup=keyboard)
    elif message.text == 'Надаю нову послугу':
        add_new_service_main_master(message)
    else:
        if message.text[0] == '/':
            clear_user_state(message.chat.id)
            bot.send_message(message.chat.id, 'Повторіть, будь ласка, команду')
        else:
            bot.send_message(message.chat.id, 'Ви ввели неправильно!')


@bot.message_handler(func=lambda message: get_user_state(message.chat.id)=='set_work_to')
def set_schedule_start(message):
    """Отримання даних про терміну роботи, запит про вихідні дні"""

    try:
        txt = message.text.split('.')
        date = datetime.date(int(txt[2]), int(txt[1]), int(txt[0]))
        date = date.strftime('%d.%m.%Y')

        set_user_state(message.chat.id, 'set_days_off')
        dbpy.set_master_work_to(message.chat.id, date)

        keyboard = types.InlineKeyboardMarkup(row_width=7)
        days = sort_days(date)
        set_user_data(message.chat.id, 'days', days)
        month = next(iter(days))
        set_user_data(message.chat.id, 'month', month)
        set_user_data(message.chat.id, 'days_off', [])
        weeks = days[month]
        if len(days) != 1:
            btn_next = types.InlineKeyboardButton(text='>>', callback_data='setting_days_off_next')
            keyboard.add(btn_next)

        for num_week, week in weeks.items():
            week_btns = []
            for day in week:
                week_btns.append(types.InlineKeyboardButton(text=day.split('-')[2],
                                                            callback_data='setting_days_off_'+day))

            if len(week_btns) != 7:
                if datetime.datetime.strptime(week[0], '%Y-%m-%d').date().isocalendar()[2] == 1:
                    btns_to_add = 7-len(week_btns)
                    for x in range(btns_to_add):
                        week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                elif datetime.datetime.strptime(week[-1], '%Y-%m-%d').date().isocalendar()[2] == 7:
                    btns_to_add = 7 - len(week_btns)
                    for x in range(btns_to_add):
                        week_btns.insert(0, types.InlineKeyboardButton(text='-', callback_data='nothing'))
                else:
                    first_day = datetime.datetime.strptime(week[0], '%Y-%m-%d').date().isocalendar()[2]
                    last_day = datetime.datetime.strptime(week[-1], '%Y-%m-%d').date().isocalendar()[2]

                    day = 1
                    while day != first_day:
                        week_btns.insert(0, types.InlineKeyboardButton(text='-', callback_data='nothing'))
                        day += 1

                    day = 7
                    while day != last_day:
                        week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                        day -= 1


            keyboard.add(week_btns[0], week_btns[1], week_btns[2], week_btns[3],
                         week_btns[4], week_btns[5], week_btns[6])

        complete = types.InlineKeyboardButton(text='Завершити вибір вихідних днів', callback_data='setting_days_off_complete')
        keyboard.add(complete)

        msg = bot.send_message(message.chat.id, f'Виберіть вихідні дні\n\nМісяць: {month}',
                         reply_markup=keyboard)

        set_user_data(message.chat.id, 'sent_message', msg.message_id)
    except:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(message.chat.id, 'Ви ввели не правильно, будь ласка, спробуйте ще раз',
                         reply_markup=keyboard)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id)=='set_days_off')
def set_schedule(message):
    """Отримання даних про вихідні дні"""

    try:
        txt = message.text.split(',')
        list = [element.split('.') for element in txt]

        master_id = dbpy.get_master_id_with_user_id(message.chat.id)

        for day_off in list:
            date = datetime.date(day=int(day_off[0]), month=int(day_off[1]), year=int(day_off[2]))
            dbpy.set_day_off(date, master_id)

        set_user_state(message.chat.id, 'main_master')

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(message.chat.id, 'Ваш графік сформовано!', reply_markup=keyboard)

    except:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(message.chat.id, 'Ви ввели не правильно, будь ласка, спробуйте ще раз', reply_markup=keyboard)


# CALLBACK_QUERY_HANDLERS
@bot.callback_query_handler(func=lambda call: call.data.startswith('end_adding_services'))
def end_adding_services(call):
    """Закінчення додавання нових послуг"""

    set_user_state(call.message.chat.id, 'main_master')

    services = get_user_data(call.message.chat.id, 'reg_services')
    old_services_id = dbpy.get_services_of_master(call.message.chat.id)
    old_services = [dbpy.get_service(service_id) for service_id in old_services_id]
    new_services = [service for service in services if service not in old_services]

    master_id = dbpy.get_master_id_with_user_id(call.message.chat.id)

    for service in new_services:
        service_id = dbpy.get_service_id_with_title(service)
        dbpy.set_service_master_relation(master_id, service_id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back = types.KeyboardButton(text='Повернутись на головний екран')
    keyboard.add(back)

    bot.send_message(call.message.chat.id, 'Ви змінили список послуг, які надаєте', reply_markup=keyboard)

def month_calendar(keyboard, weeks, days_off, type):
    """Створює Inline кнопки - книжечка-календар"""

    for num_week, week in weeks.items():
        week_btns = []
        for day in week:
            if day in days_off:
                week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
            else:
                if type == 'days_off':
                    week_btns.append(types.InlineKeyboardButton(text=day.split('-')[2],
                                                            callback_data='setting_days_off_' + day))
                elif type == 'break_hours':
                    week_btns.append(types.InlineKeyboardButton(text=day.split('-')[2],
                                                                callback_data='setting_hours_day_' + day))

        if len(week_btns) != 7:
            if datetime.datetime.strptime(week[0], '%Y-%m-%d').date().isocalendar()[2] == 1:
                btns_to_add = 7 - len(week_btns)
                for x in range(btns_to_add):
                    week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
            elif datetime.datetime.strptime(week[-1], '%Y-%m-%d').date().isocalendar()[2] == 7:
                btns_to_add = 7 - len(week_btns)
                for x in range(btns_to_add):
                    week_btns.insert(0, types.InlineKeyboardButton(text='-', callback_data='nothing'))
            else:
                first_day = datetime.datetime.strptime(week[0], '%Y-%m-%d').date().isocalendar()[2]
                last_day = datetime.datetime.strptime(week[-1], '%Y-%m-%d').date().isocalendar()[2]

                day = 1
                while day != first_day:
                    week_btns.insert(0, types.InlineKeyboardButton(text='-', callback_data='nothing'))
                    day += 1

                day = 7
                while day != last_day:
                    week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                    day -= 1

        keyboard.add(week_btns[0], week_btns[1], week_btns[2], week_btns[3],
                     week_btns[4], week_btns[5], week_btns[6])

    if type == 'days_off':
        complete = types.InlineKeyboardButton(text='Завершити вибір вихідних днів',
                                            callback_data='setting_days_off_complete')
    elif type == 'break_hours':
        complete = types.InlineKeyboardButton(text='Завершити вибір перерв',
                                              callback_data='setting_hours_complete_all')
    keyboard.add(complete)

    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('setting_hours_'))
def set_break_hours(call):
    """Функція яка обробляє встановлення перерв"""

    command = call.data[14:]
    all_hours = [x/2 for x in range(16, 41)]
    WORK_HOURS = []
    for hour in all_hours:
        if hour % 1 == 0:
            WORK_HOURS.append(str(int(hour)) + ':00')
        elif hour % 1 == 0.5:
            WORK_HOURS.append(str(int(hour - 0.5)) + ':30')

    days = get_user_data(call.message.chat.id, 'days')
    month = get_user_data(call.message.chat.id, 'month')
    days_off = get_user_data(call.message.chat.id, 'days_off')
    hour_breaks = get_user_data(call.message.chat.id, 'hour_breaks')
    msg_id = get_user_data(call.message.chat.id, 'sent_message')

    match command:
        case 'next':
            months = iter(days)
            while next(months) != month:
                pass
            new_month = next(months)
            set_user_data(call.message.chat.id, 'month', new_month)
            weeks = days[new_month]

            keyboard = types.InlineKeyboardMarkup(row_width=7)

            try:
                next(months)
                btn_next = types.InlineKeyboardButton(text='>>', callback_data='setting_hours_next')
                keyboard.add(btn_next)
            except:
                pass
            btn_back = types.InlineKeyboardButton(text='<<', callback_data='setting_hours_back')
            keyboard.add(btn_back)

            keyboard = month_calendar(keyboard, weeks, days_off, 'break_hours')

            msg = bot.edit_message_text(f'Виберіть дні для вибору перерви\n\nМісяць: {new_month}',
                                        chat_id=call.message.chat.id, message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)
        case 'back':
            reversed_days = {key: value for key, value in reversed(days.items())}
            months = iter(reversed_days)
            while next(months) != month:
                pass
            new_month = next(months)
            set_user_data(call.message.chat.id, 'month', new_month)
            weeks = days[new_month]

            keyboard = types.InlineKeyboardMarkup(row_width=7)

            try:
                next(months)
                btn_back = types.InlineKeyboardButton(text='<<', callback_data='setting_hours_back')
                keyboard.add(btn_back)
            except:
                pass
            btn_next = types.InlineKeyboardButton(text='>>', callback_data='setting_hours_next')
            keyboard.add(btn_next)

            keyboard = month_calendar(keyboard, weeks, days_off, 'break_hours')

            msg = bot.edit_message_text(f'Виберіть дні для вибору перерви\n\nМісяць: {new_month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)
        case 'complete_all':
            set_user_state(call.message.chat.id, 'main_master')
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            back = types.KeyboardButton(text='Повернутись на головний екран')
            keyboard.add(back)

            bot.delete_message(call.message.chat.id, msg_id)
            bot.send_message(call.message.chat.id, 'Ваш графік сформовано!', reply_markup=keyboard)
        case 'complete_day':
            weeks = days[month]

            keyboard = types.InlineKeyboardMarkup(row_width=7)

            months = iter(days)
            while next(months) != month:
                pass

            try:
                next(months)
                btn_next = types.InlineKeyboardButton(text='>>', callback_data='setting_hours_next')
                keyboard.add(btn_next)
            except:
                pass

            reversed_days = {key: value for key, value in reversed(days.items())}
            reversed_months = iter(reversed_days)
            while next(reversed_months) != month:
                pass

            try:
                next(reversed_months)
                btn_back = types.InlineKeyboardButton(text='<<', callback_data='setting_hours_back')
                keyboard.add(btn_back)
            except:
                pass

            keyboard = month_calendar(keyboard, weeks, days_off, 'break_hours')

            msg = bot.edit_message_text(f'Виберіть дні для вибору перерви\n\nМісяць: {month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)
        case str() if command.startswith('day_'):
            master_id = dbpy.get_master_id_with_user_id(call.message.chat.id)
            hours = dbpy.get_break_hours_master(master_id)

            if command[4:] in hours:
                hours_of_day = [hour for hour in WORK_HOURS if hour.zfill(5)+':00' not in hours[command[4:]]]
            else:
                hours_of_day = WORK_HOURS

            keyboard = types.InlineKeyboardMarkup(row_width=2)
            btns = []
            for hour in hours_of_day:
                btns.append(types.InlineKeyboardButton(text=hour, callback_data=f'setting_hours_hour_{command[4:]}_{hour}'))


            for btn in btns:
                keyboard.add(btn)

            back_to_days = types.InlineKeyboardButton(text='Повернутись до перегляду днів',
                                                      callback_data='setting_hours_complete_day')
            keyboard.add(back_to_days)

            msg = bot.edit_message_text(f'Виберіть години, в які хочете відпочивати\n\nДата: {month}, {command[12:]}',
                                        chat_id=call.message.chat.id, message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)
        case str() if command.startswith('hour_'):
            master_id = dbpy.get_master_id_with_user_id(call.message.chat.id)
            day, hour = command[5:].split('_')
            dbpy.set_break_hour(hour, day, master_id)

            hours = dbpy.get_break_hours_master(master_id)

            if day in hours:
                hours_of_day = [hour for hour in WORK_HOURS if hour.zfill(5)+':00' not in hours[day]]
            else:
                hours_of_day = WORK_HOURS


            keyboard = types.InlineKeyboardMarkup(row_width=2)
            btns = []
            for hour in hours_of_day:
                btns.append(types.InlineKeyboardButton(text=hour, callback_data=f'setting_hours_hour_{day}_{hour}'))


            for btn in btns:
                keyboard.add(btn)

            back_to_days = types.InlineKeyboardButton(text='Повернутись до перегляду днів',
                                                      callback_data='setting_hours_complete_day')
            keyboard.add(back_to_days)

            msg = bot.edit_message_text(f'Виберіть години, в які хочете відпочивати\n\nДата: {month}, {day[8:]}',
                                        chat_id=call.message.chat.id, message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('setting_days_off_'))
def set_days_off(call):
    """Функція яка керує механізмом книжечки для вибору вихідних днів"""

    command = call.data[17:]

    days = get_user_data(call.message.chat.id, 'days')
    month = get_user_data(call.message.chat.id, 'month')
    days_off = get_user_data(call.message.chat.id, 'days_off')
    msg_id = get_user_data(call.message.chat.id, 'sent_message')

    match command:
        case 'next':
            months = iter(days)
            while next(months) != month:
                pass
            new_month = next(months)
            set_user_data(call.message.chat.id, 'month', new_month)
            weeks = days[new_month]

            keyboard = types.InlineKeyboardMarkup(row_width=7)

            try:
                next(months)
                btn_next = types.InlineKeyboardButton(text='>>', callback_data='setting_days_off_next')
                keyboard.add(btn_next)
            except:
                pass
            btn_back = types.InlineKeyboardButton(text='<<', callback_data='setting_days_off_back')
            keyboard.add(btn_back)

            keyboard = month_calendar(keyboard, weeks, days_off, 'days_off')

            msg = bot.edit_message_text(f'Виберіть вихідні дні\n\nМісяць: {new_month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)
        case 'back':
            reversed_days = {key: value for key, value in reversed(days.items())}
            months = iter(reversed_days)
            while next(months) != month:
                pass
            new_month = next(months)
            set_user_data(call.message.chat.id, 'month', new_month)
            weeks = days[new_month]

            keyboard = types.InlineKeyboardMarkup(row_width=7)

            try:
                next(months)
                btn_back = types.InlineKeyboardButton(text='<<', callback_data='setting_days_off_back')
                keyboard.add(btn_back)
            except:
                pass
            btn_next = types.InlineKeyboardButton(text='>>', callback_data='setting_days_off_next')
            keyboard.add(btn_next)

            keyboard = month_calendar(keyboard, weeks, days_off, 'days_off')

            msg = bot.edit_message_text(f'Виберіть вихідні дні\n\nМісяць: {new_month}', chat_id=call.message.chat.id,
                                       message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)
        case 'complete':
            list = [element.split('-') for element in days_off]

            master_id = dbpy.get_master_id_with_user_id(call.message.chat.id)

            for day_off in list:
                date = datetime.date(day=int(day_off[2]), month=int(day_off[1]), year=int(day_off[0]))
                dbpy.set_day_off(date, master_id)

            weeks = days[month]

            keyboard = types.InlineKeyboardMarkup(row_width=7)

            months = iter(days)
            while next(months) != month:
                pass

            try:
                next(months)
                btn_next = types.InlineKeyboardButton(text='>>', callback_data='setting_hours_next')
                keyboard.add(btn_next)
            except:
                pass

            reversed_days = {key: value for key, value in reversed(days.items())}
            reversed_months = iter(reversed_days)
            while next(reversed_months) != month:
                pass

            try:
                next(reversed_months)
                btn_back = types.InlineKeyboardButton(text='<<', callback_data='setting_hours_back')
                keyboard.add(btn_back)
            except:
                pass

            for num_week, week in weeks.items():
                week_btns = []
                for day in week:
                    if day in days_off:
                        week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                    else:
                        week_btns.append(types.InlineKeyboardButton(text=day.split('-')[2],
                                                                    callback_data='setting_hours_day_' + day))

                if len(week_btns) != 7:
                    if datetime.datetime.strptime(week[0], '%Y-%m-%d').date().isocalendar()[2] == 1:
                        btns_to_add = 7 - len(week_btns)
                        for x in range(btns_to_add):
                            week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                    elif datetime.datetime.strptime(week[-1], '%Y-%m-%d').date().isocalendar()[2] == 7:
                        btns_to_add = 7 - len(week_btns)
                        for x in range(btns_to_add):
                            week_btns.insert(0, types.InlineKeyboardButton(text='-', callback_data='nothing'))
                    else:
                        first_day = datetime.datetime.strptime(week[0], '%Y-%m-%d').date().isocalendar()[2]
                        last_day = datetime.datetime.strptime(week[-1], '%Y-%m-%d').date().isocalendar()[2]

                        day = 1
                        while day != first_day:
                            week_btns.insert(0, types.InlineKeyboardButton(text='-', callback_data='nothing'))
                            day += 1

                        day = 7
                        while day != last_day:
                            week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                            day -= 1

                keyboard.add(week_btns[0], week_btns[1], week_btns[2], week_btns[3],
                             week_btns[4], week_btns[5], week_btns[6])

            complete = types.InlineKeyboardButton(text='Завершити вибір перерв',
                                                  callback_data='setting_hours_complete_all')
            keyboard.add(complete)

            set_user_data(call.message.chat.id, 'hour_breaks', [])

            msg = bot.edit_message_text(f'Виберіть день для якого хочете відредагувати робочі години\n\n'
                                        f'Місяць: {month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)

        case _:
            if days_off == None:
                days_off = [command]
            else:
                days_off.append(command)
            set_user_data(call.message.chat.id, 'days_off', days_off)
            weeks = days[month]

            keyboard = types.InlineKeyboardMarkup(row_width=7)

            months = iter(days)
            while next(months) != month:
                pass

            try:
                next(months)
                btn_next = types.InlineKeyboardButton(text='>>', callback_data='setting_days_off_next')
                keyboard.add(btn_next)
            except:
                pass

            reversed_days = {key: value for key, value in reversed(days.items())}
            reversed_months = iter(reversed_days)
            while next(reversed_months) != month:
                pass

            try:
                next(reversed_months)
                btn_back = types.InlineKeyboardButton(text='<<', callback_data='setting_days_off_back')
                keyboard.add(btn_back)
            except:
                pass

            keyboard = month_calendar(keyboard, weeks, days_off, 'days_off')

            msg = bot.edit_message_text(f'Виберіть вихідні дні\n\nМісяць: {month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            set_user_data(call.message.chat.id, 'sent_message', msg.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_master_from_db(call):
    """Видалення певного майстра з БД"""

    try:
        dbpy.delete_master_from_db(call.data[7:])
        set_user_state(call.message.chat.id, 'main_master')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)
        bot.send_message(call.message.chat.id, 'Видалено!', reply_markup=keyboard)
    except:
        bot.send_message(call.message.chat.id, 'Щось пішло не так')

@bot.callback_query_handler(func=lambda call: call.data.startswith('master_booking_'))
def master_booking(call):
    """Реалізація книжечки для отримання інформації про клієнта"""


    if 'date' in call.data:
        bookings = []
        for booking in get_user_data(call.message.chat.id, 'get_client_date'):
            if booking['date'] == call.data[20:]:
                bookings.append(booking)

        keyboard = types.InlineKeyboardMarkup()
        btn = []
        for booking in bookings:
            breaking = True
            for button in btn:
                if button.text == booking['start_time']:
                    breaking = False
            if breaking:
                btn.append(
                    types.InlineKeyboardButton(text=booking['start_time'],
                                               callback_data='master_booking_time_' + booking['start_time']))

        for button in btn:
            keyboard.add(button)

        set_user_state(call.message.chat.id, 'get_client_time')
        set_user_data(call.message.chat.id, 'get_client_time', bookings)

        bot.send_message(call.message.chat.id, 'Щоб отримати інформацію про клієнта, будь ласка, виберіть його замовлення',
                         reply_markup=keyboard)

    elif 'time' in call.data:
        bookings = []
        for booking in get_user_data(call.message.chat.id, 'get_client_time'):
            if booking['start_time'] == call.data[20:]:
                bookings.append(booking)

        set_user_state(call.message.chat.id, 'main_master')

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(call.message.chat.id, f"Ім\'я замовника: {bookings[0]['client_name']},\nномер телефону замовника:{bookings[0]['phone_number']}",
                         reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('change_'))
def changing_master(call):
    """Зміна інформації про майстра"""

    if call.data[7:] == 'name':
        bot.send_message(call.message.chat.id, 'Ваше нове ім\'я:')
        bot.register_next_step_handler(call.message, changing_master_name)
    elif call.data[7:] == 'info':
        bot.send_message(call.message.chat.id, 'Ваш новий опис:')
        bot.register_next_step_handler(call.message, changing_master_info)
    elif call.data[7:] == 'experience':
        bot.send_message(call.message.chat.id, 'Ваш новий досвід:')
        bot.register_next_step_handler(call.message, changing_master_experience)


def changing_master_name(message):
    """Зміна імені майстра"""

    dbpy.set_master_name(message.text, message.chat.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back = types.KeyboardButton(text='Повернутись на головний екран')
    keyboard.add(back)

    bot.send_message(message.chat.id, 'ваше ім\'я змінено!', reply_markup=keyboard)


def changing_master_info(message):
    """Зміна опису майстра"""

    dbpy.set_master_info(message.text, message.chat.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back = types.KeyboardButton(text='Повернутись на головний екран')
    keyboard.add(back)

    bot.send_message(message.chat.id, 'ваш опис змінено!', reply_markup=keyboard)


def changing_master_experience(message):
    """Зміна досвіду майстра"""

    dbpy.set_master_experience(message.text, message.chat.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back = types.KeyboardButton(text='Повернутись на головний екран')
    keyboard.add(back)

    bot.send_message(message.chat.id, 'ваш досвід змінено!', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('end_registration'))
def ending_registration(call):
    """Закінчення реєстрації: внесення даних до БД"""

    set_user_state(call.message.chat.id, 'info')

    bot.send_message(call.message.chat.id, 'Опишіть себе, свої вміння')


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_new_service'))
def start_add_new_service(call):
    """Бот задає запитання на рахунок назви послуги"""

    if get_user_state(call.message.chat.id) == 'reg_services':
        set_user_data(call.message.chat.id, 'add_new_service', 'registration')
    elif get_user_state(call.message.chat.id) == 'main_master':
        set_user_data(call.message.chat.id, 'add_new_service', 'main_master')

    set_user_state(call.message.chat.id, 'add_new_service')

    bot.send_message(call.message.chat.id,
                     'Щоб створити нову послугу ви повинні дотриматись формату:\n'
                     'назва, ціна, час(у хвилинах)     коми обов\'язкові')


@bot.message_handler(func=lambda message: get_user_state(message.chat.id)=='add_new_service')
def end_add_new_service(message):
    """Бот звертається до БД і додає нову послугу"""

    info = get_user_data(message.chat.id, 'reg_services')

    try:
        txt = message.text.split(', ')
        info.append(txt[0])
        if dbpy.get_existance_service(txt[0]):
            bot.send_message(message.chat.id, 'Вибачте, але послуга з такою ж нозвою уже існує, спробуйте змінити назву')
        else:
            set_user_data(message.chat.id, 'reg_services', info)
            dbpy.set_service(title=txt[0], cost=txt[1], duration=txt[2])
            bot.send_message(message.chat.id, 'Додано')
    except:
        bot.send_message(message.chat.id, 'Будь ласка, перевірте чи ви дотримались правильної форми. Якщо все було дотримано правильно,'
                                          'то зверніться до тех. підтримки')
    finally:
        if get_user_data(message.chat.id, 'add_new_service') == 'registration':
            set_user_state(message.chat.id, 'reg_services')
            set_user_data(message.chat.id, 'add_new_service', 0)
            choosing_services(message)
        elif get_user_data(message.chat.id, 'add_new_service') == 'main_master':
            set_user_state(message.chat.id, 'main_master')
            set_user_data(message.chat.id, 'add_new_service', 0)
            add_new_service_main_master(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('reg_serv_'))
def registration_services_callback(call):
    serv_info = get_user_data(call.message.chat.id, 'reg_services')
    if serv_info == None:
        serv_info = []
    serv_info.append(call.data[9:])
    set_user_data(call.message.chat.id, 'reg_services', serv_info)

    bot.send_message(call.message.chat.id, 'Додано!')
    if get_user_state(call.message.chat.id) == 'reg_services':
        choosing_services(call.message)
    elif get_user_state(call.message.chat.id) == 'main_master':
        add_new_service_main_master(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('serv_'))
def services_callback(call):
    serv_id = int(call.data[5:])
    set_user_data(call.message.chat.id, 'service_id', serv_id)
    masters_id = dbpy.get_all_masters_with_service(serv_id)
    masters = []
    for master_id in masters_id:
        masters.append(dbpy.get_master(master_id))

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    msg = 'Ось майстри, які цим займаються:\n'
    btn = []

    for mt in masters:
        btn.append(types.InlineKeyboardButton(
            text=mt[1], callback_data='book_' + '_' + str(mt[0])))
        msg += mt[1] + '\n' + mt[3] + f'\nз досвідом {mt[4]} р.\n\n'
    [keyboard.add(b) for b in btn]

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg,
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('book_'))
def book_callback(call):
    master_id = call.data.split('_')[2]
    set_user_data(call.message.chat.id, 'master_id', master_id)
    may_to_book = plot.get_schedule_of_master(master_id)
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    days = []
    btn = []
    for day in may_to_book:
        if isinstance(day, str):
            btn.append(types.InlineKeyboardButton(text=day, callback_data='bookday_' + day))
            days.append(day)
    for x in range(len(btn)):
        keyboard.add(btn[x])

    msg = 'Ось дні на які ви можете записатись до цього майстра:\n'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg,
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('bookday_'))
def bookday_callback(call):
    data = call.data.split('_')
    day = data[1]
    set_user_data(call.message.chat.id, 'day', day)

    service_id = get_user_data(call.message.chat.id, 'service_id')
    master_id = get_user_data(call.message.chat.id, 'master_id')
    duration = dbpy.get_duration(service_id)
    hours = plot.get_day_of_master(master_id, day, duration)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    btn = []
    for hour in hours:
        btn.append(types.InlineKeyboardButton(text=hour, callback_data='bookhour_' + hour))
    for x in range(len(btn)):
        keyboard.add(btn[x])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Ось вільні години в цей день', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('bookhour_'))
def bookhour_callback(call):
    day = get_user_data(call.message.chat.id, 'day')
    dt = day + ' ' + call.data.split('_')[1]

    set_user_data(call.message.chat.id, 'date_time', dt)

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    share_contact_button = types.KeyboardButton(text="Поділитись своїм номером телефону", request_contact=True)
    keyboard.add(share_contact_button)

    bot.send_message(call.message.chat.id,
                     "Для бронювання поділіться, будь ласка, своїм номером телефону",
                     reply_markup=keyboard)

    set_user_data(call.message.chat.id, 'booking', 'true')
    set_user_state(call.message.chat.id, 'booking')

bot.infinity_polling()