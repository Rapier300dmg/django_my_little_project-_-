from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Post, Comment, Notification, Profile 
from .forms import LoginForm, UserRegistrationForm, PostForm, CommentForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.conf import settings


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
           
            return redirect('forum:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'forum/register.html', {'form': form})


def home(request):
    posts = Post.objects.all()
    
    if request.method == 'POST':
        comment_content = request.POST.get('comment')
        post_id = request.POST.get('post_id')

        if comment_content and post_id:
            post = get_object_or_404(Post, id=post_id)
            comment = Comment(content=comment_content, post=post, author=request.user)
            comment.save()
            Notification.objects.create(user=post.author, comment=comment)
            return redirect('forum:home')

    return render(request, 'forum/home.html', {'posts': posts})


def my_posts(request):
    posts = Post.objects.filter(author=request.user)
    return render(request, 'forum/my_posts.html', {'posts': posts})

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('forum:home')
    else:
        form = PostForm()
    return render(request, 'forum/create_post.html', {'form': form})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            Notification.objects.create(user=post.author, comment=comment)
            return redirect('forum:post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'forum/post_detail.html', {'post': post, 'comments': comments, 'form': form})

def profile(request):
    return render(request, 'forum/profile.html', {'user': request.user})

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.user == post.author:
        post.delete()
    
    return redirect('forum:home')

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('forum:profile')  
        else:
            print(form.errors)  

    else:
        form = ProfileForm(instance=profile)

    return render(request, 'forum/edit_profile.html', {'form': form})

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.author:
        comment.delete()
    
    return redirect('forum:home')