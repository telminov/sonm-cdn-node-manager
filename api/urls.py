from django.urls import path
from rest_framework.routers import SimpleRouter
from api import views

app_name = 'api'

urlpatterns = [
    path('nodes_by_regions/', views.NodesByRegions.as_view(), name='nodes_by_regions'),
]

router = SimpleRouter()
router.register('node', views.Node)
urlpatterns += router.urls
