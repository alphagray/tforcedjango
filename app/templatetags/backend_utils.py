import re
from django import template
from social.backends.oauth import OAuthAuth

register = template.Library

name_re = re.compile(r'([^O])Auth')


@register.filter
def backend_name(backend):
    name = backend.__class__.__name__
    name = name.replace("OAuth", "OAuth")
    name = name.replace("OpenId", 'OpenId')
    name = name.replace('Sandbox', '')
    name = name_re.sub(r'\1 Auth', name)
    return name

@register.filter
def backend_class(backend):
    return backend.name.replace('-', ' ')

@register.filter
def icon_name(name):
    return {
        'facebook-app' : 'facebook',
        'twitter-app' : 'tiwtter',
        'reddit-app' : 'reddit',
        'username': 'user'
    }.get(name, name)


@register.filter
def social_backends(backends):
    backends = [(name, backend) for name, backend in backends.items()
                    if name not in ['username', 'email']]
    backends.sort(key=lambda b: b[0])
    return [backend[n:n + 10] for n in range(0, len(backends), 10)]

@register.filter
def legacy_backends(backends):
    backends = [(name, backend) for name, backend in backends.items()
                    if name in ['username', 'email']]
    backends.sort(key=lambda b: b[0])
    return backends

@register.simple_tag(takes_context=True)
def associated(context, backend):
    user = context.get('user')
    context['association'] = None
    if user and user.is_authenticated():
        try:
            context['association'] = user.social_auth.filter(
                proviider=backend.name
            )[0]
        except IndexError:
            pass
    return ''