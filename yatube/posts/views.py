from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Follow, Group, Post
from yatube.settings import POSTS_ON_PAGE

User = get_user_model()


def paginator(request, items, count=POSTS_ON_PAGE):
    """
    Пагинатор количества элементов на странице.Функция принимает на вход
    request, кверисет и количество элементов на странице. Количество
    элементов на странице по умолчанию задается в настройках.
    """

    paginator = Paginator(items, count)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    """Функция возвращает данные для главной страницы"""

    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = paginator(request=request, items=posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request=request, template_name=template, context=context)


def group_posts(request, slug):
    """Функция возвращает данные для страницы группы"""

    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request=request, items=posts)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request=request, template_name=template, context=context)


def profile(request, username):
    """Функция возвращает данные для страницы профиля пользователя"""

    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(author=author).exists()
    is_author = author != request.user
    posts = author.posts.all()
    page_obj = paginator(request=request, items=posts)
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
        'is_author': is_author,
    }
    return render(request=request, template_name=template, context=context)


def post_detail(request, post_id):
    """Функция возвращает данные страницы детальной информации о публикации"""

    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    count = post.author.posts.count()
    is_author = post.author == request.user
    comments = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'count': count,
        'is_author': is_author,
        'comments': comments,
        'form': form,
    }
    return render(request=request, template_name=template, context=context)


@login_required
def post_create(request):
    """Функция создает новую запись поста"""

    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    context = {'form': form}
    return render(request=request, template_name=template, context=context)


@login_required
def post_edit(request, post_id=None):
    """Функция редактирования поста"""

    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'is_edit': True, 'post': post}
    return render(request=request, template_name=template, context=context)


@login_required
def add_comment(request, post_id):
    """Функция добавления комментария к посту"""

    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """
    Функция отображает список записей только тех авторов, на которых
    подписался пользователь
    """

    template = 'posts/follow.html'
    following_authors = Follow.objects.filter(user=request.user).values_list(
        'author_id', flat=True)
    posts = Post.objects.filter(author_id__in=list(following_authors))
    page_obj = paginator(request=request, items=posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request=request, template_name=template, context=context)


@login_required
def profile_follow(request, username):
    """Функция подписывает пользователя на посты автора"""

    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    """Функция отписывает пользователя на посты автора"""

    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(author=author).delete()
    return redirect('posts:profile', author)
