from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['author', 'publish', 'created', 'status']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'email', 'created', 'active']
    list_filter = ['created', 'active', 'post']
    date_hierarchy = 'created'
    search_fields = ['post', 'name']
    raw_id_fields = ['post']
    ordering = ['active', 'created']