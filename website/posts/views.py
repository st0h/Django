from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, get_user_model, logout

from .models import Post, Comment
from .forms import PasswordResetForm, CreatePostForm, CommentForm, LoginForm

import markdown as md

def index(request):
	"""
		Display a list of the latest 10 posts, sorted by date in descending order.
	"""
	posts = Post.objects.order_by("-pub_date")
	# Display 10 posts per page.
	paginator = Paginator(posts, 10)
	page_number = request.GET.get("page")
	page_obj = paginator.get_page(page_number)
	return render(request, "posts/index.html", {"page_obj": page_obj})

def about(request):
    """
        Display an "about" page with a brief description of the site.
    """
    return render(request, "posts/about.html")

def tos(request):
    """
        Display the privacy policy and terms of service.
    """
    return render(request,"posts/tos.html")

def create(request):
	"""
		Display the form for creating a new post. If a new post has been received, store
		it in the database and display a message to the user upon a successful save.
	"""
	if (request.method == "POST"):
		form = CreatePostForm(request.POST)
		# This action should only be available to active, authenticated accounts.
		if (not request.user.is_authenticated or not request.user.is_active):
			messages.error(request,"You must be signed in to create posts!")
			return redirect("posts:login_view")
		# Check that the user has the appropriate permissions!
		if (not request.user.has_perm("posts.add_post")):
			messages.error(request,"You do not have permission to post messages!")
			return redirect("posts:index")
		# If the test cookie is successfully set, clean it up. Otherwise, we cannot proceed!
		if request.session.test_cookie_worked():
			request.session.delete_test_cookie()
			# Set a session variable for the user's per-session post count.
			request.session['num_posts'] = request.session.get('num_posts', 0)
		else:
			messages.error(request, "You must have cookies enabled to post. Please check your browser settings and try again!")
			request.session.set_test_cookie()
			return render(request, "posts/create.html", {"form":form})
		# Limit the user to 100 posts per session.
		if request.session['num_posts'] >= 100:
			messages.error(request, "You have posted too many times (100) during this session! Please try again later.")
			request.session.set_test_cookie()
			return render(request, "posts/create.html", {"form":form})
		# Validate the provided form data before proceeding.
		if (form.is_valid()):
			title = form.cleaned_data['title']
			body = md.markdown(form.cleaned_data['message'])
			author = request.user
			pub_date = timezone.now()
			post = Post.objects.create(title=title,body=body,pub_date=pub_date,author=author)
			post.save()
			# Increment the user's per-session post count.
			request.session['num_posts'] += 1 
			messages.success(request, "Your post was saved successfully!")
			return redirect("posts:index")
		else:
			messages.error(request,"There was a problem saving your post. Please check your input and try again!")
			request.session.set_test_cookie()
			return render(request, "posts/create.html", {"form":form})
	else:
		# Create an instance of the form to pass to our template.
		form = CreatePostForm()
		request.session.set_test_cookie()
		# This action should only be available to active, authenticated accounts.
		if (not request.user.is_authenticated or not request.user.is_active):
			messages.error(request,"You must be signed in to create posts!")
			return redirect("posts:login_view")
		# Check that the user has the appropriate permissions!
		if (not request.user.has_perm("posts.add_post")):
			messages.error(request,"You do not have permission to post messages!")
			return redirect("posts:index")
		# Display the form.
		return render(request, "posts/create.html", {"form":form})

def view(request,post_id):
	"""
		View the full contents of an individual post.
	"""
	post = get_object_or_404(Post,pk=post_id)
	# Sort the comments in ascending order (i.e. oldest first).
	comments = Comment.objects.filter(post__id=post_id).order_by("pub_date")
	# Count the total number of comments for this post.
	comment_count = Comment.objects.filter(post__id=post_id).count()
	# Display 100 comments per page.
	paginator = Paginator(comments,100)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context = {
		"post":post,
		"page_obj":page_obj,
		"comment_count":comment_count,
	}
	return render(request,"posts/view.html",context)

