from django.db import models
from time import mktime
import datetime, feedparser

# Create your models here.
class Feed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(unique=True, help_text="Don't forget to add http:// or https:// to the URL")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        feed_data = feedparser.parse(self.url)
        
        # Set some fields
        self.title = feed_data.feed.title
            
        super(Feed, self).save(*args, **kwargs)
        
        for entry in feed_data.entries:
            article = Article()
            article.title = entry.title
            article.url = entry.link
            article.description = entry.description
        
            # Set publication date
            try:
                published = entry.published_parsed
            except AttributeError:
                try:
                    published = entry.updated_parsed
                except AttributeError:
                    published = entry.created_parsed
                    
            publication_date = datetime.datetime.fromtimestamp(mktime(published))
            date_string = publication_date.strftime('%Y-%m-%d %H:%M:%S')
            article.publication_date = date_string
        
            article.feed = self
            article.save()
    
class Article(models.Model):
    feed = models.ForeignKey(Feed, blank=True, null=True)
    title = models.CharField(max_length=200)
    url = models.URLField(verbose_name="URL")
    description = models.TextField()
    publication_date = models.DateTimeField()
    
    def __str__(self):
        return self.title