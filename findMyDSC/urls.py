from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import render

urlpatterns = [
    path('adminadmin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('admin/', include('admins.urls')),
    path('', views.adminSignIn, name='adminSignIn'),
    path('signUp/', views.signUp, name='signUp'),
    path('adminSignIn/', views.adminSignIn, name='adminSignIn'),
    path('userSignIn/', views.userSignIn, name='userSignIn'),
    path('logOut/', views.logOut, name='logOut'),
    path('termsCondition/', views.termsCondition, name='termsCondition'),
    path('plan/selectPlan', views.selectPlan, name='selectPlan'),
    path('plan/pay/paymentSuccess/', views.paymentSuccess, name='paymentSuccess'),
    path('plan/pay/paymentFail/', views.paymentFail, name='paymentFail'),
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def custom_404(request, exception):
    return render(request, '404.html', status=404)

handler404 = custom_404