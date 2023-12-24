from django import forms

class PasswordResetForm(forms.Form):
	password1 = forms.CharField(label="Enter your new password here (255 characters maximum)", max_length=255,required=True,widget=forms.PasswordInput)
	password2 = forms.CharField(label="Password (confirm)", max_length=255, required=True,widget=forms.PasswordInput)

class CreatePostForm(forms.Form):
	title = forms.CharField(label="Title (100 characters maximum)",max_length=100,required=True)
	message = forms.CharField(label="Enter your message here (25,000 characters maximum)",max_length=25000,required=True,widget=forms.Textarea)

class CommentForm(forms.Form):
	message = forms.CharField(label="Enter your comment here (1,000 characters maximum)", max_length=1000, required=True,widget=forms.Textarea)

class LoginForm(forms.Form):
	username = forms.CharField(label="Username", max_length=150, required=True)
	password = forms.CharField(label="Password", max_length=255, required=True,widget=forms.PasswordInput)
