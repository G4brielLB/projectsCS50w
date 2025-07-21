from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import User
from .models import Post
import json


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    liked_posts = set()
    if request.user.is_authenticated:
        liked_posts = set(Post.objects.filter(likes=request.user).values_list('id', flat=True))

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "liked_posts": liked_posts
    })



@login_required
def following(request):
    user = request.user
    posts = Post.objects.filter(user__in=user.following.all()).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    liked_posts = set()
    if request.user.is_authenticated:
        liked_posts = set(Post.objects.filter(likes=request.user).values_list('id', flat=True))

    return render(request, "network/following.html", {
        "page_obj": page_obj,
        "liked_posts": liked_posts
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    

@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        post = Post(user=request.user, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/new_post.html")
    
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if user is the owner of the post
    if request.user != post.user:
        return JsonResponse({"success": False, "error": "You can only edit your own posts"}, status=403)
    
    if request.method == "POST":
        try:
            # For AJAX requests with JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                post.content = data.get('content')
                post.save()
                return JsonResponse({"success": True, "content": post.content})
            # For traditional form submissions
            else:
                post.content = request.POST.get("content", "")
                post.save()
                return HttpResponseRedirect(reverse("index"))
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    
def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(user=user).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    is_following = False
    if request.user.is_authenticated:
        is_following = request.user in user.followers.all()
    
    return render(request, "network/profile.html", {
        "page_obj": page_obj,
        "profile_user": user,
        "is_following": is_following
    })


# API Views
@login_required
def like(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        liked = False

        if user in post.likes.all():
            post.likes.remove(user)
        else:
            post.likes.add(user)
            liked = True  

        return JsonResponse({"success": True, "likes_count": post.likes.count(), "liked": liked})

    return JsonResponse({"success": False})



@login_required
def follow(request, username):
    user = request.user
    follow_user = get_object_or_404(User, username=username)
    
    if user in follow_user.followers.all():
        follow_user.followers.remove(user)
        is_following = False
    else:
        follow_user.followers.add(user)
        is_following = True

    return JsonResponse({
        "success": True,
        "is_following": is_following,
        "followers_count": follow_user.followers.count()
    })

    


