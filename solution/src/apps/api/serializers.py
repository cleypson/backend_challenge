from rest_framework import serializers
from .models import Car, Tyre, Trip, Order


class CarSerializer(serializers.ModelSerializer):
    tyres_status = serializers.SerializerMethodField()
    class Meta:
        model = Car
        fields = ['id', 'gas_capacity', 'max_quantity_tyres',
                  'current_gas', 'odometer', 'km_per_liter', 'created_at', 'tyres_status']
        read_only_fields = ['id', 'gas_capacity', 'max_quantity_tyres',
                            'current_gas', 'odometer', 'km_per_liter', 'created_at']

    def get_tyres_status(self, instance):
        return instance.get_status_tyres()


class TyreSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Tyre
        fields = ['id', 'degradation', 'car',
                  'status', 'status_display', 'created_at']
        read_only_fields = ['id', 'degradation', 'car', 'status', 'created_at']

    def get_status_display(self, instance):
        return instance.get_status_display()


class TripSerializer(serializers.ModelSerializer):

    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = [
            'id',
            'distance',
            'car',
            'description',
            'odometer',
            'created_at'
        ]


class OrderSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'km',
                  'trip', 'car', 'type', 'description', 'fueled', 'type_display', 'created_at']
        read_only_fields = ['id', 'km',
                            'trip', 'car', 'type', 'description', 'fueled', 'created_at']

    def get_type_display(self, instance):
        return instance.get_type_display()
