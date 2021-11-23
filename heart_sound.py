from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd, Tk, Label, Button, Scrollbar, Listbox, Entry
import numpy as np
from scipy.io.wavfile import read
from db_struct import Database
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from playsound import playsound

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
        ax1.set_xlabel('Время (с)')
        ax1.set_ylabel('Амплитуда')
        ax1.set_title(selected_item)
        bar1.draw()
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
    print(selected_index)
    playsound(db.fetch()[selected_index][2])


def open_new_window(event):
    new_window = Toplevel(root)
    new_window.title('Подробный анализ')
    new_window.geometry('930x600')
    sample_rate, data = read(db.fetch()[selected_index][2])
    fft_spectrum = np.fft.rfft(data)
    freq = np.fft.rfftfreq(len(data), d=1./sample_rate)
    fft_spectrum_abs = np.abs(fft_spectrum)

    figure2 = plt.Figure(figsize=(6, 5), dpi=100)
    ax2 = figure2.add_subplot()
    ax2.plot(freq, fft_spectrum_abs, linewidth=0.5)
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Мощность')
    ax2.set_title(selected_item + ' (преобразование Фурье)')
    bar2 = FigureCanvasTkAgg(figure2, new_window)
    frequency_domain_graph = bar2.get_tk_widget()
    frequency_domain_graph.place(x=5, y=0)
    bar2.draw()


root = Tk()
root.title('Звук Сердца')
root.resizable(width=False, height=False)
root.geometry('930x600')

# Место для графика
figure1 = plt.Figure(figsize=(6, 5), dpi=100)
ax = figure1.add_subplot()
bar1 = FigureCanvasTkAgg(figure1, root)
rhythm_graph = bar1.get_tk_widget()
rhythm_graph.place(x=5, y=0)
bar1.draw()

figure1.canvas.draw_idle()

rhythm_text = StringVar()
instr_label = Label(root, text='Добавить ритм', font=('bold', 14), pady=20)
instr_label.place(x=600, y=250)

rhythm_label = Label(root, text='Имя', font=('bold', 14), pady=20)
rhythm_label.place(x=600, y=300)
rhythm_entry = Entry(root, textvariable=rhythm_text)
rhythm_entry.place(x=700, y=315)

# Список ранее загруженных ритмов
rhythms_list = Listbox(root, height=8, width=25, border=0)
rhythms_list.place(x=620, y=20)

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
add_btn.place(x=700, y=350)

add_btn = Button(root, text='Удалить из списка', width=16, command=remove_item)
add_btn.place(x=700, y=400)

pulse_label = Label(root, text='Пульс', font=('bold', 14), pady=20)
pulse_label.place(x=20, y=500)

arythmy_label = Label(root, text='Аритмия', font=('bold', 14), pady=20)
arythmy_label.place(x=120, y=500)

listen_btn = Button(root, text='Слушать', width=12)
listen_btn.bind('<Button-1>', listen_rhythm)
listen_btn.place(x=220, y=550)

listen_btn = Button(root, text='Подробнее', width=12)
listen_btn.bind('<Button-1>', open_new_window)
listen_btn.place(x=370, y=550)

populate_list()

root.mainloop()
