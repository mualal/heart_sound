from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd, Tk, Label, Button, Scrollbar, Listbox, Entry
import numpy as np
from scipy.io.wavfile import read
from db_struct import Database
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Slider
import pygame as pg
from stingray import lightcurve
from stingray.bispectrum import Bispectrum
from detecta import detect_peaks
from scipy.signal import butter, lfilter
from scipy.spatial.distance import pdist, squareform
import itertools
import subprocess
import threading
from mpl_toolkits.axes_grid1 import make_axes_locatable

db = Database('heart_rhythms.db')


def listen_thread():
    while pg.mixer.music.get_busy():
        continue
    else:
        listen_btn.config(text='Слушать')


def recurrence_data(signal, scale=30, cutoff=15):
    dist = pdist(signal[:, None])
    dist = np.floor(dist * scale)
    dist[dist > cutoff] = cutoff
    m = squareform(dist)
    return np.rot90(m)


def heart_rate():
    sample_rate, data = rhythm_preprocess()
    data = butter_bandpass_filter(data, 30, 60, sample_rate, order=6)
    data = data / max(abs(data))
    data_split = int(sample_rate * 2)
    data_split_lst = [data[x:x+data_split] for x in range(0, len(data), data_split)]
    data_split_arr = np.array([np.array(xi) for xi in data_split_lst])
    for i in range(0, len(data_split_arr)):
        data_split_arr[i] = data_split_arr[i]/max(abs(data_split_arr[i]))
    data = list(itertools.chain(*data_split_arr))
    #plt.plot(data)
    #plt.show()
    splited_size = int(sample_rate * 0.02)
    data_splited = [data[x:x+splited_size] for x in range(0, len(data), splited_size)]
    data_np_splited = np.array([np.array(xi) for xi in data_splited])
    for j in range(0, len(data_np_splited)):
        for k in range(0, len(data_np_splited[j])):
            if data_np_splited[j][k] == 0:
                data_np_splited[j][k] = 0.0001
    shannon_energy = np.array([-np.sum(i**2*np.log(i**2))/len(i) for i in data_np_splited])
    shannon_energy_norm = (shannon_energy - np.mean(shannon_energy))/np.std(shannon_energy)
    #shannon_energy_norm = shannon_energy / max(shannon_energy)
    print(np.mean(shannon_energy))
    ind = detect_peaks(shannon_energy_norm, mph=np.mean(shannon_energy), mpd=5, show=False)
    heart_rate = 0.5 * 60 / (np.mean((ind[1:] - ind[:len(ind) - 1]) * 0.02))
    pulse_label.config(text='ЧСС ~' + str(int(heart_rate)) + ' уд./мин')
    #plt.plot(shannon_energy_norm)
    #plt.show()
    #plt.specgram(data, NFFT=256, Fs=sample_rate)
    #plt.show()


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = fs / 2
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


def rhythm_preprocess():
    path_to_file = db.fetch()[selected_index][2]
    sample_rate, data = read(path_to_file)
    # проверка моно или стерео сигнал; если стерео, то оставляю информацию только по одному каналу
    if isinstance(data[1], np.ndarray):
        data = data[:, 0]
    path_label.config(text=path_to_file)
    data = data[0:len(data):int(sample_rate / 2000)]
    sample_rate = int(sample_rate / int(sample_rate / 2000))
    data = data / max(abs(data))

    if filter_var.get() and upp_freq_value.get().isdigit() and low_freq_value.get().isdigit()\
            and int(low_freq_value.get()) < int(upp_freq_value.get()):
        data = butter_bandpass_filter(data, int(low_freq_value.get()), int(upp_freq_value.get()), sample_rate, order=6)
        data = data / max(abs(data))
    else:
        low_freq_value.set(0+1)
        upp_freq_value.set(int(sample_rate/2)-1)
    return sample_rate, data


def populate_list():
    rhythms_list.delete(0, END)
    for row in db.fetch():
        print(row)
        rhythms_list.insert(END, row[1])


def add_item(path):
    if rhythm_text.get() == '':
        messagebox.showerror('Поле не заполнено', 'Введите имя')
        return
    db.insert(rhythm_text.get(), path)
    rhythms_list.delete(0, END)
    rhythms_list.insert(END, (rhythm_text.get()))
    clear_text()
    populate_list()


