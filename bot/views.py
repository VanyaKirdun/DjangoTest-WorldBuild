import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from django.http import HttpResponse, HttpResponseBadRequest
from index.models import Worker, PositionList, BuildObject
import datetime
import json
import calendar as calendario
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from index.scripts.calcSalary import calcSalary
from datetime import date
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from jsonschema import validate



authStatus = False
menuStatus = ''
login = ''
password = ''
worker = None
yearData = datetime.datetime.now().year
monthData = ''
dayData = ''
monthArray = []
for i in range(1, 13):
  monthArray.append(f'{calendario.month_name[i]}')
  
bot = telebot.TeleBot(settings.TOKEN)

calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")



markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
item1 = types.KeyboardButton('Сменить пользователя')
item2 = types.KeyboardButton('Отчёт об отработных часах')
item3 = types.KeyboardButton('Зарплата')
item4 = types.KeyboardButton('Отчёт')
markup.add(item1, item2, item3, item4)

markupDeleted = types.ReplyKeyboardRemove()


def setwebhook(request):
  bot.set_webhook(url=settings.TELEGRAM_API_URL+ "setWebhook?url=" + settings.URL)
  return HttpResponse(f"{bot.get_webhook_info()}")

@csrf_exempt
def telegram_bot(request):
    if request.META['CONTENT_TYPE'] == 'application/json':
        update = telebot.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])

    return HttpResponse('<h1>Ты подключился!</h1>')
  

  
@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
  global login, password, worker, authStatus, menuStatus, markup, markupDeleted

  if authStatus:
    
    bot.send_message(message.chat.id, f'Привет, {worker[0].name}!', reply_markup=markup)
  else:
    login = ''
    password = ''
    
    bot.send_message(message.chat.id, f'Авторизируйтесь!\n'
                                      f'Введите логин:', reply_markup=markupDeleted)
    
    
