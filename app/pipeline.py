from django.shortcuts import redirect
from app.models import Profile
from social.pipeline.partial import partial
from django.contrib.auth import login

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
        user.login()
        return redirect('home')
    elif is_new and not user.user_profile:
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
            return redirect("complete_profile")
        else:
            return { 'profile': profile }
#end generate_profile