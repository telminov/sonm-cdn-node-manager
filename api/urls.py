from django.urls import path
from api import views

app_name = 'api'

urlpatterns = [
    path('nodes/', views.Nodes.as_view(), name='nodes'),
]

