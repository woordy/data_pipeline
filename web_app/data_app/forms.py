from django import forms
from .models import AVGTicketPriceByDeparture


class AVGTicketPriceByDepartureForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2025)))
    end_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2025)))

    class Meta:
        model = AVGTicketPriceByDeparture
        fields = ["place_id_origin", "place_id_dest"]
