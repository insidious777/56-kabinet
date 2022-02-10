"""fs_cabinet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include(('menu.urls', 'menu'), namespace='menu')),
    path('api/v1/menu/', include(('menu.api.urls', 'menu'), namespace='menu_api')),

    path('order/', include(('order.urls', 'order'), namespace='order')),
    path('api/v1/order/', include(('order.api.urls', 'order'), namespace='order_api')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = _('56 Cabinet')
admin.site.site_title = _('56 Cabinet')
admin.site.index_title = _('Administration')