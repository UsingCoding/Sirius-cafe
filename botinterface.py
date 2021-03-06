from tkinter import *
from misc.utils import *
#from multiprocessing.pool import ThreadPool
import speech_recognition as sr
from logic import *
from multiprocessing.dummy import Process, Queue, Lock
from Stt_and_tts import *
import time

''' Инициализация программы tkinter '''
root = Tk()
root.title('Официант Сириус')
root.resizable(False, False)
c = Canvas(root, bg='#000000', highlightthickness=0, width=800, height=600)

messages = []
bubbles = []
messages_timestamps = []
audio = []
menu = []
# pool = ThreadPool(processes=1)

# Стадия (этап, фаза) общения с официантом
stages = ['pre']

''' События '''
def CheckProc(stage):
    ai = Speech_AI()
    while True:
        time.sleep(0.5)
        print('Checking')
        #message = str(q.get())
        message = input()
        message = message.replace('ё', 'е')
        #print(message + ' Print conv')
        if message == "False":
            break
        elif message == 'None':
            add_message_bubble('right', "...")
            add_message_bubble('left', "Повторите, пожалуйста")
            ai.say("Повторите, пожалуйста")
        else:
            for element in menu:
                c.delete(element)
            print(stage)
            stage = current_stage(message, stage)
            #answer = message_handler(stage)
            message = message[0:1].upper() + message[1:len(message)]
            add_message_bubble('right', message)
            if stage == 'menu':
                menu_show()
                answer = message_handler(stage)
            else:
                if type(stage) is str:
                  answer = message_handler(stage)
                  add_message_bubble('left', answer)
                  print('heresibe')
                elif len(dishes) != 0:
                  answer = get_check(dishes)
                  print('Here')
                  stage = 'check'
                  add_message_bubble('left', answer)
            print(answer)
            #print(stage)
            #ai.say(answer)

def Exit():
    root.destroy()
    q.put('False')


# По нажатию на микрофон, создаем красный микрофон и анимацию, а так же включаем
def mic_clickEvent(event, button_stage):
    if button_stage == 'begin':
        #mic_red.place(x=380, y=506, anchor='nw')
        #mic_red.place_forget()
        A = Speech_AI()
        proc = Process(target=A.work, args=(q, mic_red, lock))
        proc.start()

    elif button_stage == 'end_recording':
        for element in menu:
            c.delete(element)
        print(event.widget)
        event.widget.place_forget()

def menu_show():
    for element in menu:
        c.delete(element)
    menu.append(c.create_image((0,0), image=menu_shadow, anchor='nw', tags='menu_shadow'))
    menu.append(c.create_image((400, 280), image=menu_banner_image, anchor='center', tags='menu_banner'))
    # first row of menu entries
    # При добавлении нового столбца меню (2, 3), по x сдвигать на 165
    menu.append(c.create_text((160, 95), text=menu_placeholder, anchor='nw', font=('Calibri', 13), fill='#606060', tags='menu_entries'))
    c.tag_lower(c.find_withtag('menu_shadow'))
    for ts in messages_timestamps:
        c.tag_lower(ts)
    for msg in messages:
        c.tag_lower(msg)
    for bub in bubbles:
        c.tag_lower(bub)
    c.tag_lower(c.find_withtag('mainbg'))

''' Добавить облачко текста. Параметры - сторона, текст сообщения '''
def add_message_bubble(side, text):
    text = split_text(text, 26)
    now = get_current_time()
    if side == 'left':
        bubbles.insert(0, c.create_image((10, 450), image=bubble_left_image, anchor='nw', tags='bubble_left'))
        messages.insert(0, c.create_text((20, 460), text=text, anchor='nw', font=('Bahnschrift Light Condensed', 13), fill='#f2f2f2'))
        messages_timestamps.insert(0, c.create_text((210, 510), text=now, anchor='nw', font=('Bahnschrift Light Condensed', 10), fill='#f2f2f2'))
    if side == 'right':
        bubbles.insert(0, c.create_image((550, 450), image=bubble_right_image, anchor='nw', tags='bubble_right'))
        messages.insert(0, c.create_text((560, 460), text=text, anchor='nw', font=('Bahnschrift Light Condensed', 13), fill='#f2f2f2'))
        messages_timestamps.insert(0, c.create_text((750, 510), text=now, anchor='nw', font=('Bahnschrift Light Condensed', 10), fill='#f2f2f2'))
    if len(bubbles) > 1: #двигать старые сообщения с их контентом наверх
        for i in range(1, len(bubbles)):
            c.move(bubbles[i], 0, -128)
            c.move(messages_timestamps[i], 0, -128)
            c.move(messages[i],0, -128)
            c.tag_lower(messages[i])
            c.tag_lower(messages_timestamps[i])
            c.tag_lower(bubbles[i])
            if c.coords(bubbles[i])[1] < 10: # если по 'y' ниже 10, удаляем (не забываем удалить из messages методом pop)
                c.delete(bubbles[i])
                c.delete(messages_timestamps[i])
                c.delete(messages[i])
                bubbles.pop(i)
                messages_timestamps.pop(i)
                messages.pop(i)
    # Всегда ставить фон на самый нижний слой, соответственно сообщения слоем выше
    c.tag_lower(c.find_withtag('mainbg'))

