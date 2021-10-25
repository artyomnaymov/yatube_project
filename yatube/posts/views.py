from django.shortcuts import render, get_object_or_404

from posts.models import Post, Group


def index(request):
    """Функция возвращает данные для главной страницы"""

    template = 'posts/index.html'
    posts = Post.objects.all()[:10]
    context = {
        'posts': posts
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Функция возвращает данные для страницы группы"""

    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:10]
    context = {
        'posts': posts,
        'group': group,
    }
    return render(request, template, context)