def comment(request, post_id):
    """
        Display the form for commenting on a specific post. If a new comment has
        been received, process it and store it in the database.
    """
    # First, find the post that we're commenting on!
    post = get_object_or_404(Post,pk=post_id) 
    if (request.method == "POST"):
        # Create an instance of the appropriate form.
        form = CommentForm(request.POST)
        context = {
            "post_id":post_id,
            "post":post,
            "form":form,
        }
        # Only authenticated users with the appropriate permission can post comments!
        if (not request.user.is_active or not request.user.is_authenticated): 
            messages.error(request, "You must be signed in to post comments!")
            return redirect("posts:login_view")
        if (not request.user.has_perm("posts.add_comment")):
            messages.error(request, "You do not have permission to post comments!")
            return redirect("posts:index")
        # If the test cookie is successfully set, clean it up. Otherwise, we cannot proceed!
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            # Set a session variable for the user's per-session comment count.
            request.session['num_comments'] = request.session.get('num_comments', 0)
        else:
            messages.error(request, "You must have cookies enabled to post comments. Please check your browser settings and try again!")
            request.session.set_test_cookie()
            return render(request, "posts/comment.html", context)
        # Limit the user to 1000 comments per session.
        if request.session['num_comments'] >= 1000:
            messages.error(request, "You have commented too many times (1000) during this session! Please try again later.")
            request.session.set_test_cookie()
            return render(request, "posts/comment.html", context)
        # Validate the provided form data before proceeding.
        if (form.is_valid()):    
            body = form.cleaned_data['message']
            author = request.user
            pub_date = timezone.now()  
            comment = Comment.objects.create(body=body,pub_date=pub_date,post_id=post_id,author=author)
            comment.save()
            request.session['num_comments'] += 1
            messages.success(request,"Your comment has been saved successfully!")
            return redirect("posts:view", post_id=post_id)
        else:
            messages.error(request, "There was a problem submitting your comment. Please check your input and try again!")
            form = CommentForm()
            return render(request, "posts/comment.html", context)
    else:
        # Only authenticated users with the appropriate permission can post comments!
        if (not request.user.is_active or not request.user.is_authenticated): 
            messages.error(request, "You must be signed in to post comments!")
            return redirect("posts:login_view")
        if (not request.user.has_perm("posts.add_comment")):
            messages.error(request, "You do not have permission to post comments!")
            return redirect("posts:index")
        request.session.set_test_cookie()
        # Display the appropriate form.
        form = CommentForm()
        context = {
            "post_id":post_id,
            "post":post,
            "form":form,
        }
        return render(request, "posts/comment.html", context)
       
def edit(request, post_id):
	"""
		Edit the content of an individual post. Optionally delete or update the content of the post,
		depending upon the button clicked.
	""" 
	# Check to see if the post exists first!
	post = get_object_or_404(Post, pk=post_id)
	if (request.method == "POST"):
		if (request.POST['submit'] == "Delete this post!"):
			# Check to see if the user has permission to delete posts first!
			if (not request.user.is_authenticated or not request.user.is_active):
				messages.error(request,"You must be signed in to delete posts!")
				return redirect("posts:login_view")
			if (not request.user.has_perm("posts.delete_post")):
				messages.error(request,"You do not have permission to delete posts!")
				return redirect("posts:view", post_id=post_id)
			# Posts can only be deleted by their owner!
			if (not request.user == post.author):
				messages.error(request,"You can only delete your own posts!")
				return redirect("posts:view", post_id=post_id)
			post.delete()
			messages.success(request, "Post deleted: " + post.title.title())
			return redirect("posts:index")
		else:
			# Validate the provided form data before proceeding.
			form = CreatePostForm(request.POST)
			if (form.is_valid()):
				# Check to see if the user has permission to change posts first!
				if (not request.user.is_authenticated or not request.user.is_active):
					messages.error(request,"You must be signed in to edit posts!")
					return redirect("posts:login_view")
				if (not request.user.has_perm("posts.delete_post")):
					messages.error(request,"You do not have permission to edit posts!")
					return redirect("posts:view", post_id=post_id)
				# Posts can only be changed by their owner!
				if (not request.user == post.author):
					messages.error(request,"You can only edit your own posts!")
					return redirect("posts:view", post_id=post_id)
				post.title = form.cleaned_data['title']
				post.body = md.markdown(form.cleaned_data['message'])
				# Since we're updating the post, we'll "refresh" the publication date too.
				post.pub_date = timezone.now()
				# Save our changes and display the updated post!
				post.save()
				messages.success(request, "Your changes have been saved successfully!")
				return redirect("posts:view", post_id)
			else:
				messages.error(request,"There was a problem modifying this post. Please check your input and try again!")
				# Display the appropriate form.
				form = CreatePostForm(request.POST)
				context = {
					"post_id":post_id,
					"post":post,
					"form":form,
				}
				return render(request, "posts/edit.html", context)
	else:
		# Check to see if the user has permission to change posts first!
		if (not request.user.is_authenticated or not request.user.is_active):
			messages.error(request,"You must be signed in to edit posts!")
			return redirect("posts:login_view")
		if (not request.user.has_perm("posts.delete_post")):
			messages.error(request,"You do not have permission to edit posts!")
			return redirect("posts:view", post_id=post_id)
		# Posts can only be changed by their owner!
		if (not request.user == post.author):
			messages.error(request,"You can only change your own posts!")
			return redirect("posts:view", post_id=post_id)
		# Display the appropriate form.
		form = CreatePostForm(initial={"title":post.title.title,"message":post.body})
		context = {
			"post_id":post_id,
			"post":post,
			"form":form,
		}
		return render(request, "posts/edit.html", context)
    
