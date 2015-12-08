from django.db import models
from website.fields import ThumbnailImageField


class Publication(models.Model):
    image_file = ThumbnailImageField(upload_to='documents')
    user = models.ForeignKey('auth.User', related_name='publications')
    created = models.DateTimeField(auto_now_add=True)

    def delete(self, using=None):
        self.image_file.delete(save=False)
        super(Publication, self).delete(using=using)


class Follower(models.Model):
    user = models.ForeignKey('auth.User', related_name='following')
    following = models.ForeignKey('auth.User', related_name='followers')
    created = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    UNDEFINED = 0
    NEGATIVE = 1
    POSITIVE = 2
    POLARITIES = (
        (UNDEFINED, "UNDEFINED"),
        (NEGATIVE, "NEGATIVE"),
        (POSITIVE, "POSITIVE")
    )

    user = models.ForeignKey('auth.User', related_name='comments')
    publication = models.ForeignKey(Publication, related_name='comments')
    text = models.CharField(max_length=512)
    created = models.DateTimeField(auto_now_add=True)
    polarity = models.IntegerField(choices=POLARITIES, default=UNDEFINED)


class RunningTask(models.Model):
    user = models.ForeignKey('auth.User', related_name='tasks')
    running_id = models.CharField(max_length=36)