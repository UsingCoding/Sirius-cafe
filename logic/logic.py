# -*- coding: utf-8 -*-

import re
from logic.vocabulary import *
from math import fabs

#Обработчик входящих сообщений

def message_handler(stage):
  if stage == 'greeting':
    answer = 'Приветствую вас в нашем замечательном кафе!'
    return answer

  elif stage == 'menu':
    answer = 'Наше замечательное меню можно увидеть в vocabulary.py!'
    return answer

  elif stage == 'dishes':
    answer = 'Ваш текущий заказ: '+', '.join(dishes)+'. Если Вы определилсь с заказом,'+\
                                                    ' то выберите свое место.'

    return answer

  elif stage == 'place':
    answer = 'Можете пройти за свой стол. Скоро Ваш заказ будет готов. Для завершения попросите счёт.'
    return answer

  elif stage == 'bye':
    answer = 'о пока'
    return answer

  else:
    answer = 'ты тупой сука'
    return answer

def check_counter(message):
  check = 0

  for dish in range(len(dishes)):
    check += dishes[dish]

  return check


def current_stage(message, stage):
  #print('Вычисление стадии...')
  message = re.sub('[^А-я]', ' ', message.lower())
  message = message.split()    # Список из слов сообщения
  menu_stages = 0     # Количество упоминаний ключ  евых слов menu и stages в одном сообщении
  place_stages = 0
  greeting_stages = 0
  bye_stages = 0
  dishes_stages = 0
  print(stage, message)
  for i in range(len(message)):     # Подсчет количества каждого из ключевых слов словарей place и menu
    if message[i] in greeting_keywords:
      greeting_stages += 1

    elif message[i] in menu_keywords:
      menu_stages += 1

    elif message[i] in place_keywords:
      place_stages += 1

    elif message[i] in bye_keywords:
      bye_stages += 1

  if stage in ['menu', 'dishes', 'place']:
    for i in range(3):
      message.insert(0, 'a')

    for i in range(0, len(message)-2):
      if message[i] + ' ' + message[i + 1] + ' ' + message[i + 2] in dishes_keywords:
        if message[i] + ' ' + message[i + 1] + ' ' + message[i + 2] not in dishes:
          #print('А3')
          dishes.append(message[i] + ' ' + message[i + 1] + ' ' + message[i + 2])
          print('Блюдо', message[i] + ' ' + message[i + 1] + ' ' + message[i + 2], 'было добавлено.')
          dishes_stages += 1

      elif message[i + 1] + ' ' + message[i + 2] in dishes_keywords:
        if message[i] + ' ' + message[i + 1] not in dishes:
          #print('А2')
          dishes.append(message[i + 1] + ' ' + message[i + 2])
          print('Блюдо', message[i + 1] + ' ' + message[i + 2], 'было добавлено.')
          dishes_stages += 1

      elif message[i + 2] in dishes_keywords:
        if message[i + 2] not in dishes:
          #print('А1')
          dishes.append(message[i + 2])
          print('Блюдо', message[i + 2], 'было добавлено.')
          dishes_stages += 1


  try:
    if greeting_stages > max(menu_stages, place_stages, bye_stages, dishes_stages)*2.9 and stage in ['pre', 'tupoy']:  # Этап приветствия
      return 'greeting'

    if bye_stages > max(menu_stages, place_stages, greeting_stages, dishes_stages)*2.9 and stage in ['place']:  # Этап прощания
      return 'bye'

    if dishes_stages > max(greeting_stages, place_stages, bye_stages)*2.9 and stage in ['menu', 'dishes']:
      return 'dishes'

    if message[0] in question_words:  # Условие, если сообщения начинается с вопросительного слова
      #print('a')

      if max(menu_stages, place_stages, dishes_stages)/min(menu_stages, place_stages, dishes_stages) >= 3.0:
        #print('a.1')

        if menu_stages == max(menu_stages, place_stages, dishes_stages) and stage == 'greeting':
          #print('a.1.1')
          return 'menu'

        elif max(menu_stages, place_stages, dishes_stages) == place_stages and stage == 'dishes':
          #print('a.1.2')
          return 'place'

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

        if menu_stages > place_stages and stage == 'greeting':
          #print('b.2.1')
          return 'menu'

        elif place_stages > menu_stages and stage == 'menu':
          #print('b.2.2')
          return 'place'

        else:
          #print('b.2.3')
          return stage

      else:
        #print('b.3')
        return 'tupoy'

  except ZeroDivisionError:
    if menu_stages != 0 and stage == 'greeting':
      return 'menu'

    elif place_stages != 0 and stage == 'dishes':
      return 'place'

    else:
      return stage

'''stage = 'pre'

while stage != 'bye':
  message = str(input())

  if not message.isspace() and message != '':
    stage = current_stage(message, stage)
    answer = message_handler(stage)
    #print('stage:', stage)
    print(answer)
    #print('вот тебе эту хуйню выдаст:')
    #print(stage, answer)

  else:
    print('ты тупой или да')'''
