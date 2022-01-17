from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    title = "Последние обновления на сайте"
    paginator = Paginator(post_list, settings.DEFAULT_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "title": title,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, settings.DEFAULT_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    title = group.title
    description = group.description
    context = {
        "page_obj": page_obj,
        "title": title,
        "description": description,
        "post_list": post_list,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    title = username
    post_all = Post.objects.filter(author=author).count()
    paginator = Paginator(post_list, settings.DEFAULT_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "post_all": post_all,
        "title": title,
        "author": author,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    author = post.author
    post_all = Post.objects.filter(author=author).count()
    context = {
        "post": post,
        "post_all": post_all,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user.username)
    return render(request, "posts/create_post.html", {"form": form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_edit = True
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:post_detail", pk)
    else:
        form = PostForm(instance=post)
    context = {"form": form, "is_edit": is_edit, "post": post}
    return render(request, "posts/create_post.html", context)
