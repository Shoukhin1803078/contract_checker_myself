from django.urls import path
from . import views

urlpatterns = [
    path('home/',views.home, name='home'),
    path('bank-ocr/', views.BankOcrView.as_view(), name='bank-ocr'),
    path('schema-records/', views.SchemaRecordView.as_view(), name='schema-records'),
]