"""
Definition of urls for DjangoWebProject.
"""

from datetime import datetime
from django.conf.urls import patterns, url
from app.forms import BootstrapAuthenticationForm


# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',

    # Examples:
    url(r'^$', 'app.views.home', name='home'),
    url(r'^contact$', 'app.views.contact', name='contact'),
    url(r'^about', 'app.views.about', name='about'),
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {
            'template_name': 'app/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Log in',
                'year':datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        'django.contrib.auth.views.logout',
        {
            'next_page': '/',
        },
        name='logout'),
    # Uncomment the podcasts line to enable podcast stuff. 
    #url(r"^podcasts/", include("podcasting.urls")),
    #url(r"^feeds/podcasts/", include("podcasting.urls_feeds")),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^ajax/', include('ajax.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # social auth urls
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'', include('app.urls', namespace='app')),
)