def select_item(event):
    try:
        print(filter_var.get())
        print('Hello')
        global selected_item
        global selected_index
        selected_index = rhythms_list.curselection()[0]
        selected_item = rhythms_list.get(selected_index)
        rhythm_entry.delete(0, END)
        rhythm_entry.insert(END, selected_item)

        sample_rate, data = rhythm_preprocess()
        print(len(data))
        duration = len(data) / sample_rate
        #data1 = -data**2*np.log(data**2)
        #ind = detect_peaks(data, mph=0.5, mpd=0.3*sample_rate, show=False)
        time = np.arange(0, duration, 1 / sample_rate)
        #figure1.clear()
        #ax1 = figure1.add_subplot()
        ax.clear()
        ax.plot(time[0:len(data)], data[0:len(data)], linewidth=0.5, color='black')
        ax.yaxis.set_major_formatter(formatter)
        trans_factor.valmax = duration - 1
        trans_factor.ax.set_xlim(trans_factor.valmin, trans_factor.valmax)
        ax.grid(which='major', linewidth=0.3)
        ax.grid(which='minor', linewidth=0.1)
        ax.minorticks_on()
        ax.set_xlabel('Время (с)')
        ax.set_ylabel('Амплитуда')
        ax.set_title(selected_item)

        def update(val):
            current_trans = trans_factor.val
            ax.set_xlim(current_trans, current_trans + 1)
            figure1.canvas.draw_idle()

        trans_factor.on_changed(update)

        canvas.draw()
        heart_rate()

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
    if '.m4a' in file_name.name:
        new_file_name = file_name.name[:len(file_name.name)-4]+'.wav'
        subprocess.call(['ffmpeg', '-i', file_name.name, new_file_name])
        add_item(new_file_name)


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
        t = threading.Thread(target=listen_thread)
        t.start()


def rqa_window(event):
    sample_rate, data = rhythm_preprocess()

    if ax.get_xlim()[1] - ax.get_xlim()[0] < 2:
        low_value = int(ax.get_xlim()[0]*sample_rate)
        upp_value = int(ax.get_xlim()[1]*sample_rate)
    else:
        low_value = int(len(data) / 2 - 0.75 * sample_rate)
        upp_value = int(len(data) / 2 + 0.75 * sample_rate)

    fig, ax3 = plt.subplots(figsize=(7, 6))
    rqa_matrix = recurrence_data(data[low_value:upp_value])
    img = ax3.imshow(rqa_matrix, extent=np.array([low_value, upp_value, low_value, upp_value]) / sample_rate)
    divider = make_axes_locatable(ax3)
    cax = divider.append_axes("right",size="5%", pad=0.05)
    fig.colorbar(img, cax=cax)
    ax3.set_xlabel('Время, с')
    ax3.set_ylabel('Время, с')
    ax3.set_title('Анализ повторяемости')
    plt.subplots_adjust(left=0.25, bottom=0.25)
    ax_scale = plt.axes([0.25, 0.1, 0.65, 0.03])
    ax_cutoff = plt.axes([0.1, 0.25, 0.0225, 0.63])
    scale_factor = Slider(ax_scale, 'Масштаб', 1, 100, valinit=30)
    cutoff_factor = Slider(ax_cutoff, 'Отсечка', 1, 100, valinit=15, orientation='vertical')

    def update(val):
        current_scale = scale_factor.val
        current_cutoff = cutoff_factor.val
        rqa_matrix1 = recurrence_data(data[low_value:upp_value], scale=current_scale, cutoff=current_cutoff)
        ax3.imshow(rqa_matrix1, extent=np.array([low_value, upp_value, low_value, upp_value]) / sample_rate)
        fig.canvas.draw_idle()

    scale_factor.on_changed(update)
    cutoff_factor.on_changed(update)
    plt.show()


def fft_window(event):
    """
    Быстрое преобразование Фурье для выбранного интервала фонокардиограммы
    :param event:
    :return: возвращает True, если выполнилась успешно
    """
    sample_rate, data = rhythm_preprocess()
    # duration = len(data) / sample_rate
    low_value = int(ax.get_xlim()[0] * sample_rate)
    upp_value = int(ax.get_xlim()[1] * sample_rate)
    data = data[low_value:upp_value]
    fft_spectrum = np.fft.rfft(data)
    freq = np.fft.rfftfreq(len(data), d=1./sample_rate)
    fft_spectrum_abs = np.abs(fft_spectrum)

    plt.plot(freq[freq < 400], fft_spectrum_abs[freq < 400], linewidth=0.5, color='black')
    ax3 = plt.gca()
    ax3.yaxis.set_major_formatter(formatter)
    plt.grid(linewidth=0.3)
    plt.xlabel('Частота (Гц)')
    plt.ylabel('Мощность')
    plt.title(selected_item + ' (быстрое преобразование Фурье)')
    plt.show()

    return True


