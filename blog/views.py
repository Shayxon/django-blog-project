from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

def post_share(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = Post.Status.PUBLISHED)
    sent = False
    
    if request.method == 'POST':

        form = EmailPostForm(request.POST)

        if form.is_valid():

            cd = form.cleaned_data

            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"Hi! my name is {cd['name']}. I recommend you to read {post.title}"
            comments = f"read {post.title} at {post_url}\n\n my comment: {cd['comment']}"

            send_mail(subject, comments, cd['email'], [cd['to']], fail_silently=False)

            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

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
    
    form = CommentForm()

    comments = post.comments.filter(active=True)

    return render(
        request,
        'blog/post/detail.html',
        {'post': post,
         'comments': comments,
         'form': form}
    )

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id = post_id, status = Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)

    if form.is_valid():

        comment = form.save(commit=False)

        comment.post = post

        comment.save()

    return render(request, 'blog/post/comment.html', {'form':form, 'post':post, 'comment': comment})    