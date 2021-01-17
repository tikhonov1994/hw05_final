from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


User = get_user_model()


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    post_count = post_list.count()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    followers = Follow.objects.filter(
        author__username=username
    ).count()
    followings = Follow.objects.filter(
        user__username=username
    ).count()
    context = {
        'page': page,
        'author': author,
        'paginator': paginator,
        'post_count': post_count,
        'following': False,
        'followers': followers,
        'followings': followings,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author, user=request.user
        ).exists()
        context.update({
            'following': following,
            'user': request.user,
        })
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    comments = Comment.objects.filter(post=post_id)
    author = User.objects.get(username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    count = Post.objects.filter(author=author).select_related('author').count()
    form = CommentForm(request.POST or None)
    followers = Follow.objects.filter(
        author__username=username
    ).count()
    followings = Follow.objects.filter(
        user__username=username
    ).count()
    context = {
        'post': post,
        'author': author,
        'count': count,
        'form': form,
        'comments': comments,
        'followers': followers,
        'followings': followings,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(
            'post',
            username=request.user.username,
            post_id=post_id
        )
    return render(
        request,
        'new_post.html',
        {'form': form, 'post': post, 'is_edit': True},
    )


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if request.GET or not form.is_valid():
        return render(request, 'comments.html', {'post': post, 'form': form})
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    authors_list = Follow.objects.filter(user=request.user).values_list('author')
    post_list = Post.objects.filter(author__in=authors_list)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(author=author, user=user).exists()
    if user != author and not following:
        follow = Follow.objects.create(
            user=user,
            author=author
        )
        follow.save()
    return redirect(reverse('profile', kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    unfollow = Follow.objects.select_related('user').filter(
            user=request.user,
            author__username=username
    )
    unfollow.delete()
    return redirect(reverse('profile', kwargs={'username': username}))
