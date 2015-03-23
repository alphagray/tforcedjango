"""
Definition of views.
"""

import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpRequest
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.models import User
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.backends.facebook import FacebookOAuth2
from social.backends.twitter import TwitterOAuth
from social.backends.reddit import RedditOAuth2
from social.backends.utils import load_backends
from social.apps.django_app.utils import psa

from app.models import Profile

from app.decorators import render_to

from django.template import RequestContext
from datetime import datetime


@login_required
def profile(request, incomplete=False):
    context = RequestContext(request, { 'request': request, 'user': request.user, 'incomplete': incomplete, 'profile': request.user.profile })
    return render_to_response('app/profile.html', context_instance=context)
