from django.db.models import Max, Min
from django.db import models

# Create your models here.


class Car(models.Model):

    KM_PER_LITER = 8
    DEFAULT_GAS_CAPACITY = 45
    LOW_CURRENT_GAS = 5
    MAX_QUANTITY_TYRES = 4

    gas_capacity = models.FloatField(
        'Gas Capacity in Liter', default=DEFAULT_GAS_CAPACITY)
    current_gas = models.FloatField('Current Gas in %', default=0.0)
    max_quantity_tyres = models.IntegerField(
        'Quantity of Tires', default=MAX_QUANTITY_TYRES)
    km_per_liter = models.FloatField(
        'Gas consumption per liter', default=KM_PER_LITER)
    odometer = models.FloatField(
        'Odometer', default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Id: {} | capacity: {} Liter(s) | current: {}%".format(self.id, self.gas_capacity, self.current_gas)

    class Meta:
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'

    def trip(self, distance):
        if self.check_can_trip():
            trip = Trip.objects.create(car=self, distance=distance)
            travelled = 0.0
            stop = False
            finished = False
            distance = float("%.1f" % (distance))
            additional = float("%.1f" % (distance % 1))
            trip.distance = distance
            distance = distance - additional
            while travelled < distance and not stop:
                stop = self.consume_fuel(1)
                stop = self.degrade_tyres(1)
                self.odometer += 1.0
                self.save()
                travelled += 1.0
            if additional != 0.0:
              stop = self.consume_fuel(additional)
              stop = self.degrade_tyres(additional)
              self.odometer += additional
              self.save()
              travelled += additional
            trip.travelled_distance = travelled
            trip.save()
            if trip.distance == trip.travelled_distance:
                finished = True
            return {
                'car_status': self.get_status(), 
                'trip_status': {
                    'id': trip.id,
                    'finished': finished, 
                    'distance': trip.distance, 
                    'travelled_distance': trip.travelled_distance
                }
            }
        else:
            return {'error': "Car #{} in no condition to travel.".format(self.id)}

    def maintenance(self, replace_part):
        if replace_part == '_fuel':
            tank_left = self.gas_tank_left()
            refuel = self.gas_capacity - tank_left
            return self.refuel(refuel)
        elif replace_part == '_tyre':
            return self.create_tyre()
        else:
            return {'error': "Maintenance option {} is invalid.".format(replace_part)}

    def refuel(self, quantity):
        tank_left = self.gas_tank_left()
        if quantity > 0:
            if self.current_gas <= Car.LOW_CURRENT_GAS:
                if (quantity + tank_left) >= self.gas_capacity:
                    self.current_gas = 100.0
                    self.save()
                    set_order_fueling(self, quantity)
                    return {'message': "{}".format(self.current_gas)}
                else:
                    self.current_gas = "%.1f" % (
                        quantity / self.gas_capacity * 100)
                    self.save()
                    set_order_fueling(self, quantity)
                    return {'message': "{}".format(self.current_gas)}
            else:
                return {'error': "Tank is over {}% of capacity | current: {}%.".format(Car.LOW_CURRENT_GAS, self.current_gas)}
        else:
            return {'error': "Quantity must be more than one liter."}

    def create_tyre(self):
        new = 0
        available = 0
        discarded = 0
        tyre_in_use_count = self.tyre_set.filter(status=1)
        swapp_limit = self.tyre_set.filter(
            status=1,
            degradation__gte=Tyre.DEGRADATION_SWAPP_LIMIT - 0.1)
        if tyre_in_use_count.count() == 0:
            for i in range(self.max_quantity_tyres):
                new, available = get_or_create_tyre(self, new, available)
        if tyre_in_use_count.count() < self.max_quantity_tyres:
            diff = self.max_quantity_tyres - tyre_in_use_count.count()
            for i in range(diff):
                new, available = get_or_create_tyre(self, new, available)
        elif swapp_limit.count() > 0:
            for tyre_swapp in swapp_limit:
                new, available = get_or_create_tyre(self, new, available)
                tyre_swapp.status = 3
                tyre_swapp.save()
        tyres_shatter = self.tyre_set.filter(
            degradation__gte=Tyre.DEGRADATION_SWAPP_LIMIT - 0.1)
        discarded = tyres_shatter.count()
        tyres_shatter.update(status=3)
        tyres_in_use = {
            'tyres': [{'id': tyre.id, 'degradation': tyre.degradation} for tyre in self.tyre_set.filter(status=1)],
            'create_new_tyres': new,
            'use_available_tyres': available,
            'discarded_tyres': discarded
        }
        return tyres_in_use

    def get_status(self):
        tyres_in_use = [
            {'id': tyre.id, 'degradation': tyre.degradation, 'status': tyre.get_status_display()} for tyre in self.tyre_set.filter(status__in=[1, 4])
        ]
        car_status = {
            'id': self.id,
            'capacity': "{}".format(self.gas_capacity),
            'fuel': "{}".format(self.current_gas),
            'km_per_liter': "{}".format(self.km_per_liter),
            'odometer': "{}".format(self.odometer),
            'fuel_autonomy': self.get_autonomy_tank(),
            'fuel_autonomy_total': self.get_autonomy_tank_total(),
            'tyres_autonomy': self.get_autonomy_tyres(),
            'tyres_autonomy_total': self.get_autonomy_tyres_total(),
            'tank': 'Empty' if self.current_gas == 0.0 else 'Full',
            'tyres': tyres_in_use            
        }
        return car_status

    def get_status_tyres(self):
        tyres = [
            {'id': tyre.id, 'degradation': tyre.degradation, 'status': tyre.get_status_display()} for tyre in self.tyre_set.filter(status__in=[1, 4])
        ]
        return tyres

    def gas_tank_left(self):
        tank_left = float("%.1f" % (self.gas_capacity - (self.gas_capacity / 100) *
                                    (100 - self.current_gas)))
        return tank_left

    def check_can_trip(self):
        ready_to_trip = False
        if self.tyre_set.filter(status=1).count() == self.max_quantity_tyres:
            tyres_degradation = self.tyre_set.filter(status=1).aggregate(
                Min('degradation'))['degradation__min']
            if self.current_gas > Car.LOW_CURRENT_GAS and tyres_degradation < Tyre.DEGRADATION_SWAPP_LIMIT:
                ready_to_trip = True
        return ready_to_trip

    def consume_fuel(self, distance):
        stop = False
        consume = distance / self.km_per_liter
        self.current_gas -= float("%.1f" % (consume / self.gas_capacity * 100))
        if self.current_gas <= 0.0:
            self.current_gas = 0.0
            stop = True
        self.current_gas = float("%.1f" % (self.current_gas))
        self.save()
        return stop

    def degrade_tyres(self, distance):
        stop = False
        stops = []
        for tyre in self.tyre_set.filter(status=1):
            stops.append(tyre.degrade(distance))
        stop = True if True in stops else False
        return stop

    def get_autonomy_tank(self):
        autonomy = 0
        if self.current_gas > 0:
            lower = 100 - (Car.LOW_CURRENT_GAS)
            current_gas = self.current_gas if self.current_gas < lower else lower
            if current_gas > Car.LOW_CURRENT_GAS:
                gas = float("%.1f" % ((self.gas_capacity / 100) *
                                        (current_gas - Car.LOW_CURRENT_GAS)))
            else:
                gas = float("%.1f" % ((self.gas_capacity / 100) *
                                      (current_gas)))
            autonomy = self.km_per_liter * gas
        return autonomy

    def get_autonomy_tyres(self):
        autonomy = 0
        lower = Tyre.DEGRADATION_SWAPP_LIMIT
        tyres = self.tyre_set.filter(status=1)
        if tyres.count() == self.max_quantity_tyres:
            degradation_max = tyres.aggregate(
                Max('degradation'))['degradation__max']
            degradation = lower - degradation_max
            degradation = degradation if degradation < lower else lower
            autonomy = float("%.1f" % (Tyre.KM_TYRE_DEGRADATION * degradation))
        return autonomy

    def get_autonomy_tank_total(self):
        autonomy = 0
        gas = float("%.1f" % ((self.gas_capacity / 100) *
                                (self.current_gas)))
        autonomy = self.km_per_liter * gas
        return autonomy

    def get_autonomy_tyres_total(self):
        autonomy = 0
        tyres = self.tyre_set.filter(status=1)
        if tyres.count() == self.max_quantity_tyres:
            degradation_max = tyres.aggregate(
                Max('degradation'))['degradation__max']
            degradation = 100 - degradation_max
            autonomy = float("%.1f" % (Tyre.KM_TYRE_DEGRADATION * degradation))
        return autonomy


class Tyre(models.Model):

    PERCENTAGE_TYRE_DEGRADATION = 1
    KM_TYRE_DEGRADATION = 3
    DEGRADATION_SWAPP_LIMIT = 94
    DEGRADATION_CREATE_LIMIT = 95

    TYRE_STATUS = (
        (1, 'In Use'),
        (2, 'Available'),
        (3, 'Discarded'),
        (4, 'Shatter')
    )

    degradation = models.FloatField('Degradation in %', default=0)
    status = models.PositiveSmallIntegerField(
        'Status', choices=TYRE_STATUS, default=2)
    car = models.ForeignKey("Car", verbose_name='Car',
                            on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Id: {} | car: {} | degradation: {}%".format(self.id, self.car.id, self.degradation)

    class Meta:
        verbose_name = 'Tyre'
        verbose_name_plural = 'Tyres'

    def get_status(self):
        tyre = {'id': self.id,
                'degradation': self.degradation,
                'car': self.car.id if self.car else None,
                'status': self.get_status_display(),
                'created_at': self.created_at}
        return tyre

    def degrade(self, distance):
        stop = False
        degradation = distance / Tyre.KM_TYRE_DEGRADATION
        self.degradation += degradation
        if self.degradation >= 99.9:
            self.status = 4
            self.degradation = 100.0
            stop = True
        self.save()
        return stop


class Trip(models.Model):
    distance = models.FloatField('Distance in KM')
    travelled_distance = models.FloatField(
        'Travelled distance in KM', null=True)
    car = models.ForeignKey("Car", verbose_name='Car',
                            on_delete=models.CASCADE)
    description = models.TextField('description')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Id: {} | car: {} | distance: {} KM | travelled: {}".format(self.id, self.car.id, self.distance, self.travelled_distance)

    class Meta:
        verbose_name = 'Trip'
        verbose_name_plural = 'Trips'


class Order(models.Model):
    ORDER_TYPE = (
        (1, 'Refuelling'),
        (2, 'Change tyre'),
        (3, 'New tyre'),
    )
    distance = models.FloatField('Distance in KM', null=True)
    car = models.ForeignKey("Car", verbose_name='Car',
                            on_delete=models.CASCADE, null=True)
    fueled = models.FloatField("Fueled in liter(s)", default=0.0)
    tyre = models.ForeignKey("Tyre", verbose_name='Tyre',
                             on_delete=models.CASCADE, null=True)
    type = models.PositiveSmallIntegerField(
        'Order Type', choices=ORDER_TYPE, default=2)
    description = models.TextField('description')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Id: {} | Type: {}".format(self.id, self.get_type_display())


    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


def get_or_create_tyre(car, new=0, available=0):
    tyre_available = Tyre.objects.filter(
        status=2,
        degradation__lte=Tyre.DEGRADATION_CREATE_LIMIT - 0.1)[:1]
    if tyre_available.exists():
        for tyre in tyre_available:
            tyre.status = 1
            tyre.car = car
            tyre.save()
            available = + 1
            Order.objects.create(
                car=car, tyre=tyre, type=2, description="Allocating available tyre for car #{} | Degradation: {}%".format(car.id, tyre.degradation))
    else:
        tyre = Tyre.objects.create(car=car, status=1)
        new += 1
        Order.objects.create(
            car=car, tyre=tyre, type=3, description="Creating new tyre for car #{}".format(car.id))
    return new, available


def set_order_fueling(car, quantity):
    Order.objects.create(
        car=car, fueled=quantity, type=1, description="Fueling car #{} | fueled: {} liter(s).".format(car.id, quantity))


