from django.utils.translation import ugettext_lazy as _

from django.contrib import admin

try:
    from imagekit.admin import AdminThumbnail
except ImportError:
    AdminThumbnail = None

from app.forms import AdminShowForm, AdminEpisodeForm
from app.models import Content, Profile, Episode, Show
from app.utils.twitter import can_tweet


class ShowAdmin(admin.ModelAdmin):
    form = AdminShowForm
    list_display = ["title", "slug", "published_flag"]
    list_filter = ["title", "published"]
    if AdminThumbnail:
        list_display.append("admin_thumbnail")
        admin_thumbnail = AdminThumbnail(image_field="admin_thumb_sm")

    if can_tweet():
        fields.append("tweet_text")  # noqa

    def published_flag(self, obj):
        return bool(obj.published)
    published_flag.short_description = _("Published")
    published_flag.boolean = True

    def show_sites(self, obj):
        return ', '.join([site.name for site in obj.sites.all()])
    show_sites.short_description = "Sites"


class EpisodeAdmin(admin.ModelAdmin):
    form = AdminEpisodeForm
    list_display = ["title", "episode_shows", "slug", "episode_sites", "published_flag"]
    list_filter = ["shows", "published"]
    if AdminThumbnail:
        list_display.append("admin_thumbnail")
        admin_thumbnail = AdminThumbnail(image_field="admin_thumb_sm")

    if can_tweet():
        readonly_fields = ("tweet_text",)

    def published_flag(self, obj):
        return bool(obj.published)
    published_flag.short_description = _("Published")
    published_flag.boolean = True

    def episode_shows(self, obj):
        return ', '.join([show.title for show in obj.shows.all()])
    episode_shows.short_description = "Shows"

    def episode_sites(self, obj):
        sites = list()
        for show in obj.shows.all():
            for site in show.sites.all():
                if site not in sites:
                    sites.append(site)
        return ', '.join([site.name for site in sites])
    episode_sites.short_description = "Sites"

    def save_form(self, request, form, change):
        # this is done for explicitness that we want form.save to commit
        # form.save doesn't take a commit kwarg for this reason
        return form.save()


class EnclosureAdmin(admin.ModelAdmin):
    #form = AdminEnclosureForm

    list_display = ("mime", "url")
    list_filter = ("mime", "episodes")
    pass


class EmbedMediaAdmin(admin.ModelAdmin):
    pass

admin.site.register(Show, ShowAdmin)
admin.site.register(Episode, EpisodeAdmin)
