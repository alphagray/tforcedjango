from app.models import Content

def get_subclasses(cls):
    result = [cls]
    classes_to_inspect = [cls]
    while classes_to_inspect:
        class_to_inspect = classes_to_inspect.pop()
        for sublcass in class_to_inspect.__subclasses__():
            if subclass not in result:
                result.append(subclass)
                classes_to_inspect.append(sublcass)
    return result


def post_to_reddit_on_save(sender, instance, **kwargs):
    if instance.published:
        # this argument will create a reddit 
        pass
    pass


def update_feeds_on_save(sender, instance, **kwargs):
    if instance.published:
        #if this object is published, then I need to get
        #all the channels it's attached to
        #from those channels, I have to find all the content container objects
        #that it might be contained in. In other words, if it's a blog post
        #that's only pinging against a specific channel instead of one of its parent blogs
        #then that's fine, but I need to know those channel. Likewise, if for whatever reason,
        #the channel didn't get set but a bunch of blogs or shows are added, I need to know that too. 
        #so basically, I need to know the name and type of the parent object. 
        # so, first, try to get the channels from the instance
        channel_ids = [item.get('id') for item in instance.channels.values('id')]
        feeds = []
        # then get the parents objs
        if hasattr(instance, 'parents'):
            for parent in instance.parents.exclude(channels__exact=None):
                pass
            pass
        else:
            pass
        pass
    pass



for subclass in get_subclasses(Content):
    post_save.connect(update_feeds_on_save, subclass)