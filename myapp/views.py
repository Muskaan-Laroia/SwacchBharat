from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel ,CategoryModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
from SwacchBharat.settings import BASE_DIR
from clarifai.rest import ClarifaiApp
from imgurpython import ImgurClient
import sendgrid
from sendgrid.helpers.mail import *


#views help in adding functionality to the structure
# Create your views here.

your_clientId="31bd2c0d7d5a46d"
your_clientSecret="bd8022508c9d2924f77a230a120e3c8f6d919344"
sendgrid_key="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"
api_key_clarifai="b6cb8952189e4e608c72c82668c129b3"

#create the sign up page

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            if(len(form.cleaned_data['username'])<5 or set('[~!#$%^&*()_+{}":;\']+$ " "').intersection(form.cleaned_data['username'])):
                return render(request,'invalid.html')
            else:
                if (len(form.cleaned_data["password"])>5):
                    username = form.cleaned_data['username']
                    name = form.cleaned_data['name']
                    email = form.cleaned_data['email']
                    password = form.cleaned_data['password']
                    # saving data to the database
                    user = UserModel(name=name, password=make_password(password), email=email, username=username)
                    user.save()
                    sg = sendgrid.SendGridAPIClient(apikey=(sendgrid_key))
                    from_email = Email("muskaanlaroia@gmail.com")
                    to_email = Email(form.cleaned_data['email'])
                    subject = "Welcome to SwacchBharat"
                    content = Content("text/plain", "Swacch Bharat team welcomes you!\n We hope you like sharing the images of your surroundings to help us build a cleaner india /n")
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                    return render(request, 'success.html')
                else:
                    return render(request, 'invalid.html')
                    # return redirect('login/')
    else:
        form = SignUpForm()

    return render(request, 'index.html' , {'form': form})

#it creates the login page functionalities
def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    return render(request, 'invalidlogin.html')

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)
#creates the  post fiunctionality helping the user to post things

def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + post.image.url)

                client = ImgurClient(your_clientId, your_clientSecret)
                post.image_url = client.upload_from_path(path, anon=True)['link']

                post.save()

                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')

#this code is for clarifai and categorizing the posts under various attributes
def add_category(post):
    app = ClarifaiApp(api_key='c0d6dcc72a5f490b8a1f0df33bf2f272')
    model = app.models.get("general-v1.3")

    response = model.predict_by_url(url=post.image_url)
    if response["status"]["code"]==10000:
        if response["outputs"]:
            if response["output"][0]["data"]:
                if response["output"][0]["data"]["concepts"]:
                    x=[]
                    for index in range (0,len(response["outputs"][0]["data"]["concepts"])):
                        category=x.append(CategoryModel(post=post,category_text=response['outputs'][0]['data']['concepts'][index]['name']))
                        category.save()
                        print x
                else:
                    print 'no concepts error'
            else:
                print 'no data list error'
        else:
            print 'no outtput list error'
    else:
        print 'response code error'


def feed_view(request): #creates the feed page functionalities
    user = check_validation(request)
    if user:

        posts = PostModel.objects.all().order_by('created_on')

        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})
    else:

        return redirect('/login/')


def like_view(request):# create the like funcionalities
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id

            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()



            if not existing_like:
                like=LikeModel.objects.create(post_id=post_id, user=user)
                sg = sendgrid.SendGridAPIClient(apikey=(sendgrid_key))
                from_email = Email("muskaanlaroia@gmail.com")
                to_email = Email(like.post.user.email)
                subject = "You have a new like on your post %d " % (post_id)
                content = Content("text/plain",
                                  "You have a new like on your post %d /n Login to view the details" % post_id)
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
                print(response.status_code)
                print(response.body)
                print(response.headers)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')

#helps to post a comment on the post as it adds the commenting functionality
def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            sg = sendgrid.SendGridAPIClient(apikey=(sendgrid_key))
            from_email = Email("muskaanlaroia@gmail.com")
            to_email = Email(comment.post.user.email)
            subject = "Welcome to Swacch Bharat"
            content = Content("text/plain",
                              "Swacch Bharat team welcomes you!\n We hope you like sharing the images of your surroundings to help us build a cleaner india/n")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')


# For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None
#helps the user to logout as it addsthe logging out funtionality taking the user to the login page
def logout_view(request):
    request.session.modified= True
    response=redirect('/login/')
    response.delete_cookie(key="session_token")
    return response