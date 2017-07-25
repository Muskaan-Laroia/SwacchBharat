# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#models help in creating the database to store values
# Create your models here.
from django.db import models

import uuid

#Create your models here.

#this model is for the sign up page and also used the same model in login page
class UserModel(models.Model):
	email = models.EmailField()
	name = models.CharField(max_length=120)
	username = models.CharField(max_length=120)
	password = models.CharField(max_length=40)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

class SessionToken(models.Model): #this model is used for logging in and logging out functiionality
	user = models.ForeignKey(UserModel)
	session_token = models.CharField(max_length=255)
	last_request_on = models.DateTimeField(auto_now=True)
	created_on = models.DateTimeField(auto_now_add=True)
	is_valid = models.BooleanField(default=True)

# this lets the user be logged in untill he logs out and his session gets over
	def create_token(self):
		self.session_token = uuid.uuid4()

#this is for the feed page for posting pictures by the user
class PostModel(models.Model):
	user = models.ForeignKey(UserModel)
	image = models.FileField(upload_to='user_images')
	image_url = models.CharField(max_length=255)
	caption = models.CharField(max_length=240)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	has_liked = False


	@property
	def like_count(self):
		return len(LikeModel.objects.filter(post=self))

	@property
	def comments(self):
		return CommentModel.objects.filter(post=self).order_by('-created_on') #it gives the comments a chronological order

#this is for likes by various users on the post by a user
class LikeModel(models.Model):
	user = models.ForeignKey(UserModel)
	post = models.ForeignKey(PostModel)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
# one click on the 'like' button likes the post while another click on it unlikes it

#this further model is for the comments on the pic, user may comment on any pic in his feed
class CommentModel(models.Model):
	user = models.ForeignKey(UserModel)
	post = models.ForeignKey(PostModel)
	comment_text = models.CharField(max_length=555)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

#this further model is for creagting a database for various categories in which the posts may lie , such as clean or dirty
class CategoryModel(models.Model):
   user = models.ForeignKey(UserModel)
   post = models.ForeignKey(PostModel)
   category_text = models.CharField(max_length=255)


   @property
   def category(self):
      return CategoryModel.objects.filter(post=self)

