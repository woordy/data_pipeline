from django.db import models


# Create your models here.


class Country(models.Model):
    """
    Creates Model for different countries
    Normalizes Airport
    """
    country = models.CharField(max_length=264, unique=True, primary_key=True)

    def __str__(self):
        return str(self.country)

    class Meta:
        verbose_name_plural = 'Countries'


class City(models.Model):
    """
    Creates the model of Airport City
    Normalizes cities
    """
    city_id = models.CharField(max_length=264, primary_key=True)
    city = models.CharField(max_length=264, blank=False, null=False)
    country_name = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.city) + ' ' + str(self.country_name)

    class Meta:
        verbose_name_plural = 'Cities'


class PlaceType(models.Model):
    """
    Creates the model for airport type
    Normalizes place types
    """
    type = models.CharField(max_length=264, unique=True, primary_key=True)

    def __str__(self):
        return str(self.type)


class Place(models.Model):
    """
    Creates the model for Airports
    """
    place_id = models.PositiveIntegerField(unique=True, primary_key=True)
    iata_code = models.CharField(max_length=264, blank=False, null=False, unique=True)
    name = models.CharField(max_length=264, unique=True)
    type = models.ForeignKey(PlaceType, on_delete=models.CASCADE)
    skyscanner_code = models.CharField(max_length=264, blank=False, null=False, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class Carrier(models.Model):
    """
    Model for Airports
    """
    carrier_id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=264, unique=True)

    def __str__(self):
        return str(self.name)


class AVGTicketPriceByDeparture(models.Model):
    """
    Provides Average prices of all  tickets from 2 locations by departure time
    """
    departure_date = models.DateTimeField(blank=False, null=False)
    place_id_origin = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='%(class)s_place_id_origin')
    place_id_dest = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='%(class)s_place_id_dest')
    count = models.FloatField(blank=False, null=False)
    sum = models.FloatField(blank=False, null=False)

    def __str__(self):
        return str(self.place_id_origin) + '-' + str(self.place_id_dest) + '-' + str(self.departure_date)


class AVGTicketPriceByCarrier(models.Model):
    """
    Provides Average prices of all by carrier
    """
    quote_dateTime = models.DateTimeField(blank=False, null=False)
    place_id_origin = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='%(class)s_place_id_origin')
    place_id_dest = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='%(class)s_place_id_dest')
    carrier_id = models.ForeignKey(Carrier, on_delete=models.CASCADE)
    count = models.FloatField(blank=False, null=False)
    total_sum = models.FloatField(blank=False, null=False)

    def __str__(self):
        return str(self.place_id_origin) + '-' + str(self.place_id_dest) + '-' + str(self.quote_dateTime)


class AVGTicketPriceByWindow(models.Model):
    """
    Provides Average prices of all  tickets from 2 locations by window
    Window: Time between date of quote and date of departure
    """
    quote_dateTime = models.DateTimeField(blank=False, null=False)
    place_id_origin = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='%(class)s_place_id_origin')
    place_id_dest = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='%(class)s_place_id_dest')
    window = models.PositiveIntegerField(blank=False, null=False)
    count = models.FloatField(blank=False, null=False)
    sum = models.FloatField(blank=False, null=False)


class AVGTicketPriceByDepartureUI(AVGTicketPriceByDeparture):
    """
    We create a proxy model which extends AVGTicketPriceByDeparture without a creating table
    """
    class Meta:
        proxy = True
        verbose_name = 'Average Ticket Price By Departure Summary'
        verbose_name_plural = 'Average Tickets Price By Departure Summary'
