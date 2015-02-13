from django.contrib import admin
from django.contrib.auth.models import User
import tforce.models as tf 


class ChoiceInline(admin.TabularInline):
    model = tf.Choice
    extra = 3
    
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
admin.site.register(User, UserAdmin)
admin.site.register(tf.Poll, PollAdmin)
admin.site.register(tf.Channel)
admin.site.register(tf.Show)
admin.site.register(tf.Episode)
admin.site.register(tf.Post)