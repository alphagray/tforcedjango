from django.shortcuts import redirect
from app.models import Profile
from social.pipeline.partial import partial
from django.contrib.auth import login, authenticate

from uuid import uuid4

from social.utils import slugify, module_member


USER_FIELDS = ['username', 'email']

#custom get_username pipeline piece so that i can understand it.
def get_username(strategy, details, user=None, *args, **kwargs):
    if 'username' not in strategy.setting('USER_FIELDS', USER_FIELDS):
        return
    storage = strategy.storage

    if not user:
        email_as_username = strategy.setting('USERNAME_IS_FULL_EMAIL', False)
        uuid_length = strategy.setting('UUID_LENGTH', 16)
        max_length = storage.user.username_max_length()
        do_slugify = strategy.setting('SLUGIFY_USERNAMES', False)
        do_clean = strategy.setting('CLEAN_USERNAMES', True)

        if do_clean:
            clean_func = storage.user.clean_username
        else:
            clean_func = lambda val: val

        if do_slugify:
            override_slug = strategy.setting('SLUGIFY_FUNCTION')
            if override_slug:
                slug_func = module_member(override_slug)
            else:
                slug_func = slugify
        else:
            slug_func = lambda val: val

        if email_as_username and details.get('email'):
            username = details['email']
        elif details.get('username'):
            username = details['username']
        else:
            username = uuid4().hex

        short_username = username[:max_length - uuid_length]
        final_username = slug_func(clean_func(username[:max_length]))

        # Generate a unique username for current user using username
        # as base but adding a unique hash at the end. Original
        # username is cut to avoid any field max_length.
        while storage.user.user_exists(username=final_username):
            username = short_username + uuid4().hex[:uuid_length]
            final_username = slug_func(clean_func(username[:max_length]))
    else:
        final_username = storage.user.get_username(user)
    return {'username': final_username}


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            return redirect('require_email')
#end require_email

@partial
def generate_profile(strategy, details, user, is_new=True, *args, **kwargs):
    """ generate a Trinity Force Network profile from the social information, if available """
    if not is_new:
        return
    else:
        profile = Profile.create(user.username)
        for name, value in details.items():
            if not hasattr(profile, name):
                continue
            current_value = getattr(profile, name, None)
            if not current_value or name not in protected:
                setattr(profile, name, value)
        try:
            profile.save()
        except:
            return redirect("profile", incomplete=True)
        else:
            return { 'profile': profile }
#end generate_profile