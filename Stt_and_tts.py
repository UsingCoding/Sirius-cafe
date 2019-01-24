import speech_recognition as sr
from gtts import gTTS
import multiprocessing as mp
from multiprocessing import Queue

from pygame import mixer
mixer.init()

import os, sys, time
import logging

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


    def work(self, q, mic_red, lock):
        lock.acquire()
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
        lock.release()
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
        self.clean_up()

    def check_in_string(self, string, words):
        if any(word in string for word in words):
            return True
        return False

    def clean_up(self):
        os.remove(self._mp3_name)
