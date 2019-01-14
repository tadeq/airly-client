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


class Window(tk.Tk):
    def reset_window(self):
        if self.displayed_plot is not None:
            self.displayed_plot.destroy()
        if self.data_labels:
            for l in self.data_labels:
                l.destroy()

    def on_find_click(self):
        if not self.city_entry.get():
            messagebox.showinfo('City left empty', 'City name is required')
            return
        location = geolocator.geocode(
            self.city_entry.get() + ' ' + self.street_entry.get() + ' ' + self.number_entry.get())
        if location is None:
            messagebox.showinfo('No such address', 'This address does not exists')
            return
        self.measurements = get_measurements(location.latitude, location.longitude)
        for button in self.bottom_buttons:
            button.config(state='normal')
        self.on_current_click()

    def plot_24h(self, option):
        self.reset_window()
        if self.measurements is None:
            messagebox.showinfo('No address found', 'Find the address first')
            return
        period = self.measurements[option]
        hrs = [strptime(measurement['fromDateTime'], '%Y-%m-%dT%H:%M:%SZ').tm_hour for measurement in period]
        mins = [strptime(measurement['fromDateTime'], '%Y-%m-%dT%H:%M:%SZ').tm_min for measurement in period]
        hours = ['{}:{}0'.format(hrs[i], mins[i]) for i in range(0, 24)]
        if option == 'history':
            i = (1, 2,)
        else:
            i = (0, 1,)
        pm25_val = [measurement['values'][i[0]]['value'] for measurement in period]
        pm10_val = [measurement['values'][i[1]]['value'] for measurement in period]
        pm25_std = [measurement['standards'][0]['percent'] for measurement in period]
        pm10_std = [measurement['standards'][1]['percent'] for measurement in period]
        plt.figure(figsize=(13, 5))
        ax1 = plt.subplot(1, 2, 1)
        x = np.arange(24)
        plt.xticks(x, hours, rotation=80)
        plt.xlabel('time')
        ax1.set_title(option)
        ax2 = ax1.twinx()
        ax2.grid(True)
        ax1.plot(x, pm25_val)
        ax2.plot(x, pm25_std)
        ax1.set_ylabel('PM2.5 [μg/m³]')
        ax2.set_ylabel('PM2.5 [%]')
        ax3 = plt.subplot(1, 2, 2)
        ax3.set_title(option)
        plt.xticks(x, hours, rotation=80)
        plt.xlabel('time')
        ax4 = ax3.twinx()
        ax4.grid(True)
        ax3.plot(x, pm10_val)
        ax4.plot(x, pm10_std)
        ax3.set_ylabel('PM10 [μg/m³]')
        ax4.set_ylabel('PM10 [%]')
        plt.tight_layout()
        plt.savefig('plot.png')
        img = ImageTk.PhotoImage(Image.open('plot.png'))
        self.displayed_plot = tk.Label(image=img)
        self.displayed_plot.image = img
        self.displayed_plot.place(x=10, y=160)

    def on_history_click(self):
        self.plot_24h('history')

    def on_forecast_click(self):
        self.plot_24h('forecast')

    def on_current_click(self):
        self.reset_window()
        if self.measurements is None:
            messagebox.showinfo('No address found', 'Find the address first')
            return
        curr = self.measurements['current']
        index = curr['indexes'][0]
        canvas = tk.Canvas(width=120, height=120)
        canvas.place(x=1230, y=10)
        canvas.create_oval(5, 5, 115, 115, fill=index['color'])
        if index['value'] is None:
            messagebox.showinfo('Can\'t get measurements', 'There is no installation near given address')
            return
        values = curr['values']
        values[1]['name'] = 'PM2.5'
        standards = curr['standards']
        pm25 = tk.Label(text='{}: {} μg/m³   {} %'.format(values[1]['name'], str(values[1]['value']), str(
            standards[0]['percent'])), font=("Courier", 18))
        pm10 = tk.Label(text='{}: {} μg/m³   {} %'.format(values[2]['name'], str(values[2]['value']), str(
            standards[1]['percent'])), font=("Courier", 18))
        pressure = tk.Label(text='{}: {} hPa'.format(values[3]['name'], str(values[3]['value'])),
                            font=("Courier", 18))
        humidity = tk.Label(text='{}: {} %'.format(values[4]['name'], str(values[4]['value'])),
                            font=("Courier", 18))
        temperature = tk.Label(text='{}: {} °C'.format(values[5]['name'], str(values[5]['value'])),
                               font=("Courier", 18))
        caqi = tk.Label(text='{}: {}   {}\n{} {}'.format(index['name'], str(index['value']), index['level'],
                                                         index['description'], index['advice']),
                        font=("Courier", 18), anchor='w', wraplength=1000)
        self.data_labels = [pm25, pm10, pressure, humidity, temperature, caqi]
        space = 0
        for element in self.data_labels:
            element.place(x=10, y=160 + space)
            space += 40

    def __init__(self):
        super().__init__()
        self.winfo_toplevel().resizable(False, False)
        self.winfo_toplevel().title('Airly client')
        self.geometry('1366x768')
        tk.Label(text='City*').place(x=10, y=10)
        tk.Label(text='Street').place(x=10, y=35)
        tk.Label(text='Number').place(x=10, y=60)
        tk.Label(text='* - required').place(x=10, y=85)
        self.city_entry = tk.Entry(width=20)
        self.city_entry.place(x=70, y=10)
        self.street_entry = tk.Entry(width=20)
        self.street_entry.place(x=70, y=35)
        self.number_entry = tk.Entry(width=10)
        self.number_entry.place(x=70, y=60)
        self.find_button = tk.Button(text='Find', width=8, command=self.on_find_click)
        self.find_button.place(x=30, y=105)
        history_button = tk.Button(text='History', width=8, command=self.on_history_click, state='disabled')
        current_button = tk.Button(text='Current', width=8, command=self.on_current_click, state='disabled')
        forecast_button = tk.Button(text='Forecast', width=8, command=self.on_forecast_click, state='disabled')
        self.bottom_buttons = [history_button, current_button, forecast_button]
        space = 0
        for button in self.bottom_buttons:
            button.place(x=10 + space, y=730)
            space += 110
        self.measurements = None
        self.data_labels = None
        self.displayed_plot = None


def get_measurements(lat, long):
    response = requests.get(
        'https://airapi.airly.eu/v2/measurements/point?lat={}&lng={}'.format(lat, long),
        headers={'Accept': 'application/json', 'apikey': '{}'.format(apikey)})

    if response.status_code != 200:
        print('{} {}'.format(response.status_code, response.text))
        exit(1)

    json_response = response.json()
    return json_response


def load_installations():
    response = requests.get(
        'https://airapi.airly.eu/v2/installations/nearest?lat=52&lng=19&maxDistanceKM=-1&maxResults=-1',
        headers={'Accept': 'application/json', 'apikey': '{}'.format(apikey)})

    if response.status_code != 200:
        print('{} {}'.format(response.status_code, response.text))
        exit(1)

    json_response = response.json()
    with open('installations.json', 'w', encoding='utf8') as outfile:
        json.dump(json_response, outfile, ensure_ascii=False)


if __name__ == '__main__':
    geolocator = Nominatim(user_agent='__main__')
    window = Window()
    window.protocol("WM_DELETE_WINDOW", lambda: quit())
    window.mainloop()
