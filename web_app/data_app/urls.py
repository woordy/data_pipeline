from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from .views import AVGTicketPriceByDeparture, Indexview, AirportDepartureView, TicketPriceView

urlpatterns = [
    path('avg', AVGTicketPriceByDeparture.as_view(), name='get_avg_ticket_price_ByDeparture'),
    path('', Indexview.as_view(), name='Index'),
    path('api/chart/airports', AirportDepartureView.as_view(), name='get-chart-data'),
    path('api/chart/prices', TicketPriceView.as_view(), name='get-price-data'),
    path('api-auth/', include('rest_framework.urls'))
]
