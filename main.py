import requests
import json
from geopy.geocoders import Nominatim
import tkinter as tk
from tkinter import messagebox
from time import strptime
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk

# apikey = YOUR API KEY


# TODO pack everything into a class
# class Display(tk.Tk()):
#     def __init__(self):
#


def get_measurements(lat, long):
    response = requests.get(
        'https://airapi.airly.eu/v2/measurements/point?lat={}&lng={}'.format(lat, long),
        headers={'Accept': 'application/json', 'apikey': '{}'.format(apikey)})

    if response.status_code != 200:
        print(response.status_code, ' ', response.text)
        exit(1)

    json_response = response.json()
    return json_response


def load_installations():
    response = requests.get(
        'https://airapi.airly.eu/v2/installations/nearest?lat=52&lng=19&maxDistanceKM=-1&maxResults=-1',
        headers={'Accept': 'application/json', 'apikey': '{}'.format(apikey)})

    if response.status_code != 200:
        print(response.status_code, ' ', response.text)
        exit(1)

    json_response = response.json()
    with open('installations.json', 'w', encoding='utf8') as outfile:
        json.dump(json_response, outfile, ensure_ascii=False)


def reset_window():
    global displayed_plot, data_labels
    if displayed_plot is not None:
        displayed_plot.destroy()
    if data_labels:
        for l in data_labels:
            l.destroy()


def on_find_click():
    global measurements, bottom_buttons
    if not city_entry.get():
        messagebox.showinfo('City left empty', 'City name is required')
        return
    location = geolocator.geocode(city_entry.get() + ' ' + street_entry.get() + ' ' + number_entry.get())
    if location is None:
        messagebox.showinfo('No such address', 'This address does not exists')
        return
    measurements = get_measurements(location.latitude, location.longitude)
    for button in bottom_buttons:
        button.config(state='normal')
    on_current_click()


def plot_24h(option):
    global measurements, displayed_plot
    reset_window()
    if measurements is None:
        messagebox.showinfo('No address found', 'Find the address first')
        return
    history = measurements[option]
    hrs = [strptime(measurement['fromDateTime'], '%Y-%m-%dT%H:%M:%SZ').tm_hour for measurement in history]
    mins = [strptime(measurement['fromDateTime'], '%Y-%m-%dT%H:%M:%SZ').tm_min for measurement in history]
    hours = ['{}:{}0'.format(hrs[i], mins[i]) for i in range(0, 24)]
    if option == 'history':
        i = (1, 2,)
    else:
        i = (0, 1,)
    pm25_val = [measurement['values'][i[0]]['value'] for measurement in history]
    pm10_val = [measurement['values'][i[1]]['value'] for measurement in history]
    pm25_std = [measurement['standards'][0]['percent'] for measurement in history]
    pm10_std = [measurement['standards'][1]['percent'] for measurement in history]
    f, ax1 = plt.subplots()
    x = np.arange(24)
    plt.xticks(x, hours, rotation=80)
    plt.xlabel('time')
    ax2 = ax1.twinx()
    ax2.grid(True)
    show_pm10 = True
    if show_pm10:
        ax1.plot(x, pm10_val)
        ax2.plot(x, pm10_std)
        ax1.set_ylabel('PM10 [μg/m³]')
        ax2.set_ylabel('PM10 [%]')
    else:
        ax1.plot(x, pm25_val)
        ax2.plot(x, pm25_std)
        ax1.set_ylabel('PM2.5 [μg/m³]')
        ax2.set_ylabel('PM2.5 [%]')
    plt.savefig('plot.png')
    img = ImageTk.PhotoImage(Image.open('plot.png'))
    displayed_plot = tk.Label(window, image=img)
    displayed_plot.image = img
    displayed_plot.place(x=10, y=160)


def on_history_click():
    plot_24h('history')


def on_forecast_click():
    plot_24h('forecast')


def on_current_click():
    global measurements, data_labels
    reset_window()
    if measurements is None:
        messagebox.showinfo('No address found', 'Find the address first')
        return
    curr = measurements['current']
    values = curr['values']
    values[1]['name'] = 'PM2.5'
    standards = curr['standards']
    index = curr['indexes'][0]
    canvas = tk.Canvas(window, width=120, height=120)
    canvas.place(x=890, y=10)
    canvas.create_oval(5, 5, 115, 115, fill=index['color'])
    if index['value'] is None:
        messagebox.showinfo('Can\'t get measurements', 'There is no installation near given address')
        return
    pm25 = tk.Label(window, text=values[1]['name'] + ': ' + str(values[1]['value']) + ' μg/m³' + '   ' + str(
        standards[0]['percent']) + '%', font=("Courier", 18))
    pm10 = tk.Label(window, text=values[2]['name'] + ': ' + str(values[2]['value']) + ' μg/m³' + '   ' + str(
        standards[1]['percent']) + '%', font=("Courier", 18))
    pressure = tk.Label(window, text=values[3]['name'] + ': ' + str(values[3]['value']) + ' hPa', font=("Courier", 18))
    humidity = tk.Label(window, text=values[4]['name'] + ': ' + str(values[4]['value']) + '%', font=("Courier", 18))
    temperature = tk.Label(window, text=values[5]['name'] + ': ' + str(values[5]['value']) + '°C', font=("Courier", 18))
    caqi = tk.Label(window, text=index['name'] + ': ' + str(index['value']) + '   ' + index['level'] + '\n' +
                                 index['description'] + ' ' + index['advice'], font=("Courier", 18), anchor='w',
                    wraplength=1000)
    data_labels = [pm25, pm10, pressure, humidity, temperature, caqi]
    space = 0
    for element in data_labels:
        element.place(x=10, y=160 + space)
        space += 40


if __name__ == '__main__':
    with open('installations.json') as infile:
        installations = json.load(infile)

    geolocator = Nominatim(user_agent='__main__')

    window = tk.Tk()
    window.winfo_toplevel().resizable(False, False)
    window.winfo_toplevel().title('Airly client')
    window.geometry('1024x768')
    city_label = tk.Label(window, text='City*')
    city_label.place(x=10, y=10)
    street_label = tk.Label(window, text='Street')
    street_label.place(x=10, y=35)
    number_label = tk.Label(window, text='Number')
    number_label.place(x=10, y=60)
    tk.Label(window, text='* - required').place(x=10, y=85)
    city_entry = tk.Entry(window, width=20)
    city_entry.place(x=70, y=10)
    street_entry = tk.Entry(window, width=20)
    street_entry.place(x=70, y=35)
    number_entry = tk.Entry(window, width=10)
    number_entry.place(x=70, y=60)
    find_button = tk.Button(window, text='Find', width=8, command=on_find_click)
    find_button.place(x=30, y=105)
    history_button = tk.Button(window, text='History', width=8, command=on_history_click, state='disabled')
    current_button = tk.Button(window, text='Current', width=8, command=on_current_click, state='disabled')
    forecast_button = tk.Button(window, text='Forecast', width=8, command=on_forecast_click, state='disabled')
    history_button.place(x=10, y=730)
    current_button.place(x=120, y=730)
    forecast_button.place(x=230, y=730)
    bottom_buttons = [history_button, current_button, forecast_button]
    measurements = None
    data_labels = None
    displayed_plot = None
    window.mainloop()
