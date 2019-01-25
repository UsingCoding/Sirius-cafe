# -*- coding: utf-8 -*-

import re
from utils import *

question_words = ['что', 'какое', 'какой', 'какие', 'можно', 'где', 'куда']
greeting_keywords = ['привет', 'здравствуйте', 'доброе',  'утро', 'добрый', 'вечер']
menu_keywords = ['меню', 'ассортимент', 'блюда', 'заказать', 'можно', 'покажите', 'давайте']
place_keywords = ['сесть', 'место', 'стол', 'столик', 'присести', 'окна', 'окно', 'напротив', 'телевизора', 'приставки', 'телевизор']
place_answers = ['у окна', 'на ваш выбор', 'любое', 'у входа', 'вип']
bye_keywords = ['до', 'свидания', 'пока', 'встречи']
check_keywords = ['чек', 'счет', 'сч']

#Обработчик входящих сообщений

def message_handler(stage):
  if stage == 'greeting':
    answer = 'Здравствуйте!'
    return answer

  elif stage == 'menu':
    answer = 'Ваше меню на экране'
    return answer

  elif stage == 'dishes':
    """answer = 'Если Вы определилсь с заказом,'+\
                                                    ' то выберите место у окна или напротив телевизора.'"""
    answer = 'Определитесь с местом'
    return answer

  elif stage == 'place':
    answer = 'Можете пройти за стол. Для завершения попросите счёт.'
    return answer

  elif stage == 'bye':
    answer = 'До свидания. Хорошего Вам дня.'
    return answer

  else:
    answer = 'Не удалось распознать'
    return answer

def get_check(dishes):
  check = 0

  for i in range(len(dishes)):
    check += dishes_keywords.get(dishes[i])

  answer = 'Стоимость Вашего заказа: ' + str(check) + 'р.'
  return answer


def current_stage(message, stage):
  message = message.split()    # Список из слов сообщения
  menu_stages = 0     # Количество упоминаний ключ  евых слов menu и stages в одном сообщении
  place_stages = 0
  greeting_stages = 0
  bye_stages = 0
  dishes_stages = 0
  check_stages = 0

  for i in range(len(message)):     # Подсчет количества каждого из ключевых слов словарей place и menu
    if message[i] in greeting_keywords:
      greeting_stages += 1

    elif message[i] in menu_keywords:
      menu_stages += 1

    elif message[i] in place_keywords:
      place_stages += 1

    elif message[i] in bye_keywords:
      bye_stages += 1

    elif message[i] in check_keywords:
      check_stages += 1

  if stage in ['menu', 'dishes', 'place']:
    for i in range(3):
      message.insert(0, 'a')

    for i in range(0, len(message)-2):
      if message[i] + ' ' + message[i + 1] + ' ' + message[i + 2] in dishes_keywords:
        if message[i] + ' ' + message[i + 1] + ' ' + message[i + 2] not in dishes:
          #print('А3')
          dishes.append(message[i] + ' ' + message[i + 1] + ' ' + message[i + 2])
          #print('Блюдо', message[i] + ' ' + message[i + 1] + ' ' + message[i + 2], 'было добавлено.')
          dishes_stages += 1

      elif message[i + 1] + ' ' + message[i + 2] in dishes_keywords:
        if message[i] + ' ' + message[i + 1] not in dishes:
          #print('А2')
          dishes.append(message[i + 1] + ' ' + message[i + 2])
          #print('Блюдо', message[i + 1] + ' ' + message[i + 2], 'было добавлено.')
          dishes_stages += 1

      elif message[i + 2] in dishes_keywords:
        if message[i + 2] not in dishes:
          #print('А1')
          dishes.append(message[i + 2])
          #print('Блюдо', message[i + 2], 'было добавлено.')
          dishes_stages += 1


  try:
    if greeting_stages > max(menu_stages, place_stages, bye_stages, dishes_stages, check_stages)*2.9 and stage in ['pre', 'tupoy']:  # Этап приветствия
      return 'greeting'

    if bye_stages > max(menu_stages, place_stages, greeting_stages, dishes_stages, check_stages)*2.9 and stage in ['check']:  # Этап прощания
      return 'bye'

    if dishes_stages > max(greeting_stages, place_stages, bye_stages, check_stages)*2.9 and stage in ['menu', 'dishes', 'check']:
      return 'dishes'

    if check_stages > max(greeting_stages, place_stages, bye_stages, dishes_stages)*2.9 and stage in ['menu', 'dishes', 'place']:
      return 'check', dishes

    if message[0] in question_words:  # Условие, если сообщения начинается с вопросительного слова
      #print('a')

      if max(menu_stages, place_stages, dishes_stages)/min(menu_stages, place_stages, dishes_stages) >= 3.0:
        #print('a.1')

        if menu_stages == max(menu_stages, place_stages, dishes_stages) and stage in ['greeting', 'dishes']:
          #print('a.1.1')
          return 'menu'

        elif max(menu_stages, place_stages, dishes_stages) == place_stages and stage in ['menu', 'dishes']:
          #print('a.1.2')
          if len(dishes) != 0:
            return 'place'

          else:
            return 'menu'

        else:
          #print('a.1.3')
          return stage

      else:
        #print('a.2')
        return stage

    else:
      #print('b')
      if max(menu_stages, place_stages, dishes_stages)/min(menu_stages, place_stages, dishes_stages) > 5.0:
        #print('b.2')

        if menu_stages > place_stages and stage in ['greeting', 'dishes']:
          #print('b.2.1')
          return 'menu'

        elif place_stages > menu_stages and stage in ['menu', 'place']:
          #print('b.2.2')
          if len(dishes) != 0:
            return 'place'

          else:
            return 'menu'

        else:
          #print('b.2.3')
          return stage

      else:
        #print('b.3')
        return stage

  except ZeroDivisionError:
    if menu_stages != 0 and stage in ['greeting', 'dishes']:
      return 'menu'

    elif place_stages != 0 and stage in ['dishes', 'menu']:
      if len(dishes) != 0:
        return 'place'

      else:
        return 'menu'

    else:
      #print('zero')
      return stage

stage = 'pre'

"""
while stage != 'bye':
  message = str(input())
  message = re.sub('[^А-я]', ' ', message.lower())

  if not message.isspace() and message != '':
    stage = current_stage(message, stage)

    if type(stage) is str:
      answer = message_handler(stage)
      print(answer)

    else:
      if len(dishes) != 0:
        answer = get_check(dishes)
        stage = 'check'
        print(answer)

  else:
    print('Не удалось распознать.')
"""
