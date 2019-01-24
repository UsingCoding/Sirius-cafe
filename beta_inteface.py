from tkinter import *
from misc.utils import *
#from multiprocessing.pool import ThreadPool
import speech_recognition as sr
#from logic.logic import *
from multiprocessing.dummy import Process, Queue
#from Stt_and_tts import *
import time

class Statement:
    def __init__(self, dict):
        self.confidence = dict['confidence']
        self.text = dict['transcript'].lower()

    def __repr__(self):
        return "[{}] {}".format(self.confidence, self.text)

    def __str__(self):
        return self.text

    def __gt__(self, other):
        return self.confidence > other.confidence


class Speech_AI:
    def __init__(self, google_treshold = 0.5, chatterbot_treshold = 0.45):
        self._recognizer = sr.Recognizer()
        self._microphone = sr.Microphone()

        self.google_treshold = google_treshold

        self._mp3_name = "speech.mp3"
        self.be_quiet = False


    def work(self, q, mic_red):
        print('Минутку тишины, пожалуйста...')
        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source)

        #while True:
        print('Скажи что - нибудь!')
        mic_red.place(x=380, y=506, anchor='nw')
        with self._microphone as source:
            audio = self._recognizer.listen(source)
        print("Понял, идет распознавание...")
        statements = self.recognize(audio) # Можно заменить на файл
        print('Выражения ', statements)
        best_statement = self.choose_best_statement(statements)
        print('Вы сказали: ', best_statement)
        kort = (best_statement)
        q.put(kort)
        mic_red.place_forget()
        if not self.be_quiet:
            pass
        print()

    def recognize(self, audio):
        statements = []
        try:
            json = self._recognizer.recognize_google(audio, language="ru_RU", show_all=True)
            statements = self.json_to_statements(json)
        except sr.UnknownValueError:
            print("[GoogleSR] Неизвестное выражение")
        except sr.RequestError as e:
            print("[GoogleSR] Не могу получить данные; {0}".format(e))
        return statements

    def json_to_statements(self, json):
        statements = []
        if len(json) is not 0:
            for dict in json['alternative']:
                if 'confidence' not in dict:
                    dict['confidence'] = self.google_treshold + 0.1
                statements.append(Statement(dict))
        return statements

    def choose_best_statement(self, statements):
        if statements:
            return max(statements, key=lambda s: s.confidence)
        else:
            return None

    def say(self, phrase):
        # Synthesize answer
        # todo check exceptons there
        print("[GoogleTTS] Начало запроса")
        try:
            tts = gTTS(text=phrase, lang="ru")
            tts.save(self._mp3_name)
        except Exception as e:
            print("[GoogleTTS] Не удалось синтезировать речь: {}".format(e.strerror))
            return
        # Play answer
        mixer.music.load(self._mp3_name)
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.1)

    def check_in_string(self, string, words):
        if any(word in string for word in words):
            return True
        return False

    def clean_up(self):
        os.remove(self._mp3_name)



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
def CheckProc():
    while True:
        time.sleep(0.5)
        print('Checking')
        #if q.empty is False:
        #break
        conv = str(q.get())
        print(conv + ' Print conv')
        if conv == "False":
            break
        else:
            add_message_bubble('right')
            state = logic.main(conv)
            #send to tts message
            time.sleep(0.1)
            print(state)
            add_message_bubble('left')

def Exit():
    root.destroy()
    q.put('False')


# По нажатию на микрофон, создаем красный микрофон и анимацию, а так же включаем
def mic_clickEvent(event, button_stage):
    if button_stage == 'begin':
        #mic_red.place(x=380, y=506, anchor='nw')
        #mic_red.place_forget()
        A =Speech_AI()
        proc = Process(target=A.work, args=(q, mic_red))
        proc.start()
        # Записать микрофон в отдельном процессе : raw_audio = pool.apply_async(record_mic)
        # Сохранить записанное : udio.insert(0, raw_audio)
    elif button_stage == 'end_recording':
        for element in menu:
            c.delete(element)
        print(event.widget)
        event.widget.place_forget()
        # r = sr.Recognizer()
        # Распознанный текст в переменную : recognized_text = r.recognize_google(audio[0].get(), language='ru-RU')
        # add_message_bubble('right', recognized_text)
        # Ответ
        #stages.insert(0, current_stage(recognized_text, stages[0]))
        #answer = message_handler(stages[0])
        #add_message_bubble('left', answer)

def menu_show(event):
    for element in menu:
        c.delete(element)
    menu.append(c.create_image((0,0), image=menu_shadow, anchor='nw', tags='menu_shadow'))
    menu.append(c.create_image((400, 280), image=menu_banner_image, anchor='center', tags='menu_banner'))
    # first row of menu entries
    # При добавлении нового столбца меню (2, 3), по x сдвигать на 165
    menu.append(c.create_text((160, 95), text=menu_placeholder, anchor='nw', font=('Bahnschrift Light Condensed', 13), fill='#606060', tags='menu_entries'))
    c.tag_lower(c.find_withtag('menu_shadow'))
    c.tag_lower(c.find_withtag('mainbg'))

''' Добавить облачко текста. Параметры - сторона, текст сообщения '''
def add_message_bubble(side, text):
    text = split_text(text, 33)
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
p = Process(target=CheckProc)
p.start()
root.mainloop()
