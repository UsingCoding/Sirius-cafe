from PIL import Image, ImageTk
from datetime import datetime
import asyncio
import speech_recognition as sr

# Конвертируем картинку для использования в tkinter
def convert_im_for_tk(path, resize_tuple=None):
    im = Image.open(path).convert('RGBA')
    if resize_tuple is not None: # Если дан параметр resize_tuple, ресайзим
        im = im.resize(resize_tuple, resample=Image.LANCZOS)
    im_tk = ImageTk.PhotoImage(im)
    return im_tk

# Бесконечно проигрывать gif. frames - кадры gif
def update_frames(ind, label, root, frames):
    frame = frames[(ind % 10) + 1]
    ind += 1
    label.configure(image=frame)
    root.after(100, update_frames, ind, label, root, frames)

# Через каждые 33 символа вставляем перенос строки.
def split_text(text, limit):
    t = text
    t = list(t)
    if len(t) > limit:
        linebreaks = len(t) // limit
        for i in range(1, linebreaks+1):
            for j in range(i*limit, 0, -1):
                if t[j] == ' ':
                    t[j] = '\n'
                    break
    return ''.join(t)

# Получить текущее время в формате "ЧЧ:ММ"
def get_current_time():
    hours = datetime.now().hour
    minutes = datetime.now().minute
    if minutes < 10:
        minutes = '0'+str(minutes)
    return str(hours)+':'+str(minutes)

# Записать внеземные звуки из микрофона
def record_mic():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        #r.adjust_for_ambient_noise(source)
        raw = r.listen(source)
        return raw
