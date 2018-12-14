import requests
import json
from geopy.geocoders import Nominatim
import tkinter as tk


# apikey =


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


def on_find_click():
    location = geolocator.geocode(city_entry.get() + ' ' + street_entry.get() + ' ' + number_entry.get())
    measurements = get_measurements(location.latitude, location.longitude)
    curr = measurements['current']
    values = curr['values']
    standards = curr['standards']
    index = curr['indexes'][0]
    canvas = tk.Canvas(window, width=120, height=120)
    canvas.place(x=670, y=10)
    canvas.create_oval(5, 5, 115, 115, fill=index['color'])
    tk.Label(window, text=values[1]['name'] + ': ' + str(values[1]['value']) + ' μg/m³' + '   ' + str(
        standards[0]['percent']) + '%').place(x=10, y=140)
    tk.Label(window, text=values[2]['name'] + ': ' + str(values[2]['value']) + ' μg/m³' + '   ' + str(
        standards[1]['percent']) + '%').place(x=10, y=160)
    for i in range(3, 6):
        tk.Label(window, text=values[i]['name'] + ': ' + str(values[i]['value'])).place(x=10, y=120 + i * 20)
    print(index['name'])
    tk.Label(window,
             text=index['name'] + ': ' + str(index['value']) + '  ' + index['level'] + '\n' + index['description'] +
                  ' ' + index['advice']).place(x=10, y=240)


def on_history_click():
    location = geolocator.geocode(city_entry.get() + ' ' + street_entry.get() + ' ' + number_entry.get())
    measurements = get_measurements(location.latitude, location.longitude)
    history = measurements['history']
    pm25 = [measurement['values'][1]['value'] for measurement in history]
    print(pm25)
    pm10 = [measurement['values'][2]['value'] for measurement in history]
    print(pm10)
    return


def on_current_click():
    return


def on_forecast_click():
    return


if __name__ == '__main__':
    with open('installations.json') as infile:
        installations = json.load(infile)

    geolocator = Nominatim(user_agent='__main__')

    window = tk.Tk()
    window.winfo_toplevel().resizable(False, False)
    window.winfo_toplevel().title('Airly client')
    window.geometry('800x600')
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
    history_button = tk.Button(window, text='History', width=8, command=on_history_click)
    current_button = tk.Button(window, text='Current', width=8, command=on_current_click)
    forecast_button = tk.Button(window, text='Forecast', width=8, command=on_forecast_click)
    history_button.place(x=10, y=560)
    current_button.place(x=120, y=560)
    forecast_button.place(x=230, y=560)
    window.mainloop()
