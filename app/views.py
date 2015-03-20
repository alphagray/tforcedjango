"""
Definition of views.
"""

import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login

from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.backends.facebook import FacebookOAuth2
from social.backends.twitter import TwitterOAuth
from social.backends.reddit import RedditOAuth2
from social.backends.utils import load_backends
from social.apps.django_app.utils import psa

from app.decorators import render_to

from django.template import RequestContext
from datetime import datetime


def logout(request):
    """Logs out user """
    auth_logout(request)
    return redirect('/')

def context(**extra):
    return dict({
            'facebook_id': getattr(settings, 'SOCIAL_AUTH_FACEBOOK_KEY', None),
            'facebook_scope': ''.join(FacebookOAuth2.DEFAULT_SCOPE),
            'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS)
        }, **extra)


@render_to('auth.html')
def authtest(request, backend):
    """ Test authorize view """
    if not request.user.is_authenticated():
        return context()
    return redirect('done')




@login_required
@render_to('authtest.html')
def done(request, backend):
    """Login complete view, displays user data"""
    return context()

@login_required
@render_to('home.html')
def complete_profile(request, **kwargs):
    backend = request.session['partial_pipeline']['backend']
    return context(missing_data=True, backend=backend)

@render_to('home.html')
def require_email(request):
    backend = request.session['partial_pipeline']['backend']
    return context(email_required=True, backend=backend)

@psa('social:complete')
def ajax_auth(request, backend):
    if isinstance(request.backend, BaseOAuth1):
        token = {
            'oauth_token' : requst.REQUEST.get('access_token'),
            'oauth_token_secret': request.REQUEST.get('access_token_secret'),
        }
    elif isinstance(request.backend, BaseOAuth2):
        token = request.REQUEST.get('access_token')
    else:
        raise HttpResponseBadRequest('Wrong backend type')
    user = request.backend.do_auth(token, ajax=True)
    login(request, user)
    data = {'id': user.id, 'username': user.username}
    return HttpResponse(json.dumps(data), mimetype="application/json")



def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance=RequestContext(request,
            {
                'title':'Home Page',
                'year':datetime.now().year,
            })
    )



def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance=RequestContext(request,
            {
                'title':'Contact',
                'message':'Your contact page.',
                'year':datetime.now().year,
            })
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance=RequestContext(request,
            {
                'title':'About',
                'message':'Your application description page.',
                'year':datetime.now().year,
            })
    )
