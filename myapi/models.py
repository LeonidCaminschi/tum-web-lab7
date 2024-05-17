from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500)
    movie_url = models.URLField(max_length=500)

    def __str__(self):
        return self.title