def delete_comment(request,comment_id,post_id):
	"""
		Delete a comment.
	"""
	# First, make sure that the comment exists!
	comment = get_object_or_404(Comment, pk=comment_id)
	# Now grab the post to which it belongs as well.
	post = get_object_or_404(Post, pk=post_id)
	# This action should only be available to authenticated users with the appropriate permissions.
	if (not request.user.is_authenticated or not request.user.is_active):
		messages.error(request,"You must be signed in to delete comments!")
		return redirect("posts:login_view")
	# Check that the user has permission to delete comments!
	if (not request.user.has_perm("posts.delete_comment")):
		messages.error(request, "You do not have permission to delete comments!")
		return redirect("posts:view",post_id=post_id)
	# A comment can be deleted if it belongs to the user, or if the parent post belongs to them.
	if (request.user == comment.author or request.user == post.author):
		# Okay, let's delete the comment!
		comment.delete()
		messages.success(request,"Comment deleted!")
		return redirect("posts:view", post_id=post_id)
	else:
		messages.error(request,"You do not have permission to delete this comment!")
		return redirect("posts:view", post_id=post_id)
    
def view_user(request,user_id):
	"""
		View the records of an individual user.
	"""
	# Determine what User model Django is using, then fetch the record for the indicated
	# user with that model.
	User = get_user_model()
	user_record = get_object_or_404(User,pk=user_id)
	# Get the most recent 5 posts by the user above.
	posts = Post.objects.filter(author=user_id).order_by("-pub_date")[:5]
	# Get the user's total post and comment counts.
	post_count = Post.objects.filter(author=user_id).count()
	comment_count = Comment.objects.filter(author=user_id).count()
	context = {
		"post_count":post_count,
		"comment_count":comment_count,
		"user":user_record,
		"posts":posts,  
	}
	return render(request,"posts/view_user.html",context)

