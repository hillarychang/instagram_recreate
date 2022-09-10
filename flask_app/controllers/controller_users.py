from flask import render_template, redirect, request, session, flash

from flask_app import app

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

from flask_app.models.user import User
from flask_app.models.post import Post

app.secret_key = "shhh"


@app.route("/create_follower/<int:id>") #id is the person being followed by me
def create_follower(id):
    data = {
    "user_id":id,
    "follower_id": session['user_id']
    } 

    User.add_to_user_followers(data)      #inserts into follower table

    return redirect(f'/profile/{id}') #redirect 


@app.route("/delete_follower/<int:id>") 
def delete_follower(id):
    data = {
    "user_id":id,
    "follower_id": session['user_id']
    } 

    User.delete_user_followers(data)  

    return redirect(f'/profile/{id}') #redirect 



#CHANGE
@app.route("/profile/<int:id>")  #ID is user of post
def profile(id):
    data = {"id":id} #post's user id 
    current_user = User.get_one(data)
    users = User.get_one({"id":session['user_id']})
    posts = Post.get_all()

    user_with_posts = User.get_user_with_posts(data)


    status = Post.checkFollowStatus({"user_id":id, "follower_id":session['user_id']})
    user_with_followers = User.get_user_with_followers(data) #

# get number of followers for the profile's user
    num_follower = User.getNumFollowersforUser(current_user.id)
    current_user.numFollower = num_follower

# get number user is following for the profile's user
    num_following = User.getNumFollowingforUser(current_user.id)
    current_user.numFollowing = num_following



# get number of posts
    num_post = User.getNumPostsforUser(current_user.id)
    current_user.numPost = num_post


    return render_template("profile.html", user_follower = user_with_followers, curr_status = status, post_user = user_with_posts, this_user = current_user, user = users, all_posts = posts)


@app.route("/create_like/<int:id>") 
def create_like(id):
    data = {
    "user_id":session['user_id'],
    "post_id": id
    } 
    user = User.get_one({"id":session['user_id']})

    User.add_to_user_likes(data)  

    return redirect(f'/show_post_users/{id}') #redirect 


@app.route("/delete_like/<int:id>") 
def delete_like(id):
    data = {
    "user_id":session['user_id'],
    "post_id": id
    } 

    User.delete_user_likes(data)  

    return redirect(f'/show_post_users/{id}') #redirect 


@app.route("/showOne") #runs starting form
def showOne():
    
    data = {"id":session['user_id']} 
    user = User.get_user_with_posts(data) #returns a user with a list of posts

    return render_template("one_user.html", users = user) 


@app.route('/go_to_create_user')
def go_to_create_user():
    return render_template("create_user.html")

@app.route('/go_to_login')
def go_to_login():
    return render_template("index.html")


# REGISTRATION
@app.route('/create_user', methods=['POST'])
def create_user():

    if not User.validate_user(request.form): #request.form  (check user.py)
        return redirect('/create_user')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])

    data = {
        "first_name": request.form['fname'],
        "last_name": request.form['lname'],
        "email": request.form['email'],
        "password" : pw_hash #assign hash to self.password
    }

    user_id = User.save(data)

    session['user_id'] = user_id      # store user id into session
    return redirect("/showUser")



# LOGIN
@app.route('/login', methods=['POST'])
def login():

    if not User.validate_login(request.form): #request.form  (check user.py)
        return redirect('/')

    data = { "email" : request.form["email"] }
    user_in_db = User.get_by_email(data)

    if not user_in_db:
        flash("Invalid Email/Password")
        return redirect("/")

    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password")
        return redirect('/')

    session['user_id'] = user_in_db.id #create session with user_in_db.id 

    return redirect("/showUser")



# fix this method: when no posts: result.html doesn't run
@app.route("/showUser") #runs starting form
def showUser():
    
    posts = Post.get_all()
    data = {"id":session['user_id']} # need user's id
    user = User.get_user_with_followings(data) #when user has no post becomes False
    following_list =[]
    if (user != False):
        following_list = user.following_id_list

    user = User.get_user_with_posts(data) #returns a user with a list of posts


    for post in posts:
        num = Post.getNumLikesforPost(post.id)
        post.numLike = num
        comment_with_post = Post.get_post_with_comments({"id":post.id}) #should update comments for each post
        if (comment_with_post[0]['comment'] != None):
            post.comment = comment_with_post


    print("KDJSGFGS",following_list)

    return render_template("result.html", all_posts = posts, users = user, list_id = following_list) 


@app.route("/") #runs starting form
def index():
    return render_template("index.html") 



@app.route("/log_out") 
def log_out():
    session.clear()
    return redirect('/')


