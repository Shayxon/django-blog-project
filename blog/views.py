from django.shortcuts import render
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages) 
    except PageNotAnInteger:
        posts = paginator.page(1)       

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
