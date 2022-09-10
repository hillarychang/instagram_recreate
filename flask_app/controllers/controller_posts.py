from flask import render_template, redirect, request, session, flash

from flask_app import app

import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'C:/Users/hilla/dojo/coding_dojo/projects/recreate_insta/flask_app/static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

from flask_app.models.post import Post
from flask_app.models.user import User

app.secret_key = "shhh"


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/showUser')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('/showUser')
        if file and User.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(filename)
            data = {
                'image_path':"/static/images/"+filename,
                "text" : request.form["text"],
                "user_id": session['user_id'],
            }
            Post.save(data)
            # id = Post.save(data)
        return redirect('/showUser')




# @app.route('/create_image', methods=["POST"])
# def create_image():

#     # if not Post.validate_post(request.form): #request.form  (check user.py)
#     #     return redirect('/create_image') 

    
#     data = {
#             "text" : request.form["text"],
#             "user_id": session['user_id'],
#     }
#     id = Post.save(data)
#     return redirect('/showUser') 




@app.route("/comment/<int:id>", methods=["POST"]) #route to update
def comment(id):

    # if not Post.validate_post(request.form): #request.form  (check user.py)
    #     return redirect('/update/<int:id>')

#user_id is id of user who commented on post
    data = {
        'post_id':id,
        'user_id':session['user_id'], #change this
        "comment" : request.form["comment"]
    }

    Post.saveComment(data)
    return redirect('/showUser')


@app.route("/delete_comment/<int:id>") 
def delete_comment(id):

    # ^change to id is comment_id 
    data = {
        'comment_id':id,
        # 'post_id':id,
        'user_id':session['user_id']
    } 

    Post.deleteComment(data)  
    return redirect('/showUser') #redirect 


@app.route("/show_post_users/<int:id>")  #ID comes from 
def show_post_users(id):
    data = {"id":id}
    one_post = Post.get_one(data)
    current_user = User.get_one({'id':session['user_id']})

    status = Post.checkStatus({"user_id":session['user_id'], "post_id":id})
    post_with_users = Post.get_posts_with_likes(data) 
    this_post = Post.findPosterById(data)

    return render_template("view_post.html", spec_post = this_post, curr_status = status, post_user = post_with_users, post = one_post, user = current_user)


@app.route("/post") #runs add_post.html
def post():
    
    posts = Post.get_all()
    data = {"id":session['user_id']} 

    #ADDED
    user = User.get_user_with_posts(data) #returns a user with a list of posts
    return render_template("add_post.html", all_posts = posts, users = user) 



@app.route("/update/<int:id>", methods=["POST"]) #route to update
def update_post(id):

    if not Post.validate_post(request.form): #request.form  (check user.py)
        return redirect('/update/<int:id>')

    data = {
        'id':id,
        "text" : request.form["text"],
    }

    Post.update(data)
    return redirect('/showUser')


@app.route("/edit/<int:id>") #update a user, runs edit page
def edit_post(id):

    data = {'id':id}
    posts = Post.get_one(data)
    user = User.get_user_with_posts({'id':posts.user_id}) #returns a user with a list of posts

    return render_template("edit_post.html", post = posts, users  = user)






# @app.route('/create_post', methods=["POST"])
# def create_post():

#     if not Post.validate_post(request.form): #request.form  (check user.py)
#         return redirect('/create_post') 

    
#     data = {
#             "text" : request.form["text"],
#             "user_id": session['user_id'],
#     }
#     id = Post.save(data)
#     return redirect('/showUser') 



@app.route("/delete/<int:id>") #deletes a user, doesn't run a page
def delete_post(id):
    data = {'id':id}
    Post.delete(data)
    return redirect('/showUser')