@bot.message_handler(content_types=["text"]) 
def bot_message(message: telebot.types.Message = None, call: CallbackQuery = None):
  global login, password, worker, authStatus, menuStatus, yearData, monthData, dayData
  if authStatus == False:
    if login == '':
      login = message.text
      bot.send_message(message.chat.id, f'Введите пароль:')
    elif login != '' and password == '':
      password = message.text
      worker = Worker.objects.all().filter(login = login, password = password)
      if len(worker) > 0:
        
        bot.send_message(message.chat.id, f'Вы авторизированы!')
        authStatus = True
        start(message)
      else:
        login = ''
        password = ''
        bot.send_message(message.chat.id, 'Не верный логин или пароль!\n'
                                          'Введите логин: ')
    else:
      bot.send_message(message.chat.id, f'Вы авторизированы!')
      start(message)
  else:
    if menuStatus == '':
      match message.text:
        case 'Сменить пользователя':
          authStatus = False
          menuStatus = ''
          start(message)
        case 'Отчёт об отработных часах':
          try:
            menuStatus = 'timeWorked'
            
            monthChoose = types.InlineKeyboardMarkup()
            monthChoose.add(types.InlineKeyboardButton(text=f'{yearData}',callback_data='change_years'))
            mass = []
            for i in range(1, 13):
              mass.append(types.InlineKeyboardButton(text=f'{calendario.month_name[i]}',callback_data=f'{calendario.month_name[i]}'))
              if i % 2 ==0:
                monthChoose.add(*mass)
                mass = []

            bot.send_message(message.chat.id, 'Выберите месяц', reply_markup=monthChoose)
          except Exception as e:
            print(e)
        case 'Зарплата':
          menuStatus = 'salary'
            
          monthChoose = types.InlineKeyboardMarkup()
          print('yearData: ', yearData)
          monthChoose.add(types.InlineKeyboardButton(text=f'{yearData}',callback_data='change_years'))
          mass = []
          for i in range(1, 13):
            mass.append(types.InlineKeyboardButton(text=f'{calendario.month_name[i]}',callback_data=f'{calendario.month_name[i]}'))
            if i % 2 ==0:
              monthChoose.add(*mass)
              mass = []

          bot.send_message(message.chat.id, 'Выберите месяц', reply_markup=monthChoose)
        case 'Отчёт':
          menuStatus = 'report'
          bot.send_message(message.chat.id, 'Выберите дату ', reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=datetime.datetime.now().year,
            month=datetime.datetime.now().month, 
          ))
          
    else:
      match menuStatus:
        case 'timeWorked':
          try: 
            if yearData!= '' and monthData != '':
              text = ''
              objects = BuildObject.objects.all()
              for dayNumber in worker[0].timeWork[yearData][monthData]['data']:
                text = text + f'{dayNumber})'
                for objectID in worker[0].timeWork[yearData][monthData]['data'][dayNumber]:
                  text = text + f'  {objects.filter(id = objectID)[0].name}: {worker[0].timeWork[yearData][monthData]['data'][dayNumber][objectID]}\n'
              if message is not None:
                bot.send_message(message.chat.id, text)
              elif call is not None:
                bot.send_message(call.from_user.id, text)
              yearData = datetime.datetime.now().year
              monthData = ''
              dayData = ''
              menuStatus = ''
          except Exception as e:
              print(e)
              bot.send_message(call.from_user.id, 'Об этой дате нет данных!')
              yearData = datetime.datetime.now().year
              monthData = ''
              dayData = ''
              menuStatus = ''
              
        case 'salary':
          if yearData!= '' and monthData !='':
            try: 
              objects = BuildObject.objects.all()

              workedHoursData = worker[0].timeWork[yearData][monthData]['data']
              positionSalary = PositionList.objects.all()[worker[0].position-1].salaryOfTime
              
              totalSalary = calcSalary(workedHoursData, objects, positionSalary)
              

              if message is not None:
                bot.send_message(message.chat.id, f'Заработано: {totalSalary}€')
              elif call is not None:
                bot.send_message(call.from_user.id, f'Заработано: {totalSalary}€')
              yearData = datetime.datetime.now().year
              monthData = ''
              menuStatus = ''
            except:
              if message is not None:
                bot.send_message(message.chat.id, f'{monthData}: данных об этом месяце отсуствуют!')
              elif call is not None:
                bot.send_message(call.from_user.id, f'{monthData}: данных об этом месяце отсуствуют!')
              
              yearData = datetime.datetime.now().year
              monthData = ''
              menuStatus = ''
        case 'report':
          try:
            objects = BuildObject.objects.all()
            for key in json.loads(message.text):
              objects.filter(id = int(key))[0]
              int(key), float(json.loads(message.text)[key])
          except ValueError:
              bot.send_message(message.chat.id, 'Не правильная форма!')
          except: 
              bot.send_message(message.chat.id, 'Среди указанных номеров обьектов указаны несуществующие!')
          else:
            try:
              if yearData != '' and monthData != '' and dayData != '':
                data = worker[0].timeWork
                if yearData in data and int(datetime.datetime.now().year) != int(yearData) and monthData in data[yearData] and not bool(data[yearData][monthData]['payed']):
                  data[yearData][monthData]['data'][int(dayData)] = json.loads(message.text)
                  worker.update(timeWork=data)
                elif yearData not in data and int(datetime.datetime.now().year) != int(yearData) or monthData not in data[yearData] and int(datetime.datetime.now().year) != int(yearData):
                  bot.send_message(message.chat.id, f'{monthData} {yearData} - невозможно изменить данные за этот период!')
                elif int(datetime.datetime.now().year) != int(yearData) and bool(data[yearData][monthData]['payed']):
                    bot.send_message(message.chat.id, f'{monthData} {yearData} - уже оплачен!')
                else:
                  if int(datetime.datetime.now().year) == int(yearData) and yearData not in data:
                    data[yearData] = {f'{monthData}': {'data': {f'{int(dayData)}': json.loads(message.text)}, "payed": False}}
                    worker.update(timeWork=data)
                  elif int(datetime.datetime.now().year) == int(yearData) and monthData not in data[yearData]:
                    data[yearData][monthData] = {'data': {f'{int(dayData)}': json.loads(message.text)}, "payed": False}
                    worker.update(timeWork=data)
                  elif int(datetime.datetime.now().year) == int(yearData) and not bool(data[yearData][monthData]['payed']):
                    data[yearData][monthData]['data'][int(dayData)] = json.loads(message.text)
                    worker.update(timeWork=data)
                  elif int(datetime.datetime.now().year) == int(yearData) and bool(data[yearData][monthData]['payed']):
                    bot.send_message(message.chat.id, f'{monthData} {yearData} - уже оплачен!')
            except Exception as e:
              print(e)

          finally:
            yearData = datetime.datetime.now().year
            monthData = ''
            dayData=''
            menuStatus = ''
