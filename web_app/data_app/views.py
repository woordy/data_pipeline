import sys

sys.path.append('..')
from django.shortcuts import render

from .forms import AVGTicketPriceByDepartureForm
from data_analysis import PriceAnalytics

from django.views.generic import TemplateView
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework import status
from .serializer import AVGTicketPriceByDepartureSerializer
from .models import AVGTicketPriceByDeparture as AVGTicketPriceByDepartureModel

# Create your views here.


class AVGTicketPriceByDeparture(TemplateView):
    template_name = "chart.html"

    def get(self, request):
        form = AVGTicketPriceByDepartureForm()
        context = {"form": form}
        return render(request=request, template_name=self.template_name, context=context)

    def post(self, request):
        form = AVGTicketPriceByDepartureForm(request.POST or None)
        if form.is_valid():
            origin = form.cleaned_data.get('place_id_origin')
            destination = form.cleaned_data.get('place_id_dest')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

            price_analysis = PriceAnalytics()
            result = price_analysis. \
                get_average_tickets_by_source_destination(
                    originId=int(request.POST['place_id_origin']),
                    destinationId=int(request.POST['place_id_dest']),
                    window=[request.POST['start_date'], request.POST['end_date']])

            print('Average from: {origin} to {destination} between {start_date} and {end_date} = {result}'
                  .format(origin=origin, destination=destination, result=result,
                          start_date=start_date, end_date=end_date))
            args = {'result': result}
            return render(request, self.template_name, args)


class Indexview(View):

    template_name = "charts.html"

    def get(self, request, *args, **kwargs):
        form = AVGTicketPriceByDepartureForm()
        context = {"form": form}
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        form = AVGTicketPriceByDepartureForm(request.POST)
        if form.is_valid():

            origin = form.cleaned_data.get('place_id_origin')
            destination = form.cleaned_data.get('place_id_dest')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            price_analysis = PriceAnalytics()
            result, quotes = price_analysis. \
                get_average_tickets_by_source_destination(
                    originId=int(request.POST['place_id_origin']),
                    destinationId=int(request.POST['place_id_dest']), start_date=start_date, end_date=end_date)

            print('Average from: {origin} to {destination} between {start_date} and {end_date} = {result}'
                  .format(origin=origin, destination=destination, result=result,
                          start_date=start_date, end_date=end_date))
            if result is None:
                result = 'No value found'
                quotes_dates = ''
                quotes_avg = ''
            else:
                result = 'Average from: {origin} to {destination} between {start_date} and {end_date} = $ {result}'\
                    .format(origin=origin, destination=destination, result=round(result, 2), start_date=start_date,
                            end_date=end_date)
                quotes_dates = quotes['departure_date'].dt.strftime('%B %d, %Y').values
                quotes_avg = quotes['average'].values
                print(quotes_avg)

            # args = {'form': form, 'result': result, 'quotes_dates': quotes_dates, 'quotes_avg': quotes_avg}
            args = {'result': result, 'quotes_dates': quotes_dates, 'quotes_avg': quotes_avg}
            return render(request, self.template_name, args)


class TicketPriceView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        price_analysis = PriceAnalytics()
        result, quotes = price_analysis. \
            get_average_tickets_by_source_destination(originId=65363, destinationId=68528,
                                                      start_date='1900-01-01', end_date='2050-01-01')
        if result is None:
            result = 'No value found'
            quotes_dates = ''
            quotes_avg = ''
        else:
            quotes_dates = quotes['departure_date'].dt.strftime('%B %d, %Y').values
            quotes_avg = quotes['average'].values
        data = {
            "labels": quotes_dates,
            "data": quotes_avg
        }

        return Response(data)

    def post(self, request):
        serializer = AVGTicketPriceByDepartureSerializer(data=request.data)
        form = AVGTicketPriceByDepartureForm(request.POST or None)
        if form.is_valid():

            origin = form.cleaned_data.get('place_id_origin')
            destination = form.cleaned_data.get('place_id_dest')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

        if serializer.is_valid():
            originId = serializer.data.get('originId')
            destinationId = serializer.data.get('destinationId')
            start_date = serializer.data.get('start_date')
            end_date = serializer.data.get('end_date')
            context = {
                'data': [originId, destinationId, start_date, end_date]
            }
            return Response(context)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class AirportDepartureView(APIView):
    """
     Returns an API view that is consumed by the charts
    """
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):

        qs = AVGTicketPriceByDepartureModel.objects.values('place_id_origin__name').annotate(Sum('count'))

        airports = [item['place_id_origin__name'] for item in qs]
        num_departures = [item['count__sum'] for item in qs]
        data = {
            "labels":  airports,
            "data": num_departures
        }
        return Response(data)

