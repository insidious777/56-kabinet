from django.urls import path

from menu.views import MainView, AdditionsListView

urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('additions/', AdditionsListView.as_view(), name='additions_list'),
]