def bsp_window(event):
    """
    Биспектр-изображение выбранного интервала фонокардиограммы
    :param event:
    :return: возвращает True, если выполнилась успешно
    """
    sample_rate, data = rhythm_preprocess()
    duration = len(data) / sample_rate
    time = np.arange(0, duration, 1 / sample_rate)

    if ax.get_xlim()[1] - ax.get_xlim()[0] < 3:
        low_value = int(ax.get_xlim()[0]*sample_rate)
        upp_value = int(ax.get_xlim()[1]*sample_rate)
    else:
        low_value = int(len(data) / 2 - 1.5 * sample_rate)
        upp_value = int(len(data) / 2 + 1.5 * sample_rate)

    times = time[low_value:upp_value:2]
    counts = data[low_value:upp_value:2]
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

    return True


root = Tk()
root.title('Звук Сердца')
root.resizable(width=False, height=False)
root.geometry('930x640')

formatter = ticker.ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((-1, 1))

# Место для графика
figure1 = plt.Figure(figsize=(6, 5.5), dpi=100)
canvas = FigureCanvasTkAgg(figure1, root)
rhythm_graph = canvas.get_tk_widget()
rhythm_graph.place(x=5, y=0)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.place(x=5, y=0)
toolbar.update()
ax = figure1.subplots()
figure1.subplots_adjust(bottom=0.25)
ax_trans = figure1.add_axes([0.159, 0.1, 0.711, 0.03])
ax.set_xlim(1, 2)
trans_factor = Slider(ax_trans, 'Время\n начала', 0, 30, valinit=1)
figure1.canvas.draw_idle()

filter_var = IntVar()

filter_button = Checkbutton(root, text='Применить фильтр', variable=filter_var, onvalue=1, offvalue=0)
filter_button.place(x=630, y=190)

low_freq_text = StringVar()
low_freq_label = Label(root, text='Наименьшая частота, Гц', font=('bold', 12), pady=20)
low_freq_label.place(x=630, y=210)

upp_freq_text = StringVar()
upp_freq_label = Label(root, text='Наибольшая частота, Гц', font=('bold', 12), pady=20)
upp_freq_label.place(x=630, y=250)

rhythm_text = StringVar()
low_freq_value = StringVar()
upp_freq_value = StringVar()

instr_label = Label(root, text='Добавить ритм', font=('bold', 14), pady=20)
instr_label.place(x=630, y=325)

rhythm_label = Label(root, text='Имя', font=('bold', 14), pady=20)
rhythm_label.place(x=630, y=370)
rhythm_entry = Entry(root, textvariable=rhythm_text)
rhythm_entry.place(x=700, y=390)

low_freq_entry = Entry(root, textvariable=low_freq_value, width=7)
low_freq_entry.place(x=825, y=230)

upp_freq_entry = Entry(root, textvariable=upp_freq_value, width=7)
upp_freq_entry.place(x=825, y=270)

# Список ранее загруженных ритмов
rhythms_list = Listbox(root, height=8, width=30, border=0)
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
add_btn.place(x=700, y=425)

add_btn = Button(root, text='Удалить из списка', width=16, command=remove_item)
add_btn.place(x=700, y=470)

pulse_label = Label(root, text='Пульс', font=('bold', 14), pady=20)
pulse_label.place(x=20, y=555)

path_label = Label(root, text='Путь к файлу', font=('bold', 12), pady=20)
path_label.place(x=20, y=600)

arythmy_label = Label(root, text='', font=('bold', 14), pady=20)
arythmy_label.place(x=180, y=560)

listen_btn = Button(root, text='Слушать', width=12)
listen_btn.bind('<Button-1>', listen_rhythm)
listen_btn.place(x=400, y=560)

fft_btn = Button(root, text='Фурье', width=12)
fft_btn.bind('<Button-1>', fft_window)
fft_btn.place(x=520, y=560)

recurrence_btn = Button(root, text='Повторяемость', width=12)
recurrence_btn.bind('<Button-1>', rqa_window)
recurrence_btn.place(x=640, y=560)

bsp_btn = Button(root, text='Биспектр', width=12)
bsp_btn.bind('<Button-1>', bsp_window)
bsp_btn.place(x=760, y=560)

populate_list()

root.mainloop()
