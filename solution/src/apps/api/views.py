from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import CarSerializer, TyreSerializer, TripSerializer, OrderSerializer
from .models import Car, Tyre, Trip, Order

# Create your views here.


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    @action(detail=True, methods=['post'])
    def trip(self, request, pk=None):
        instance = self.get_object()
        distance = float(request.data.get('distance', 0.0))
        status = instance.trip(distance)
        return Response(status)

    @action(detail=True, methods=['post'])
    def refuel(self, request, pk=None):
        instance = self.get_object()
        quantity = request.data.get('quantity', 0.0)
        status = instance.refuel(int(quantity))
        return Response(status)

    @action(detail=True, methods=['post'])
    def maintenance(self, request, pk=None):
        instance = self.get_object()
        replace_part = request.data.get('replace_part', "")
        status = instance.maintenance(replace_part)
        return Response(status)

    @action(detail=True, methods=['get'])
    def get_car_status(self, request, pk=None):
        instance = self.get_object()
        status = instance.get_status()
        return Response(instance.get_status())

    @action(detail=True, methods=['post'])
    def create_tyre(self, request, pk=None):
        instance = self.get_object()
        status = instance.create_tyre()
        return Response(status)

    @action(detail=False, methods=['post'])
    def create_car(self, request, pk=None):
        car = Car.objects.create()
        car.maintenance('_fuel')
        car.maintenance('_tyre')
        return Response(car.get_status())


class TyreViewSet(viewsets.ModelViewSet):
    queryset = Tyre.objects.all()
    serializer_class = TyreSerializer

    @action(detail=False, methods=['post'])
    def create_tyre(self, request, pk=None):
        tyre = Tyre.objects.create()
        return Response(tyre.get_status())

    @action(detail=False, methods=['get'])
    def available(self, request, pk=None):
        tyres_json = []
        for tyre in Tyre.objects.filter(status=2):
            tyres_json.append(tyre.get_status())
        return Response(tyres_json)

    @action(detail=False, methods=['get'])
    def discarded(self, request, pk=None):
        tyres_json = []
        for tyre in Tyre.objects.filter(status=3):
            tyres_json.append(tyre.get_status())
        return Response(tyres_json)

    @action(detail=False, methods=['get'])
    def in_use(self, request, pk=None):
        tyres_json = []
        for tyre in Tyre.objects.filter(status=1):
            tyres_json.append(tyre.get_status())
        return Response(tyres_json)


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
