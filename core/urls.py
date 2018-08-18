from django.urls import path

import core.views

urlpatterns = [
    path('', core.views.Index.as_view()),
    path('node/create/', core.views.NodeCreate.as_view()),
    path('node/stop/<int:pk>/', core.views.NodeStop.as_view(), name='node_stop'),
    path('node/destroy/<int:pk>/', core.views.NodeDestroy.as_view(), name='node_destroy'),
]
