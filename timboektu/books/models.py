from django.db import models
from django.forms import ModelForm
 
class Department(models.Model):
    title = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.title
    
class Post(models.Model):
    title = models.CharField(max_length=1000)
    authors = models.TextField(blank=True)
    EDITION_CHOICES = (
        ('1', '1st'),
        ('2', '2nd'),
        ('3', '3rd'),
        ('4', '4th'),
        ('5', '5th'),
        ('6', '6th'),
        ('7', '7th'),
        ('8', '8th'),
        ('9', '9th'),
    )
    edition = models.CharField(max_length=2, choices=EDITION_CHOICES, blank=True)
    year = models.CharField(max_length=4, blank=True)
    isbn = models.CharField(max_length=13, blank=True) # http://djangosnippets.org/snippets/1994/
    courses = models.TextField(blank=True)
    description = models.TextField(blank=True)
    departments = models.ManyToManyField(Department, null=True, blank=True)
    #photo = models.ImageField(blank=True)
    crdate = models.DateTimeField(auto_now=True)
    mdate = models.DateTimeField(auto_now=True)
    hash = models.CharField(max_length=100, editable=False, blank=True)
    
    email = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-crdate']
    
    def __unicode__(self):
        return self.title
    
class PostForm(ModelForm):
    class Meta:
        model = Post
        
class PostManager(models.Manager):
    stop_list = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 
                 'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on',
                 'that', 'the', 'to', 'was', 'were', 'will', 'with']
    
    #TODO
    def order_by(self, *args, **kwargs):
        import sys
        sys.exit()
        return self.get_query_set().order_by(*args, **kwargs)
    
    def query(self, query):
        from django.db.models import Q
        import operator
        import re
        
        strings = []
        
        # Add quoted strings
        quoted = re.findall('".+?"', query)
        for s in quoted:
            strings.append(re.sub('"','',s))
        
        # Add unquoted terms
        unquoted = re.sub('".+?"', '', query)
        for s in unquoted.split(','):
            if s:
                strings += s.split(' ')
        
        # Remove common strings
        strings = filter(lambda s: s not in self.stop_list, strings)
        
        # Build and execute query
        posts = []
        if strings:
            ors = []
            for s in strings:
                ors.append(Q(title__icontains=s))
                ors.append(Q(description__icontains=s))
                ors.append(Q(authors__icontains=s))
                ors.append(Q(courses__icontains=s))
                ors.append(Q(isbn__icontains=s))
           
            posts = Post.objects.filter(reduce(operator.or_, ors))
    
        return posts
