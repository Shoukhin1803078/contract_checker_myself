from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
# Create your views here.

def home(request):
    return JsonResponse(
        {
            'hello': 'this is home'
        },
        status=200   #status=status.HTTP_200_OK
    )