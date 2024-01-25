from django.shortcuts import render
from .models import Post

def post_list(request):
    posts = Post.published.all()

    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}
    )

def post_detail(request, year, month, day, post):
    try:
        post = Post.published.get(publish__year = year, publish__month = month, publish__day = day, slug = post)
    except Post.DoesNotExist:
        raise 'No Post found.'

    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )
