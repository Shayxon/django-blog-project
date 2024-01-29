from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity

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

def post_list(request, tag_slug=None):
    post_list = Post.published.all()

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tag__in = [tag])

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
        {'posts': posts, 'tag':tag}
    )

def post_detail(request, year, month, day, post):
    try:
        post = Post.published.get(publish__year = year, publish__month = month, publish__day = day, slug = post)
    except Post.DoesNotExist:
        raise 'No Post found.'
    
    form = CommentForm()

    comments = post.comments.filter(active=True)

    post_tags_ids = post.tag.values_list('id', flat=True)
    similar_posts = Post.published.filter(tag__in = post_tags_ids) \
                                .exclude(id = post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tag')) \
                                .order_by('-same_tags', '-publish')[:4]
    
    return render(
        request,
        'blog/post/detail.html',
        {'post': post,
         'comments': comments,
         'form': form,
         'similar_posts': similar_posts}
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

def post_search(request):
    
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:

        form = SearchForm(request.GET)
        
        if form.is_valid():

            query = form.cleaned_data['query']

            results = Post.published.annotate(
                similarity = TrigramSimilarity('title', query)
            ).filter(similarity__gt = 0.1).order_by('-similarity')

    return render(request, 'blog/post/search.html', {'results': results, 'query': query, 'form': form})
