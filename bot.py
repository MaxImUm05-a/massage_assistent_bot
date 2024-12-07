import telebot
import datetime

import schedule as plot
import config
import database as db
from utils import UserStates
from utils import sort_days

from telebot import types
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from telebot.callback_data import CallbackData
from telebot.states.sync.context import StateContext



state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.TOKEN, state_storage=state_storage, use_class_middlewares=True)
# bot = telebot.TeleBot(TOKEN)

services_factory = CallbackData('service_id', prefix='services')
masters_factory = CallbackData('master_id', prefix='masters')


@bot.message_handler(commands=['start'])
def start(message):
    db.delete_outdated_bookings()
    db.delete_outdated_break_hours()
    db.delete_outdated_days_off()

    if db.get_existance_master(message.from_user.id) == True:
        bot.set_state(message.from_user.id, UserStates.main_master, message.chat.id)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        change_info = types.KeyboardButton(text='Змінити інформацію про себе')
        change_services = types.KeyboardButton(text='Послуги, які я надаю')
        schedule = types.KeyboardButton(text='Мій розклад')
        term = types.KeyboardButton(text='Сформувати свій графік')
        keyboard.add(change_info, change_services, schedule, term)

        bot.send_message(message.chat.id, 'Доброго вам дня', reply_markup=keyboard)
    else:
        bot.set_state(message.from_user.id, UserStates.main_menu, message.chat.id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        working_hours_button = types.KeyboardButton('Коли ви працюєте?')
        available_serv = types.KeyboardButton(text='Доступні послуги')
        # available_master = types.KeyboardButton(text='Перегляд майстрів')
        my_book = types.KeyboardButton(text='Мої записи')
        keyboard.add(working_hours_button, available_serv, my_book)
        bot.send_message(message.chat.id,
                         f'Вітаю, {message.from_user.first_name}! Я бот салону краси від Ані. Виберіть те, що вас цікавить.')
        bot.send_message(message.chat.id, 'Я з радістю допоможу вам записатись до нас <3', reply_markup=keyboard)


@bot.message_handler(state=UserStates.main_menu)
def main_menu(message):
    '''Гловне меню'''
    if message.text == 'Головне меню':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        working_hours_button = types.KeyboardButton('Коли ви працюєте?')
        available_serv = types.KeyboardButton(text='Доступні послуги')
        # available_master = types.KeyboardButton(text='Перегляд майстрів')
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
        serv_price = db.get_all_services()
        msg = 'Ось послуги, які ми пропонуємо:\n'
        for sp in serv_price:
            services.append(types.InlineKeyboardButton(
                text=sp[1],
                callback_data='serv_' + str(sp[0])))
            msg = msg + sp[1] + '  ---  ' + str(sp[2]) + '\n'
        [keyboard.add(b) for b in services]

        bot.send_message(message.chat.id, msg, reply_markup=keyboard)
        bot.add_data(message.from_user.id, message.chat.id, first='serv')
        print('user_id: ' + str(message.from_user.id) + ' chat_id: ' + str(message.chat.id))
        # bot.set_state(message.from_user.id, UserStates.masters, message.chat.id)

    # elif message.text == 'Перегляд майстрів':
    #     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    #     back_button = types.KeyboardButton(text='Головне меню')
    #     keyboard.add(back_button)
    #     bot.send_message(message.chat.id, 'Секунду, дізнаюсь інформацію...', reply_markup=keyboard)
    #
    #     keyboard = types.InlineKeyboardMarkup(row_width=2)
    #
    #     masters = db.get_all_masters()
    #     msg = 'Ось наші майстри:\n'
    #     btn = []
    #     for mt in masters:
    #         btn.append(types.InlineKeyboardButton(
    #             text=mt[1],
    #             callback_data='mast_' + str(mt[0])))
    #         msg += str(mt[2]) + ' ' + mt[1] + ' з досвідом ' + '%s р.' % mt[3] + '\n' + mt[4] + '\n'
    #     [keyboard.add(b) for b in btn]
    #
    #     bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    #     bot.add_data(message.from_user.id, message.chat.id, first='mast')
    #     print('user_id: ' + str(message.from_user.id) + ' chat_id: ' + str(message.chat.id))
        # bot.set_state(message.from_user.id, UserStates.services, message.chat.id)
    elif message.text == 'Мої записи':
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        reg_button = types.KeyboardButton(text="Поділитись своїм номером телефону", request_contact=True)
        keyboard.add(reg_button)
        bot.send_message(message.chat.id,
                         "Для цього поділіться, будь-ласка, своїм номер телефону",
                         reply_markup=keyboard)
        bot.add_data(user_id=message.chat.id, chat_id=message.chat.id, booking=False)


@bot.message_handler(commands=['delete'])
def delete_master(message):
    """Видалення майстра з БД, який звільнився"""

    try:
        master_id = db.get_master_id_with_user_id(message.from_user.id)
        master = db.get_master(master_id)

        if master[5] == config.main_phone_number:
            masters = db.get_all_masters()

            keyboard = types.InlineKeyboardMarkup()
            buttons = [types.InlineKeyboardButton(text=master[1], callback_data=f'delete_{master[0]}')
                       for master in masters]
            for btn in buttons:
                keyboard.add(btn)

            bot.send_message(message.chat.id, 'Виберіть майстра, який є звільнений', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Вибачте, але у вас немає права на цю дію')
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Вибачте, але вам  не доступна ця функція')



@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    db.set_client(message.contact.phone_number, message.contact.first_name)
    client_id = db.get_client_id(message.contact.phone_number)

    if bot.get_state(message.from_user.id) == UserStates.share_contact.name:
        """Завершення реєстрації: збереження всієї інформації в БД"""

        print(message.contact.phone_number)

        try:
            with bot.retrieve_data(message.chat.id) as data:
                db.set_master(name=data['name'], user_id=message.from_user.id,
                              info=data['info'], experience=data['experience'],
                              phone_number=message.contact.phone_number)
                services = data.get('reg_services')

            master_id = db.get_master_id_with_user_id(message.from_user.id)

            for service in services:
                service_id = db.get_service_id_with_title(service)
                print(service_id)
                db.set_service_master_relation(master_id, service_id)

            # state.set(UserStates.set_work_to)
            bot.set_state(message.from_user.id, UserStates.set_work_to)

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

        with bot.retrieve_data(message.chat.id) as data:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            working_hours_button = types.KeyboardButton('Коли ви працюєте?')
            available_serv = types.KeyboardButton(text='Доступні послуги')
            # available_master = types.KeyboardButton(text='Перегляд майстрів')
            my_book = types.KeyboardButton(text='Мої записи')
            keyboard.add(working_hours_button, available_serv, my_book)

            if data['booking']:
                db.set_booking(data['date_time'], data['service_id'], data['master_id'], client_id)

                # booking_id = db.get_booking(client_id, 1)
                # schedule_id = db.get_schedule(data['date_time'], data['master_id'])
                # hour = data['date_time'].strftime('%H')
                # db.change_schedule(hour, booking_id, schedule_id)

                bot.send_message(message.chat.id, 'Вітаю, ви записались!', reply_markup=keyboard)
                bot.set_state(message.from_user.id, UserStates.main_menu, message.chat.id)
            elif not data['booking']:
                try:
                    client_id = db.get_client_id(message.contact.phone_number)
                    bookings = db.get_all_bookings_with_client(client_id)

                    info=[]
                    for booking in bookings:
                        info.append(db.get_booking(booking))


                    msgs = []
                    for i in info:
                        master_info = db.get_master(i[5])
                        service_info = db.get_service(i[4])

                        date = i[0]
                        time = i[1]

                        msgs.append(f'Дата: {date}\nЧас на котру потрібно підійти: {time}\nІм\'я вашого майстра: '
                                    f'{master_info[1]}\nПослуга, за якою ви звертаєтесь до нас: {service_info[1]}\nЦіна: {service_info[2]}грн')

                    msg = 'Ось інформація про ваші записи:\n' + '\n\n'.join(msgs)
                    bot.send_message(message.chat.id, msg, reply_markup=keyboard)
                except:
                    bot.send_message(message.chat.id, 'У вас немає запису', reply_markup=keyboard)

        bot.set_state(message.from_user.id, UserStates.main_menu, message.chat.id)


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
        bot.set_state(message.from_user.id, UserStates.name, message.chat.id)
        bot.send_message(message.chat.id, 'Як тебе звати? (Яке ім\'я буде відображатись користувачам)')
    else:
        bot.send_message(message.chat.id, 'Вибачте, але пароль не правильний')

@bot.message_handler(state=UserStates.name)
def becoming_master_name(message, state: StateContext):
    """Бот зберігає собі ім'я майстра і задає йому запитання про досвід"""

    # state = bot.get_current_state(message.chat.id)
    state.set(UserStates.reg_services)
    bot.send_message(message.chat.id, 'Який у вас досвід? (лише цифрою в роках)')
    state.add_data(name=message.text)


# @bot.message_handler(state=UserStates.experience)
# def becoming_master_experience(message, state):
#     """Бот зберігає досвід майстра і задає йому запитання щодо його досвіду"""
#
#     state.set(UserStates.reg_services)
#     bot.send_message(message.chat.id, 'Виберіть які послуги ви надаєте')
#     state.add_data(experience=message.text)


@bot.message_handler(state=UserStates.reg_services)
def choosing_services(message, state):
    """Бот зберігає досвід майстра і задає йому запитання щодо його досвіду
    Бот виводить повідомлення з варіантами послуг і можливістю створити нову послугу"""

    state.add_data(experience=message.text)

    keyboard = types.InlineKeyboardMarkup()
    services = db.get_all_services()
    btn = []

    with state.data() as data:
        number = len(data.get('reg_services', []))

    if number == 0:
        state.add_data(reg_services = [])
        info = []
    else:
        with state.data() as data:
            info = data.get('reg_services')


    for service in services:
        if service[1] not in info:
            btn.append(types.InlineKeyboardButton(text=service[1], callback_data='reg_serv_' + service[1]))

    [keyboard.add(b) for b in btn]

    keyboard.add(types.InlineKeyboardButton(text='Додати нову послугу', callback_data='add_new_service'))

    if number >= 1:
        keyboard.add(types.InlineKeyboardButton(text='Більше я не надаю послуг', callback_data='end_registration'))

    bot.send_message(message.chat.id, 'Виберіть які послуги ви надаєте', reply_markup=keyboard)


@bot.message_handler(state=UserStates.info)
def becoming_master_end(message, state):
    """Збереження опису і перенаправлення для поширення свого номеру телефона"""

    # state.set(UserStates.main_master)

    state.set(UserStates.share_contact)
    state.add_data(info = message.text)

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    share_contact_button = types.KeyboardButton(text="Поділитись своїм номером телефону", request_contact=True)
    keyboard.add(share_contact_button)

    bot.send_message(message.chat.id,
                     "Для закінчення вашої реєстрації поділіться, будь-ласка, своїм номером телефону",
                     reply_markup=keyboard)


    # Main master menu

    # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # change_info = types.KeyboardButton(text='Змінити інформацію про себе')
    # change_services = types.KeyboardButton(text='Послуги, які я надаю')
    # schedule = types.KeyboardButton(text='Мій розклад')
    # term = types.KeyboardButton(text='Продовжити дату, до якої можливий запис')
    # keyboard.add(change_info, change_services, schedule, term)
    #
    # bot.send_message(message.chat.id, 'Дякую, реєстрацію успішно завершено!', reply_markup=keyboard)


@bot.message_handler(state=UserStates.main_master)
def main_master_menu(message, state):
    if message.text == 'Змінити інформацію про себе':
        keyboard = types.InlineKeyboardMarkup()
        change_name = types.InlineKeyboardButton(text='Ім\'я', callback_data='change_name')
        change_info = types.InlineKeyboardButton(text='Опис', callback_data='change_info')
        change_experience = types.InlineKeyboardButton(text='Досвід', callback_data='change_experience')
        keyboard.add(change_name, change_experience, change_info)

        bot.send_message(message.chat.id, 'Що саме Ви хочете змінити?', reply_markup=keyboard)
    elif message.text == 'Послуги, які я надаю':
        master_id = db.get_master_id_with_user_id(message.from_user.id)
        service_ids = db.get_all_services_with_master(master_id)
        msg = ''

        for service_id in service_ids:
            service = db.get_service(service_id)
            msg = msg + service[1] + ' -- ' + str(service[2]) + '\n'

        msg = 'Ось послуги, які ви надаєте:\n' + msg

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    elif message.text == 'Мій розклад':
        master_id = db.get_master_id_with_user_id(message.from_user.id)
        booking_ids = db.get_all_bookings_with_master(master_id)
        bookings = [db.get_booking(booking_id) for booking_id in booking_ids]
        bookings_by_name = []


        for booking in bookings:
            bookings_by_name.append({})
            service = db.get_service(booking[-3])
            client = db.get_client(booking[-1])

            print(service, client)

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

        state.set(UserStates.get_client_date)
        state.add_data(get_client_date = bookings_by_name)


        bot.send_message(message.chat.id, 'Щоб отримати інформацію про клієнта, будь ласка, виберіть його замовлення',
                         reply_markup=keyboard)
    elif message.text == 'Сформувати свій графік':
        state.set(UserStates.set_work_to)

        bot.send_message(message.chat.id, 'Напишіть, будь ласка, до якого дня включно ви плануєте працювати(день.місяць.рік)')

    elif message.text == 'Повернутись на головний екран':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        change_info = types.KeyboardButton(text='Змінити інформацію про себе')
        change_services = types.KeyboardButton(text='Послуги, які я надаю')
        schedule = types.KeyboardButton(text='Мій розклад')
        term = types.KeyboardButton(text='Сформувати свій графік')
        keyboard.add(change_info, change_services, schedule, term)

        bot.send_message(message.chat.id, 'Вас повернуто на головний екран', reply_markup=keyboard)


@bot.message_handler(state=UserStates.set_work_to)
def set_schedule_start(message, state):
    """Отримання даних про терміну роботи, запит про вихідні дні"""

    try:
        txt = message.text.split('.')
        date = datetime.date(int(txt[2]), int(txt[1]), int(txt[0]))
        date = date.strftime('%d.%m.%Y')

        state.set(UserStates.set_days_off)
        db.set_master_work_to(message.from_user.id, date)

        keyboard = types.InlineKeyboardMarkup(row_width=7)
        days = sort_days(date)
        state.add_data(days = days)
        month = next(iter(days))
        state.add_data(month = month)
        state.add_data(days_off = [])
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

        state.add_data(sent_message = msg)
    except Exception as e:
        print(e)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(message.chat.id, 'Ви ввели не правильно, будь ласка, спробуйте ще раз',
                         reply_markup=keyboard)


@bot.message_handler(state=UserStates.set_days_off)
def set_schedule(message, state):
    """Отримання даних про вихідні дні"""

    try:
        txt = message.text.split(',')
        list = [element.split('.') for element in txt]

        master_id = db.get_master_id_with_user_id(message.from_user.id)

        for day_off in list:
            date = datetime.date(day=int(day_off[0]), month=int(day_off[1]), year=int(day_off[2]))
            db.set_day_off(date, master_id)

        state.set(UserStates.main_master)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(message.chat.id, 'Ваш графік сформовано!', reply_markup=keyboard)

    except Exception as e:
        print(e)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(message.chat.id, 'Ви ввели не правильно, будь ласка, спробуйте ще раз', reply_markup=keyboard)


# CALLBACK_QUERY_HANDLERS
@bot.callback_query_handler(func=lambda call: call.data.startswith('setting_hours_'))
def set_break_hours(call: types.CallbackQuery, state):
    """Функція яка обробляє встановлення перерв"""

    command = call.data[14:]
    all_hours = [x/2 for x in range(16, 41)]
    WORK_HOURS = []
    for hour in all_hours:
        if hour % 1 == 0:
            WORK_HOURS.append(str(int(hour)) + ':00')
        elif hour % 1 == 0.5:
            WORK_HOURS.append(str(int(hour - 0.5)) + ':30')

    with state.data() as data:
        days = data.get('days')
        month = data.get('month')
        days_off = data.get('days_off')
        hour_breaks = data.get('hour_breaks')
        msg_id = data.get('sent_message').message_id

    match command:
        case 'next':
            months = iter(days)
            while next(months) != month:
                pass
            new_month = next(months)
            state.add_data(month=new_month)
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

            msg = bot.edit_message_text(f'Виберіть дні для вибору перерви\n\nМісяць: {new_month}',
                                        chat_id=call.message.chat.id, message_id=msg_id, reply_markup=keyboard)

            state.add_data(sent_message=msg)
        case 'back':
            reversed_days = {key: value for key, value in reversed(days.items())}
            months = iter(reversed_days)
            while next(months) != month:
                pass
            new_month = next(months)
            state.add_data(month=new_month)
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

            msg = bot.edit_message_text(f'Виберіть дні для вибору перерви\n\nМісяць: {new_month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            state.add_data(sent_message=msg)
        case 'complete_all':
            bot.delete_message(call.message.chat.id, msg_id)
            bot.send_message(call.message.chat.id, 'Ваш графік сформовано!')
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

            msg = bot.edit_message_text(f'Виберіть дні для вибору перерви\n\nМісяць: {month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            state.add_data(sent_message=msg)
        case str() if command.startswith('day_'):
            master_id = db.get_master_id_with_user_id(call.from_user.id)
            hours = db.get_break_hours_master(master_id)

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

            state.add_data(sent_message=msg)
        case str() if command.startswith('hour_'):
            master_id = db.get_master_id_with_user_id(call.from_user.id)
            day, hour = command[5:].split('_')
            db.set_break_hour(hour, day, master_id)

            hours = db.get_break_hours_master(master_id)

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

            state.add_data(sent_message=msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith('setting_days_off_'))
def set_days_off(call: types.CallbackQuery, state):
    """Функція яка керує механізмом книжечки для вибору вихідних днів"""

    command = call.data[17:]

    with state.data() as data:
        days = data.get('days')
        month = data.get('month')
        days_off = data.get('days_off')
        msg_id = data.get('sent_message').message_id

    match command:
        case 'next':
            months = iter(days)
            while next(months) != month:
                pass
            new_month = next(months)
            state.add_data(month = new_month)
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

            for num_week, week in weeks.items():
                week_btns = []
                for day in week:
                    if day in days_off:
                        week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                    else:
                        week_btns.append(types.InlineKeyboardButton(text=day.split('-')[2],
                                                                    callback_data='setting_days_off_' + day))

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

            complete = types.InlineKeyboardButton(text='Завершити вибір вихідних днів',
                                                  callback_data='setting_days_off_complete')
            keyboard.add(complete)

            msg = bot.edit_message_text(f'Виберіть вихідні дні\n\nМісяць: {new_month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            state.add_data(sent_message=msg)
        case 'back':
            reversed_days = {key: value for key, value in reversed(days.items())}
            months = iter(reversed_days)
            while next(months) != month:
                pass
            new_month = next(months)
            state.add_data(month=new_month)
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

            for num_week, week in weeks.items():
                week_btns = []
                for day in week:
                    if day in days_off:
                        week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                    else:
                        week_btns.append(types.InlineKeyboardButton(text=day.split('-')[2],
                                                                    callback_data='setting_days_off_' + day))

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

            complete = types.InlineKeyboardButton(text='Завершити вибір вихідних днів',
                                                  callback_data='setting_days_off_complete')
            keyboard.add(complete)

            msg = bot.edit_message_text(f'Виберіть вихідні дні\n\nМісяць: {new_month}', chat_id=call.message.chat.id,
                                       message_id=msg_id, reply_markup=keyboard)

            state.add_data(sent_message=msg)
        case 'complete':
            try:
                list = [element.split('-') for element in days_off]

                master_id = db.get_master_id_with_user_id(call.from_user.id)

                for day_off in list:
                    date = datetime.date(day=int(day_off[2]), month=int(day_off[1]), year=int(day_off[0]))
                    db.set_day_off(date, master_id)

            except Exception as e:
                print(e)

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

            state.add_data(hour_breaks = [])

            msg = bot.edit_message_text(f'Виберіть день для якого хочете відредагувати робочі години\n\n'
                                        f'Місяць: {month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            state.add_data(sent_message=msg)

        case _:
            days_off.append(command)
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

            for num_week, week in weeks.items():
                week_btns = []
                for day in week:
                    if day in days_off:
                        week_btns.append(types.InlineKeyboardButton(text='-', callback_data='nothing'))
                    else:
                        week_btns.append(types.InlineKeyboardButton(text=day.split('-')[2],
                                                                    callback_data='setting_days_off_' + day))

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

            complete = types.InlineKeyboardButton(text='Завершити вибір вихідних днів',
                                                  callback_data='setting_days_off_complete')
            keyboard.add(complete)

            msg = bot.edit_message_text(f'Виберіть вихідні дні\n\nМісяць: {month}', chat_id=call.message.chat.id,
                                        message_id=msg_id, reply_markup=keyboard)

            state.add_data(sent_message=msg)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_master_from_db(call: types.CallbackQuery, state):
    """Видалення певного майстра з БД"""

    try:
        db.delete_master_from_db(call.data[7:])
        bot.send_message(call.message.chat.id, 'Видалено!')
    except:
        bot.send_message(call.message.chat.id, 'Щось пішло не так')

@bot.callback_query_handler(func=lambda call: call.data.startswith('master_booking_'))
def master_booking(call: types.CallbackQuery, state):
    """Реалізація книжечки для отримання інформації про клієнта"""


    if 'date' in call.data:
        with state.data() as data:
            bookings = []
            for booking in data.get('get_client_date'):
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

        state.set(UserStates.get_client_time)
        state.add_data(get_client_time=bookings)

        bot.send_message(call.message.chat.id, 'Щоб отримати інформацію про клієнта, будь ласка, виберіть його замовлення',
                         reply_markup=keyboard)

    elif 'time' in call.data:
        with state.data() as data:
            bookings = []
            for booking in data.get('get_client_time'):
                if booking['start_time'] == call.data[20:]:
                    bookings.append(booking)

        state.set(UserStates.main_master)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        back = types.KeyboardButton(text='Повернутись на головний екран')
        keyboard.add(back)

        bot.send_message(call.message.chat.id, f"Ім\'я замовника: {bookings[0]['client_name']},\nномер телефону замовника:{bookings[0]['phone_number']}",
                         reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('change_'))
def changing_master(call: types.CallbackQuery, state):
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

    bot.set_state(message.from_user.id, UserStates.main_master, message.chat.id)

    db.set_master_name(message.text, message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back = types.KeyboardButton(text='Повернутись на головний екран')
    keyboard.add(back)

    bot.send_message(message.chat.id, 'ваше ім\'я змінено!', reply_markup=keyboard)


def changing_master_info(message):
    """Зміна опису майстра"""

    bot.set_state(message.from_user.id, UserStates.main_master, message.chat.id)

    db.set_master_info(message.text, message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back = types.KeyboardButton(text='Повернутись на головний екран')
    keyboard.add(back)

    bot.send_message(message.chat.id, 'ваш опис змінено!', reply_markup=keyboard)


def changing_master_experience(message):
    """Зміна досвіду майстра"""

    bot.set_state(message.from_user.id, UserStates.main_master, message.chat.id)

    db.set_master_experience(message.text, message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    back = types.KeyboardButton(text='Повернутись на головний екран')
    keyboard.add(back)

    bot.send_message(message.chat.id, 'ваш досвід змінено!', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('end_registration'))
def ending_registration(call: types.CallbackQuery, state):
    """Закінчення реєстрації: внесення даних до БД"""

    state.set(UserStates.info)

    bot.send_message(call.message.chat.id, 'Опишіть себе, свої вміння')


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_new_service'))
def start_add_new_service(call: types.CallbackQuery, state):
    """Бот задає запитання на рахунок назви послуги"""

    state.set(UserStates.add_new_service)

    bot.send_message(call.message.chat.id,
                     'Щоб створити нову послугу ви повинні дотриматись формату:\n'
                     'назва, ціна, час(у хвилинах)     коми обов\'язкові')


@bot.message_handler(state=UserStates.add_new_service)
def end_add_new_service(message, state):
    """Бот звертається до БД і додає нову послугу"""

    state.set(UserStates.reg_services)

    with state.data() as data:
        info = data.get('reg_services')

    try:
        txt = message.text.split(', ')
        info.append(txt[0])
        state.add_data(reg_services=info)
        db.set_service(title=txt[0], cost=txt[1], duration=txt[2])
        bot.send_message(message.chat.id, 'Додано')
    except:
        bot.send_message(message.chat.id, 'Будь ласка, перевірте чи ви дотримались правильної форми. Якщо все було дотримано правильно,'
                                          'то зверніться до тех. підтримки')
    finally:
        choosing_services(message, state)


@bot.callback_query_handler(func=lambda call: call.data.startswith('reg_serv_'))
def registration_services_callback(call: types.CallbackQuery, state):
    state.set(UserStates.reg_services)

    with state.data() as data:
        serv_info = data.get('reg_services')


    # serv_info[0] = serv_info[0] + 1
    serv_info.append(call.data[9:])

    state.add_data(reg_services = serv_info)

    bot.send_message(call.message.chat.id, 'Додано!')


@bot.callback_query_handler(func=lambda call: call.data.startswith('serv_'))
def services_callback(call: types.CallbackQuery):
    serv_id = int(call.data[5:])
    bot.add_data(user_id=call.message.chat.id, chat_id=call.message.chat.id, service_id=serv_id)
    masters_id = db.get_all_masters_with_service(serv_id)
    masters = []
    for master_id in masters_id:
        masters.append(db.get_master(master_id))

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    msg = 'Ось майстри, які цим займаються:\n'
    btn = []

    for mt in masters:
        btn.append(types.InlineKeyboardButton(
            text=mt[1] + ', ' + str(mt[2]), callback_data='book_' + str(serv_id) + '_' + str(mt[0])))
        msg += str(mt[2]) + ' ' + mt[1] + ' з досвідом ' + '%s р.' % mt[3] + '\n'
    [keyboard.add(b) for b in btn]

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg,
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('mast_'))
def masters_callback(call: types.CallbackQuery):
    mast_id = int(call.data[5:])
    bot.add_data(user_id=call.message.chat.id, chat_id=call.message.chat.id, master_id=mast_id)
    services_id = db.get_all_services_with_master(mast_id)
    services = []

    for service_id in services_id:
        services.append(db.get_service(service_id))

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    btn = []
    msg = 'Ось наші послуги, які пропонує цей майстер:\n'

    for sp in services:
        btn.append(types.InlineKeyboardButton(text=sp[1], callback_data='book_' + str(sp[0]) + '_' + str(mast_id)))
        msg = msg + sp[1] + '  ---  ' + 'ціна: ' + str(sp[2]) + '\n'
    [keyboard.add(b) for b in btn]

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=msg,
                          reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('book_'))
def book_callback(call: types.CallbackQuery):
    serv_mast = call.data.split('_')
    service_id = serv_mast[1]
    master_id = serv_mast[2]
    bot.add_data(user_id=call.message.chat.id, chat_id=call.message.chat.id, master_id=master_id, service_id=service_id)
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
    # bot.send_message(call.message.chat.id, msg, reply_markup = keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('bookday_'))
def bookday_callback(call: types.CallbackQuery):
    data = call.data.split('_')
    day = data[1]
    bot.add_data(user_id=call.message.chat.id, chat_id=call.message.chat.id, day=day)

    with bot.retrieve_data(call.message.chat.id) as state_data:
        duration = db.get_duration(state_data['service_id'])
        hours = plot.get_day_of_master(state_data['master_id'], day, duration)
    print(hours)
    # day_may = schedule.index(day)
    # hours = list(schedule[day_may + 1].keys())

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    btn = []
    for hour in hours:
        btn.append(types.InlineKeyboardButton(text=hour, callback_data='bookhour_' + hour))
    for x in range(len(btn)):
        keyboard.add(btn[x])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Ось вільні години в цей день', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('bookhour_'))
def bookhour_callback(call: types.CallbackQuery):
    data = call.data.split('_')
    print(data)
    # hour = data[1]
    # time = hour[:5]
    time = data[1]

    with bot.retrieve_data(call.message.chat.id) as data:
        dt = data['day'] + ' ' + time

    print(dt)
    date_time = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M')
    bot.add_data(user_id=call.message.chat.id, chat_id=call.message.chat.id, date_time=date_time)

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    share_contact_button = types.KeyboardButton(text="Поділитись своїм номером телефону", request_contact=True)
    keyboard.add(share_contact_button)

    bot.send_message(call.message.chat.id,
                     "Для бронювання поділіться, будь-ласка, своїм номером телефону",
                     reply_markup=keyboard)

    bot.add_data(user_id=call.message.chat.id, chat_id=call.message.chat.id, booking=True)
    bot.set_state(user_id=call.message.chat.id, state=UserStates.booking, chat_id=call.message.chat.id)


bot.add_custom_filter(custom_filters.StateFilter(bot))

from telebot.states.sync.middleware import StateMiddleware

bot.setup_middleware(StateMiddleware(bot))

bot.infinity_polling()