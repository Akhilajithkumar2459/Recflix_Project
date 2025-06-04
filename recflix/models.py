from django.db import models
from django.contrib.auth.models import User

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class PlaylistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20)  # 'movies', 'anime', or 'webseries'
    poster = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'title', 'category')

    def __str__(self):
        return f"{self.user.username}'s {self.category}: {self.title}"

class PopularItem(models.Model):
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20)  # 'movies', 'anime', 'webseries', 'books', 'games'
    poster = models.CharField(max_length=255)
    count = models.IntegerField(default=1)  # Number of times added to playlist
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('title', 'category')
        ordering = ['-count', '-last_updated']

    def __str__(self):
        return f"{self.title} ({self.category}) - {self.count} times"
