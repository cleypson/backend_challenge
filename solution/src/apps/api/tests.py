import json
from django.test import TestCase, Client
from django.db.models import Max, Min
from rest_framework import status
from .models import Car, Tyre, Trip, Order

# Create your tests here.

BASE_URL = '/api/v1'

client = Client()


class CarTestClass(TestCase):
    def setUp(self):
        self.car = Car.objects.create()
        self.car.maintenance('_fuel')
        self.car.maintenance('_tyre')
        self.trip_url = "{}/cars/{}/trip/".format(
            BASE_URL, self.car.id)
        self.maintenance_url = "{}/cars/{}/maintenance/".format(
            BASE_URL, self.car.id)
        self.car_status_url = "{}/cars/{}/get_car_status/".format(
            BASE_URL, self.car.id)
        for r in range(10):
            Tyre.objects.create()

    def tearDown(self):
        pass

    def test_ten_thousand_km(self):
        self.travel(10000.0)

    def test_one_hundred_fifty_km(self):
        self.travel(150.0)

    def test_three_hundred_fifty_km(self):
        self.travel(350)

    def test_one_thousand_km(self):
        self.travel(1000)

    def travel(self, distance):
        print('---------------------------- Travel | {} KM --'.format(distance))
        travelled = 0.0
        trip_distance = 0.0
        max_distance = distance
        self.get_car_status()
        while max_distance > 0:
            fuel_autonomy = self.get_autonomy_tank()
            tyres_autonomy = self.get_autonomy_tyres()
            trip_distance = self.get_trip_distance(
                fuel_autonomy, tyres_autonomy, max_distance)
            travelled += trip_distance
            max_distance -= trip_distance
            print('------------------ Begin-Trip | {} KM ---'.format(trip_distance))
            response = self.trip(trip_distance)
            self.trip_status(response.content)
            self.maintenance_fuel()
            self.maintenance_tyres()
            print('---- End-Maintenance ----')
            self.get_car_status()
            print(
                '------------------ End-Trip | {} KM | {} KM of {} KM ---'.format(trip_distance, travelled, distance))
        print('---------------------------- End Travel | {} KM --'.format(distance))

    def get_autonomy_tank(self):
        response = client.get(
            self.car_status_url,
            content_type='application/json',
            format='json'
        )
        content = json.loads(response.content)
        return float(content['fuel_autonomy'])

    def get_autonomy_tyres(self):
        response = client.get(
            self.car_status_url,
            content_type='application/json',
            format='json'
        )
        content = json.loads(response.content)
        return float(content['tyres_autonomy'])

    def trip(self, min_distance):
        response = client.post(
            self.trip_url,
            data={'distance': min_distance},
            content_type='application/json',
            format='json'
        )
        return response

    def maintenance_tyres(self):
        print('----Maintenance-Tyres---')
        response = client.post(
            self.maintenance_url,
            data={'replace_part': '_tyre'},
            content_type='application/json',
            format='json'
        )
        content = json.loads(response.content)
        try:
            print('Warning: ' + str(content['error']))
        except KeyError:
            print('New: ' + str(content['create_new_tyres']))
            print('Available: ' + str(content['use_available_tyres']))
            print('Discarded: ' + str(content['discarded_tyres']))

    def maintenance_fuel(self):
        print('----Maintenance-Fuel---')
        response = client.post(
            self.maintenance_url,
            data={'replace_part': '_fuel'},
            content_type='application/json',
            format='json'
        )
        content = json.loads(response.content)
        try:
            print('Warning: ' + str(content['error']))
        except KeyError:
            print('Fuel: ' + str(content['message']))

    def trip_status(self, content):
        content = json.loads(content)
        try:
            print('Warning: ' + str(content['error']))
        except KeyError:
            print('---Trip-Info---' +
                  '#' + str(content['trip_status']['id']))
            print('Car Id: ' + str(content['car_status']['id']) +
                  ' | Odometer: ' + str(content['car_status']['odometer']))
            print('Fuel: ' + str(content['car_status']['fuel']) +
                  '%' + ' | Tank: ' + str(content['car_status']['tank']))
            print('Fuel: ' +
                  str(content['car_status']['fuel_autonomy']) + ' km | Max: ' +
                  str(content['car_status']['fuel_autonomy_total']) + ' km')
            print('Tyres: ' +
                  str(content['car_status']['tyres_autonomy']) + ' km | Max: ' +
                  str(content['car_status']['tyres_autonomy_total']) + ' km')
            print('Finished: ' + str(content['trip_status']['finished']) +
                  ' | Distance: ' + str(content['trip_status']['distance']) + ' | Travelled distance: ' +
                  str(content['trip_status']['travelled_distance']))
            print('----Trip-Tyres-Info----')
            for tyre in content['car_status']['tyres']:
                print(
                    'Tyre: #' + str(tyre['id']) + ' | Degradation:'
                    + str(tyre['degradation']) + '%'
                    + ' | Status: ' + str(tyre['status']))

    def get_car_status(self):
        response = client.get(
            self.car_status_url,
            content_type='application/json',
            format='json'
        )
        content = json.loads(response.content)
        try:
            print('Warning: ' + str(content['error']))
        except KeyError:
            print('----Car-Status---' +
                  '#' + str(content['id']))
            print('Car Id: #' + str(content['id']) +
                  ' | Odometer: ' + str(content['odometer']))
            print('Fuel: ' + str(content['fuel']) +
                  '%' + ' | Tank: ' + str(content['tank']))
            print('Fuel: ' + str(content['fuel_autonomy']) + ' km' +
                  ' | Max: ' + str(content['fuel_autonomy_total']) + ' km')
            print('Tyres: ' + str(content['tyres_autonomy']) + ' km' +
                  ' | Max: ' + str(content['tyres_autonomy_total']) + ' km')
            print('----Car-Tyres-Info---')
            for tyre in content['tyres']:
                print(
                    'Tyre: #' + str(tyre['id']) + ' | Degradation:'
                    + str(tyre['degradation']) + '%'
                    + ' | Status: ' + str(tyre['status']))
            fuel_autonomy = content['fuel_autonomy']
            tyres_autonomy = content['tyres_autonomy']
            return fuel_autonomy, tyres_autonomy

    def get_trip_distance(self, fuel_autonomy, tyres_autonomy, distance):
        if fuel_autonomy >= tyres_autonomy:
            trip_distance = tyres_autonomy
        elif fuel_autonomy <= tyres_autonomy:
            trip_distance = fuel_autonomy
        else:
            trip_distance = fuel_autonomy
        if trip_distance > distance:
            return distance
        return trip_distance
