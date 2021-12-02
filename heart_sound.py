from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd, Tk, Label, Button, Scrollbar, Listbox, Entry
import numpy as np
from scipy.io.wavfile import read
from db_struct import Database
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pygame as pg
from stingray import lightcurve
from stingray.bispectrum import Bispectrum

db = Database('heart_rhythms.db')


def populate_list():
    rhythms_list.delete(0, END)
    for row in db.fetch():
        print(row)
        rhythms_list.insert(END, row[1])


def add_item(path):
    if rhythm_text.get() == '':
        messagebox.showerror('Required Fields', 'Please include all fields')
        return
    db.insert(rhythm_text.get(), path)
    rhythms_list.delete(0, END)
    rhythms_list.insert(END, (rhythm_text.get()))
    clear_text()
    populate_list()


def select_item(event):
    try:
        global selected_item
        global selected_index
        selected_index = rhythms_list.curselection()[0]
        selected_item = rhythms_list.get(selected_index)
        rhythm_entry.delete(0, END)
        rhythm_entry.insert(END, selected_item)

        sample_rate, data = read(db.fetch()[selected_index][2])
        print(len(data))
        duration = len(data) / sample_rate
        print(duration)
        time = np.arange(0, duration, 1 / sample_rate)
        figure1.clear()
        ax1 = figure1.add_subplot()
        ax1.plot(time[0:len(data)], data, linewidth=0.5)
        ax1.yaxis.set_major_formatter(formatter)
        ax1.grid(linewidth=0.3)
        ax1.set_xlabel('Время (с)')
        ax1.set_ylabel('Амплитуда')
        ax1.set_title(selected_item)
        canvas.draw()
        pulse_label.config(text='Пульс')

    except IndexError:
        pass


def remove_item():
    db.remove(db.fetch()[selected_index][0])
    clear_text()
    populate_list()


def choose_file(event):
    file_name = fd.askopenfile(defaultextension='.wav', title='Выберите .wav файл')
    if '.wav' in file_name.name:
        add_item(file_name.name)


def clear_text():
    rhythm_entry.delete(0, END)


def listen_rhythm(event):
    if not pg.mixer.get_init():
        pg.mixer.init()
    if pg.mixer.music.get_busy():
        pg.mixer.music.stop()
        listen_btn.config(text='Слушать')
    else:
        print(selected_index)
        pg.mixer.music.load(db.fetch()[selected_index][2])
        pg.mixer.music.play()
        listen_btn.config(text='Не слушать')


def fft_window(event):

    sample_rate, data = read(db.fetch()[selected_index][2])
    fft_spectrum = np.fft.rfft(data)
    freq = np.fft.rfftfreq(len(data), d=1./sample_rate)
    fft_spectrum_abs = np.abs(fft_spectrum)

    plt.plot(freq, fft_spectrum_abs, linewidth=0.5)
    ax3 = plt.gca()
    ax3.yaxis.set_major_formatter(formatter)
    plt.grid(linewidth=0.3)
    plt.xlabel('Частота (Гц)')
    plt.ylabel('Мощность')
    plt.title(selected_item + ' (преобразование Фурье)')
    plt.show()
    #toolbar2 = NavigationToolbar2Tk(canvas2, new_window)
    #toolbar2.place(x=5, y=0)
    #toolbar2.update()


def bsp_window(event):
    sample_rate, data = read(db.fetch()[selected_index][2])
    duration = len(data) / sample_rate
    data = data[0:len(data):int(sample_rate / 2000)]
    sample_rate = int(sample_rate / int(sample_rate / 2000))
    time = np.arange(0, duration, 1 / sample_rate)
    data = data / max(data)
    times = time[0:int(3 / duration * len(data))]
    counts = data[0:int(3 / duration * len(data))]
    times = times[0:len(times):2]
    counts = counts[0:len(counts):2]
    lc = lightcurve.Lightcurve(times, counts)

    bs = Bispectrum(lc, scale='unbiased')

    p = bs.plot_mag()
    p.title('Величина биспектра')
    p.xlabel('Частота f1, Гц')
    p.ylabel('Частота f2, Гц')
    ax3 = p.gca()
    ax3.set_ylim([-300, 300])
    ax3.set_xlim([-300, 300])
    p.show()


root = Tk()
root.title('Звук Сердца')
root.resizable(width=False, height=False)
root.geometry('930x600')

formatter = ticker.ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((-1, 1))

# Место для графика
figure1 = plt.Figure(figsize=(6, 5), dpi=100)
ax = figure1.add_subplot()
canvas = FigureCanvasTkAgg(figure1, root)
rhythm_graph = canvas.get_tk_widget()
rhythm_graph.place(x=5, y=0)
canvas.draw()

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.place(x=5, y=0)
toolbar.update()

figure1.canvas.draw_idle()

rhythm_text = StringVar()
instr_label = Label(root, text='Добавить ритм', font=('bold', 14), pady=20)
instr_label.place(x=630, y=250)

rhythm_label = Label(root, text='Имя', font=('bold', 14), pady=20)
rhythm_label.place(x=630, y=300)
rhythm_entry = Entry(root, textvariable=rhythm_text)
rhythm_entry.place(x=700, y=320)

# Список ранее загруженных ритмов
rhythms_list = Listbox(root, height=8, width=25, border=0)
rhythms_list.place(x=630, y=20)

# Полоса прокрутки
scrollbar = Scrollbar(root)
scrollbar.place(x=870, y=20)

# Связка списка ритмов и полосы прокрутки
scrollbar.pack(side='right', fill='y')
rhythms_list.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=rhythms_list.yview)


# Выбор элемента из списка ритмов
rhythms_list.bind('<<ListboxSelect>>', select_item)

# Кнопки
add_btn = Button(root, text='Выбрать файл', width=12)
add_btn.bind('<Button-1>', choose_file)
add_btn.place(x=700, y=355)

add_btn = Button(root, text='Удалить из списка', width=16, command=remove_item)
add_btn.place(x=700, y=400)

pulse_label = Label(root, text='Пульс', font=('bold', 14), pady=20)
pulse_label.place(x=20, y=530)

arythmy_label = Label(root, text='Аритмия', font=('bold', 14), pady=20)
arythmy_label.place(x=180, y=530)

listen_btn = Button(root, text='Слушать', width=12)
listen_btn.bind('<Button-1>', listen_rhythm)
listen_btn.place(x=400, y=550)

fft_btn = Button(root, text='Фурье', width=12)
fft_btn.bind('<Button-1>', fft_window)
fft_btn.place(x=520, y=550)

bsp_btn = Button(root, text='Биспектр', width=12)
bsp_btn.bind('<Button-1>', bsp_window)
bsp_btn.place(x=660, y=550)

populate_list()

root.mainloop()