def login_view(request):
	"""
		Display the login form. Alternatively, if a user is attempting to login, process
		the data from the form and attempt to authenticate the user.
	"""
	# If the user is already authenticated, let them know and return to the index!
	if (request.user.is_authenticated):
		messages.error(request,"You are already signed in!")
		return redirect("posts:index")
	if (request.method == "POST"):
		# If the test cookie is successfully set, clean it up. Otherwise, we cannot proceed!
		if request.session.test_cookie_worked():
			request.session.delete_test_cookie()
			# Set a session variable for the number of attempted logins.
			request.session['login_attempts'] = request.session.get('login_attempts', 0)
		else:
			messages.error(request, "You must have cookies enabled to proceed. Please check your browser settings and try again!")
			request.session.set_test_cookie()
			return redirect("posts:login_view")
		# If there have been too many incorrect login attempts, don't proceed any further!
		if request.session['login_attempts'] >= 3:
			messages.error(request, "You have attempted to sign in too many times (3)! Please try again later.")
			request.session.set_test_cookie()
			return redirect("posts:login_view")
		# Validate the provided form data before proceeding.
		form = LoginForm(request.POST)
		if form.is_valid():
			# Grab the username and password from the form.
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(request, username=username, password=password)
			if user is not None:
				# We found a user record matching the provided information, sign them in!
				login(request,user)
				messages.success(request,"You have signed in successfully!")
				return redirect("posts:index")
			else:
				# A matching username/password combination could not be found!
				messages.error(request, "Username or password incorrect!")
				request.session.set_test_cookie()
                # There was a failed attempt to login, record it!
				request.session['login_attempts'] += 1
				return redirect("posts:login_view")
		else:
			messages.error(request, "There was a problem signing you in. Please check your input and try again!")
			request.session.set_test_cookie()
			return redirect("posts:login_view")
	else:
		# Display the appropriate form.
		form = LoginForm()
		request.session.set_test_cookie()
		return render(request,"posts/login.html", {"form":form})
    
def logout_view(request):
	"""
		Sign a user out from the site!
	"""
	# Check to see if the current user is authenticated.
	if (not request.user.is_authenticated):
		messages.error(request, "You are not signed in!")
		return redirect("posts:login_view")
	# Okay, they're authenticated. Sign them out!
	logout(request)
	messages.success(request, "You have signed out successfully!")
	return redirect("posts:index")

def view_user_by_username(request,username):
	"""
		Find and display a user's records (if they exist), searching for the appropriate
		record by username.
	"""
	# Determine what User model Django is using, then fetch the record for the indicated
	# user with that model.
	User = get_user_model()
	user_record = get_object_or_404(User,username=username)
	# We'll grab the user's database ID from the record, then pass it along to the normal
	# template for viewing user accounts.
	user_id = user_record.pk
	# Get the most recent 5 posts by the user above.
	posts = Post.objects.filter(author=user_id).order_by("-pub_date")[:5]
	# Get the user's total post and comment counts.
	post_count = Post.objects.filter(author=user_id).count()
	comment_count = Comment.objects.filter(author=user_id).count()
	context = {
		"post_count":post_count,
		"comment_count":comment_count,
		"user":user_record,
		"posts":posts,  
	}
	return render(request,"posts/view_user.html",context)
    
def reset_password(request):
	"""
		Allows a user to reset their password.
	"""
	if (request.method == "POST"):
		# This should only be available to authenticated users!
		if (not request.user.is_authenticated or not request.user.is_active):
			messages.error(request,"You must be signed in to change your password!")
			return redirect("posts:login_view")
		# Validate the provided form data before proceeding.
		form = PasswordResetForm(request.POST)
		if (form.is_valid()):
			# Determine what User model Django is using, then fetch the record for the indicated
			# user with that model.
			User = get_user_model()
			# Find the account associated with the user requesting the reset.
			user_record = get_object_or_404(User,pk=request.user.id)
			password1 = form.cleaned_data["password1"]
			password2 = form.cleaned_data["password2"]
			# Do the values grabbed from the form match?
			if (not password1 == password2):
				messages.error(request,"The password values entered do not match. Please try again!")
				return redirect('posts:reset_password')
			# Passwords should be a minimum of 8 characters!
			if (not len(password1) >= 8):
				messages.error(request, "Passwords must be a minimum of 8 characters!")
				return redirect('posts:reset_password')
			else:
				user_record.set_password(password1)
				user_record.save()
				messages.success(request,"You have successfully changed your password. Please sign in again using the new password you have chosen!")
				return redirect("posts:login_view")
		else:
			messages.error(request,"There was a problem modifying your password. Please check your input and try again!")
			return redirect('posts:reset_password')
	else:
		# This should only be available to authenticated users!
		if (not request.user.is_authenticated or not request.user.is_active):
			messages.error(request,"You must be signed in to change your password!")
			return redirect("posts:login_view")
		# Display the appropriate form.
		form = PasswordResetForm()
		return render(request,"posts/reset_password.html", {"form":form})
