from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.simple_tag
def total_posts():
    count = Post.published.all().count()
    return f"I have posted {count} posts so far!"

@register.inclusion_tag('blog/post/includes/latest_posts.html')
def get_latest_posts(count=3):
    posts = Post.published.all().order_by('-publish')[:count]
    return {'posts':posts}

@register.inclusion_tag('blog/post/includes/latest_posts.html')
def get_most_commented_posts(count=5):
    posts = Post.published.all().annotate(comment = Count('comments')) \
                                    .order_by('-comment')[:count]
    return {'posts':posts}

@register.filter(name='markdown')
def markdownFilter(text):
    return mark_safe(markdown.markdown(text))