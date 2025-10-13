from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import User,Post

# --------------------------
# Home View
# --------------------------
def home(request):
    username = request.session.get('username')
    profile_img = None

    if username:
        try:
            user = User.objects.get(name=username)
            profile_img = user.img.url if user.img else '/static/default_profile.png'
        except User.DoesNotExist:
            username = None
            profile_img = None

    # Get 3 latest posts
    latest_posts = Post.objects.order_by('-date')[:3]

    return render(request, "home.html", {
        "username": username,
        "profile_img": profile_img,
        "latest_posts": latest_posts
    })

# --------------------------
# Register View
# --------------------------
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        desc = request.POST.get('desc', '')  # optional bio
        img = request.FILES.get('img')      # optional profile picture

        # Validations
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(name=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        # Create and save user
        user = User(name=username, email=email, desc=desc, img=img)
        user.set_password(password)  # hash password
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect('login')  # go to login page after registration

    return render(request, "register.html")


# --------------------------
# Login View
# --------------------------
def login(request):
    if request.method == "POST":
        username_input = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(name=username_input)
            if user.check_password(password):
                # Login successful: store username in session
                request.session['username'] = user.name
                messages.success(request, f"Welcome back, {user.name}!")
                return redirect('home')
            else:
                messages.error(request, "Incorrect password.")
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")

        # Login failed: show login page with empty username
        return render(request, "login.html", {"username": None})

    # GET request
    return render(request, "login.html", {"username": None})


# --------------------------
# Logout View
# --------------------------
def logout(request):
    # Clear session
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect('home')

def create(request):
    username = request.session.get('username')
    profile_img = None

    if username:
        try:
            user = User.objects.get(name=username)
            profile_img = user.img.url if user.img else '/static/default_profile.png'
        except User.DoesNotExist:
            username = None
            profile_img = None
    if not username:
        messages.error(request, "You must be logged in to create a post.")
        return redirect('login')

    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')  # this is the HTML from Quill
        image = request.FILES.get('image')

        # Get user object
        try:
            user = User.objects.get(name=username)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

        # Create post
        post = Post.objects.create(
            title=title,
            user=user,
            content=content,
            image=image
        )
        post.save()
        messages.success(request, "Post created successfully!")
        return redirect('home')

    # GET request
    return render(request, 'create.html',{"username": username,
        "profile_img": profile_img,})

def read(request, pk):
    username = request.session.get('username')
    profile_img = None

    if username:
        try:
            user = User.objects.get(name=username)
            profile_img = user.img.url if user.img else '/static/default_profile.png'
        except User.DoesNotExist:
            username = None
            profile_img = None
    post_obj = Post.objects.get(id=pk)
    return render(request, "post.html", {"post": post_obj,"username": username,
        "profile_img": profile_img,})

def posts(request):
    username = request.session.get('username')
    profile_img = None

    if username:
        try:
            user = User.objects.get(name=username)
            profile_img = user.img.url if user.img else '/static/default_profile.png'
        except User.DoesNotExist:
            username = None
            profile_img = None

    posts = Post.objects.order_by('-date')

    return render(request, "posts.html", {
        "username": username,
        "profile_img": profile_img,
        "posts": posts
    })
    
def profile(request):
    username = request.session.get('username')
    user = None
    posts = []

    if username:
        try:
            user = User.objects.get(name=username)
            posts = Post.objects.filter(user=user).order_by('-date')
        except User.DoesNotExist:
            username = None

    return render(request, "profile.html", {
        "username": username,
        "user": user,
        "posts": posts,
        "profile_img": user.img.url if user and user.img else '/static/default_profile.png',
    })

def edit(request, pk):
    username = request.session.get('username')
    profile_img = None

    if not username:
        return redirect('login')

    try:
        user = User.objects.get(name=username)
        profile_img = user.img.url if user.img else '/static/default_profile.png'
    except User.DoesNotExist:
        return redirect('login')

    post_obj = get_object_or_404(Post, id=pk, user=user)

    # Handle POST request (updating the post)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        post_obj.title = title
        post_obj.content = content
        if image:
            post_obj.image = image
        post_obj.save()

        return redirect(f'/post/{pk}')  # Redirect to the updated post page

    # Handle GET request (show form)
    return render(request, 'edit.html', {
        'username': username,
        'profile_img': profile_img,
        'post': post_obj
    })
    
def delete(request, pk):
    username = request.session.get('username')

    if not username:
        return redirect('login')

    # Get user object
    try:
        user = User.objects.get(name=username)
    except User.DoesNotExist:
        return redirect('login')

    # Get post or return 404
    post = get_object_or_404(Post, id=pk)

    # Ensure the logged-in user owns this post
    if post.user != user:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    # Delete the post immediately (no confirmation)
    post.delete()
    return redirect('profile')    