@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix)
)  
def callback_inline(call: CallbackQuery):
  try:
    global yearData, monthData, dayData, menuStatus

    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
      try:
        yearData = date.strftime('%Y')
        monthData = calendario.month_name[int(date.strftime('%m'))].lower()
        dayData = date.strftime('%d')
        
        objectChoose = types.InlineKeyboardMarkup()
        objectChoose.add(types.InlineKeyboardButton(text=f'{yearData}',callback_data='objectChoose'))
        mass = []
        for i in range(1, 13):
          mass.append(types.InlineKeyboardButton(text=f'{calendario.month_name[i]}',callback_data=f'{calendario.month_name[i]}'))
          if i % 2 ==0:
            objectChoose.add(*mass)
            mass = []
        bot.send_message(call.from_user.id, f'Введите данные:')
      except Exception as e:
        print(e)
    elif action == "CANCEL":
      yearData = datetime.datetime.now().year
      monthData = ''
      dayData = ''
      menuStatus = ''
  except Exception as e:
    print(e)


@bot.callback_query_handler(func=lambda call: call.data in monthArray)  
def callback_inline(call):
  try:
    global yearData, monthData, menuStatus
    yearData = call.message.json['reply_markup']['inline_keyboard'][0][0]['text']
    monthData = call.data.lower()
    bot.delete_message(chat_id=call.from_user.id, message_id = call.message.message_id)
    bot_message(call = call)
  except Exception as e:
    print(e)

@bot.callback_query_handler(func=lambda call: call.data == 'change_years')  
def callback_inline(call):
  try:
    mass = []
    for i in range(2001, int(datetime.datetime.now().year) + 1):
      mass.append(types.InlineKeyboardButton(text=f'{i}',callback_data=f'{i}'))
      
    markupYear = types.InlineKeyboardMarkup()
    markupYear.add(*mass)
    bot.edit_message_text(chat_id=call.from_user.id, text='Выберите год', message_id = call.message.message_id, reply_markup = markupYear)
  except Exception as e:
    print(e)
    

  
@bot.callback_query_handler(func=lambda call: int(call.data) in range(2001, int(datetime.datetime.now().year) + 1))  
def callback_inline(call):
  try:
    global yearData
    yearData = call.data
    
    monthChoose = types.InlineKeyboardMarkup()
    monthChoose.add(types.InlineKeyboardButton(text=f'{yearData}',callback_data='change_years'))
    mass = []
    for i in range(1, 13):
      mass.append(types.InlineKeyboardButton(text=f'{calendario.month_name[i]}',callback_data=f'{calendario.month_name[i]}'))
      if i % 2 ==0:
        monthChoose.add(*mass)
        mass = []
    bot.edit_message_text(chat_id=call.from_user.id, text='Выберите месяц', message_id = call.message.message_id, reply_markup = monthChoose)
  except Exception as e:
    print(e)
