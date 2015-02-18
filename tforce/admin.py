from django.contrib import admin
from django.contrib.auth.models import User
from podcasting import models as podcasts
from podcasting import admin as pdadmin
import tforce.models as tf 


class ShowInline(admin.TabularInline):
    model = tf.ShowWrapper

class EpisodeInline(admin.TabularInline):
    model = tf.EpisodeWrapper

class ChoiceInline(admin.TabularInline):
    model = tf.Choice
    extra = 3
 
class ComboShow(pdadmin.ShowAdmin):
    inlines = [ShowInline]

class ComboEpisode(pdadmin.EpisodeAdmin):
    inlines = [EpisodeInline]


class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['question']
    date_hierarchy = 'pub_date'

class TForceUserInline(admin.StackedInline):
    model = tf.TForceUser

class UserAdmin(admin.ModelAdmin):
    inlines = [TForceUserInline]

admin.site.unregister(User)
admin.site.unregister(podcasts.Episode)
admin.site.unregister(podcasts.Show)
admin.site.register(podcasts.Episode, ComboEpisode)
admin.site.register(podcasts.Show, ComboShow)
admin.site.register(User, UserAdmin)
admin.site.register(tf.Poll, PollAdmin)
admin.site.register(tf.Channel)
admin.site.register(tf.ShowWrapper)
admin.site.register(tf.EpisodeWrapper)
admin.site.register(tf.Post)