''' Подгрузка ассетов: картинки, гиф '''
bg_image = convert_im_for_tk('./assets/bg1.png', (800, 800))
header_image = convert_im_for_tk('./assets/header.png')
menu_banner_image = convert_im_for_tk('./assets/menubanner.png')
menu_burger = convert_im_for_tk('./assets/burger.png')
menu_shadow = convert_im_for_tk('./assets/shadow.png')
bubble_left_image = convert_im_for_tk('./assets/msg_left.png')
bubble_right_image = convert_im_for_tk('./assets/msg_right.png')
waiter_image = convert_im_for_tk('./assets/waiter.png', (48, 48))
mic_image = convert_im_for_tk('./assets/mic.png', (90, 90))
mic_red_image= convert_im_for_tk('./assets/mic_red.png')
mic_active_gif = [PhotoImage(file='./assets/mic_frames/micactive.gif', format = 'gif -index %i' %(i)) for i in range(12)]

''' Рисуем ассеты, расставляем виджеты '''
# Рисуем на полотне
bg = c.create_image(0, 0, image=bg_image, anchor='nw', tags='mainbg')
header = c.create_image(0, 0, image=header_image, anchor='nw')
burger = c.create_image(12, 8, image=menu_burger, anchor='nw')
waiter = c.create_image(290, 35, image=waiter_image, anchor='center')
irina_text = c.create_text(410, 35, text='Официант Сириус', anchor='center', font=('Bahnschrift Light Condensed', 16), fill='#606060')
mic_object = c.create_image(400, 540, image=mic_image, anchor='center', tags='mic')
# Виджеты
mic_red = Button(image=mic_red_image, bd=0, cursor='hand2', highlightthickness=0, state='normal')
add_bubble = Button(text='add bubble', cursor='hand2')
add_bubble.place(x=190, y=530, anchor='nw')
# Создаем, запускаем анимацию и сразу прячем (удаляем ("забываем"))
mic_red.place(x=380, y=506, anchor='nw')
update_frames(0, label=mic_red, root=root, frames=mic_active_gif)
mic_red.place_forget()

''' Привязка событий к виджетам'''
#Используем lambda чтобы задать анонимную функцию с целью передать аргумент (сложно, забуду, поэтому ссылка)
#https://stackoverflow.com/questions/41336379/how-to-pass-parameters-from-mouse-event-to-a-function
add_bubble.bind('<Button-1>', lambda bubble : add_message_bubble('left', 'Сообщение слева!'))
#add_bubble.bind('<Button-2>', lambda quit: root.quit())
add_bubble.bind('<Button-3>', lambda bubble : add_message_bubble('right', 'Сообщение справа!'))
c.tag_bind(mic_object, "<Enter>", lambda change_cursor: root.config(cursor='hand2'))
c.tag_bind(mic_object, "<Leave>", lambda change_cursor: root.config(cursor='arrow'))
c.tag_bind(mic_object, "<Button-1>", lambda event : mic_clickEvent(event, 'begin'))
c.tag_bind(burger, "<Enter>", lambda change_cursor: root.config(cursor='hand2'))
c.tag_bind(burger, "<Leave>", lambda change_cursor: root.config(cursor='arrow'))
c.tag_bind(burger, "<Button-1>", lambda event : menu_show(event))
mic_red.bind('<Button-1>', lambda event : mic_clickEvent(event, 'end_recording'))
c.pack()
root.protocol("WM_DELETE_WINDOW", Exit)
q = Queue()
lock = Lock()
p = Process(target=CheckProc, args=(stage, ))
p.start()
root.mainloop()
