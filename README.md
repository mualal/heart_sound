Heart Sound: приложение для визуализации, воспроизведения и классификации сердечных ритмов, записанных на диктофон (фонокардиограмм)

![Графический интерфейс](https://github.com/mualal/heart_sound/blob/master/img/Screenshot%202021-12-19%20at%2018.52.52.png)

Видео: https://www.youtube.com/watch?v=MUUdEyRFFeM

При первом открытии exe файла необходимо ввести имя в соответствующее поле и выбрать запись с ФКГ (например, rhythm3.wav из файлов проекта). При повторных запусках приложения ранее просмотренные файлы будут подгружаться автоматически.


Дополнительные возможности приложения:

1) пульсометр

Для более точного определения частоты сердечных сокращений необходимо прикладывать микрофон вблизи области трикуспидального клапана.

2) быстрое преобразование Фурье для выбранного интервала фонокардиограммы

![Фурье](https://github.com/mualal/heart_sound/blob/master/img/Screenshot%202021-12-19%20at%2018.08.23.png)

3) полосовой фильтр Баттерворта для отсечки высокочастотных и низкочастотных помех

![Баттерворт](https://github.com/mualal/heart_sound/blob/master/img/Screenshot%202021-12-19%20at%2018.35.21.png)

4) визуализация биспектра для выбранного интервала фонокардиограммы

![Биспектр](https://github.com/mualal/heart_sound/blob/master/img/Screenshot%202021-12-19%20at%2018.40.38.png)

5) анализ повторяемости значений в выбранном интервале фонокардиограммы

![RQA](https://github.com/mualal/heart_sound/blob/master/img/Screenshot%202021-12-19%20at%2018.24.36.png)

Функция автоматического распознавания ритмов с отклонениями от нормы находится в разработке (текущий прогресс в ipynb файлах).

План дальнейшей доработки:
1) реорганизовать код с использованием подхода объектно-ориентированного программирования (ООП), чтобы в дальнейшем импортировать функции приложения (например, определение частоты сердечных сокращений) в Jupyter-тетрадь PCG_datasets_exploration.ipynb для исследования наборов данных ФКГ (например, построения распределения ЧСС на ФКГ из выбранного датасета);
2) реализовать алгоритм сегментации ФКГ (автоматического определения диапазонов времени с первым и вторым тонами сердца);
3) в дополнение проводить анализ шумов от лёгких (алгоритмы для отделения тонов сердца и шумов от лёгких, основанные на различном положении их аттракторов в пространстве состояний); по шумам лёгких определять наличие или отсутствие респираторного заболевания;
4) по проделанному (в автоматическом режиме) анализу тонов сердца и шумов лёгких генерировать подробный pdf отчёт с Фурье-анализом каждого тона сердца;
5) использовать степень коррелированности в алгоритмах;
6) визуализировать 3Д-проекцию траекторий в пространстве состояний;
7) в дополнение к уже сделанному GUI на основе tkinter реализовать GUI на основе PyQt, а также сделать Web-приложение (например, на основе Django) и приложения для смартфона (например, на основе Swift и Kotlin) с аналогичным функционалом;
8) доработать возможность импорта аудио-файлов любого расширения (не только wav файлы);
9) создать телеграмм-бота: пользователь отправляет аудио-файл и получает pdf отчёт с проанализированной ФКГ;
10) в идеале создать собственный прототип интеллектуального стетоскопа. Анализ ФКГ+ЭКГ+дыхание
