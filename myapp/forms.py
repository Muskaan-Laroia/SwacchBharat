from django import forms
from models import UserModel, PostModel, LikeModel, CommentModel

#forms help in creating the structure of the pages
class SignUpForm(forms.ModelForm): #form for the sign up page
    class Meta:
        model = UserModel
        fields=['email','name','username','password']

class LoginForm(forms.ModelForm): #form for the login page
    class Meta:
        model = UserModel
        fields = ['username', 'password']

class PostForm(forms.ModelForm): #form for the feed page
    class Meta:
        model = PostModel
        fields=['image', 'caption']


class LikeForm(forms.ModelForm): #form for liking the post

    class Meta:
        model = LikeModel
        fields=['post']


class CommentForm(forms.ModelForm): #form for commenting on the posts

    class Meta:
        model = CommentModel
        fields = ['comment_text', 'post']