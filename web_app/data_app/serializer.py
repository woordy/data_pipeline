from rest_framework import serializers
from .models import AVGTicketPriceByDeparture


class AVGTicketPriceByDepartureSerializer(serializers.Serializer):

    class Meta:
        model = AVGTicketPriceByDeparture
        fields = '__all__'
