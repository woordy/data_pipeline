from django.contrib import admin
from .models import \
    (Country, City, PlaceType, Place,
     Carrier, AVGTicketPriceByCarrier,
     AVGTicketPriceByWindow, AVGTicketPriceByDeparture)

# Register your models here.
admin.site.register(Country)
admin.site.register(PlaceType)
admin.site.register(Carrier)
admin.site.register(AVGTicketPriceByCarrier)
admin.site.register(AVGTicketPriceByWindow)


class CityModelAdmin(admin.ModelAdmin):
    """
    Lists the models as a list
    """
    list_display = ['__str__', 'city_id', 'city', 'country_name']
    list_display_links = ['__str__']
    list_filter = ['city']
    search_fields = ['city_id', 'city']

    class Meta:
        model = City


admin.site.register(City, CityModelAdmin)


class PlaceModelAdmin(admin.ModelAdmin):
    """
    Lists the models as a list
    """
    list_display = ['__str__', 'place_id', 'iata_code', 'name', 'type', 'skyscanner_code', 'city']
    list_display_links = ['__str__']
    list_filter = ['city']
    search_fields = ['place_id', 'iata_code']

    class Meta:
        model = Place


admin.site.register(Place, PlaceModelAdmin)


class AVGTicketPriceByDepartureModelAdmin(admin.ModelAdmin):
    """
    Provides Average prices of all  tickets from 2 locations by departure time
    """
    list_display = ['place_id_origin', 'place_id_dest', 'departure_date', 'count', 'sum']
    list_display_links = ['place_id_origin', 'place_id_dest', 'departure_date']
    list_filter = ['place_id_origin', 'place_id_dest', 'departure_date']
    search_fields = ['place_id_origin', 'place_id_dest', 'departure_date']

    class Meta:
        model = AVGTicketPriceByDeparture


admin.site.register(AVGTicketPriceByDeparture, AVGTicketPriceByDepartureModelAdmin)
