from cmath import log
from hashlib import new
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import FollowersCount, LikePost, Profile, Post

from itertools import chain
import random


# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    feed = []
    user_following_list = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for influencer in user_following:
        user_following_list.append(influencer.user)  # Usernames

    for username in user_following_list:
        feed_lists = Post.objects.filter(user=username)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # User suggestions starts.
    all_users = list(User.objects.all())
    user_following_all = []

    for username in user_following_list:
        user_list = User.objects.get(username=username)
        user_following_all.append(user_list)

    all_users.remove(user_object) # Removing self from suggestions.

    new_suggestion_list = [x for x in all_users if (x not in user_following_all)]    
    random.shuffle(new_suggestion_list)

    username_profile = []
    username_profile_list = []

    for users in new_suggestion_list:
        username_profile.append(users.id)

    for id in username_profile:
        profile_lists = Profile.objects.filter(id_user=id)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    
    return render(request, 'index.html', {'user_profile':user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]} )

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists!')
                return redirect('signup')
            
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken :(, please select another')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Log the user in and redirect to settings page.
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #Create a profile object for the new user.
                user_current = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_current, id_user=user_current.id)
                new_profile.save()
                return redirect('signup')
        else:
            messages.info(request, 'passwords do not Match')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')
    
@login_required(login_url='signin')    
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('profile/'+user)
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)


    if request.method == 'POST':
        username = request.POST['username']
        username_list = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for user in username_list:
            username_profile.append(user.id)
            # username_profile = Profile.objects.get(username=user.username)

        for id in username_profile:
            profile_lists = Profile.objects.filter(id_user=id)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list':username_profile_list})

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object.username)
    user_post_count = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow User'
    else:
        button_text = 'Follow'

    follower_count = FollowersCount.objects.filter(user=user).count()
    following_count = FollowersCount.objects.filter(follower=user).count()

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts_count': user_post_count,
        'user_posts': user_posts,
        'button_text': button_text,
        'follower_count': follower_count,
        'following_count': following_count
    }
     
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.like_count = post.like_count + 1
        post.save()

    else:
        # LikePost.objects.delete(post_id=post_id, username=username)
        like_filter.delete()
        post.like_count = post.like_count - 1
        post.save()
    
    return redirect('/')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = user_profile.profileimg
        
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')

        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
    
        return redirect('settings')
        
    return render(request, 'setting.html', {'user_profile':user_profile})