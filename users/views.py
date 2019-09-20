from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.core import serializers
from django.forms.models import model_to_dict

from .models import Flats
import json

@login_required()
def Dashboard(request):
	return render(request, 'users/dashboard.html', {})


@login_required
def Recharge(request):
	return render(request, 'users/recharge.html', {})

@login_required()
def getFlat(request):
	if request.method == "POST":
		tower = request.POST.get("tower", '')
		flat = request.POST.get("flat", '')
		if tower and flat:
			flat = get_object_or_404(Flats, tower=tower, flat=flat)
			if flat:
				flat = serializers.serialize('json', [flat,])[1:-1]
				data = json.loads(flat)['fields']
				return JsonResponse(data)
	return HttpResponse(status=404)
