import django.apps

class Config(django.apps.AppConfig):
    name = 'app'
    def read(self):
        import app.singals