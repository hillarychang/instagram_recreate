# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
# from flask import render_template, redirect, request, session, flash

from flask_app.models import post

from flask_app import app

import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'C:/Users/hilla/dojo/coding_dojo/projects/recreate_insta/flask_app/static/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


from flask_bcrypt import Bcrypt   
bcrypt = Bcrypt(app)     

import re	# the regex module

class User: # model the class after the user table from the database
    
    db='recreate_insta' #database (in mySQL workbench)

    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

        self.numFollower = 0
        self.numPost = 0
        self.following_id_list = []

        self.followers = []
        self.following = []
        self.posts=[] # one to many
        

    # @classmethod #get list of users this user is following
    # def select_user_following( cls , data ): #like get_posts_with_likes
    #     query = """
    #     SELECT u.*, u2.*
    #     FROM follower
    #     LEFT JOIN user u
    #     ON follower.follower_id = u.id
    #     LEFT JOIN user u2
    #     ON follower.user_id = u2.id
    #     WHERE follower.follower_id = %(id)s;
    #     """



    @classmethod #get list of users this user is following
    def get_user_with_followings( cls , data ): #like get_posts_with_likes
        query = """
        SELECT u.*, u2.*
        FROM follower
        LEFT JOIN user u
        ON follower.follower_id = u.id
        LEFT JOIN user u2
        ON follower.user_id = u2.id
        WHERE follower.follower_id = %(id)s;
        """

        results = connectToMySQL(cls.db).query_db( query , data )
        # results will be a list of user objects with the user/follower attached to each row. 
        
        if len(results)<1:
            return False
        
        user_info = cls( results[0] ) #makes a class instance (user object out of user columns in first row)

        for row_from_db in results:
            # Now parse the user data to make instances of followers and add them into the list.
            follower_data = {
                "id" : row_from_db["u2.id"],
                "first_name" : row_from_db["u2.first_name"],
                "last_name" : row_from_db["u2.last_name"],
                "email" : row_from_db["u2.email"],

                "password":row_from_db["u2.password"],

                "created_at" : row_from_db["u2.created_at"],
                "updated_at" : row_from_db["u2.updated_at"]
            }
            user_info.following_id_list.append(row_from_db["u2.id"])
            user_info.following.append(User( follower_data ) ) #calls User constructor method
            print("HEARTBREAKANNIVERSARY",user_info.following_id_list)
        return user_info #get a list of users this user is following 



    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    @classmethod     # This method will retrieve the post with all the likes that are associated with the post.
    def getNumPostsforUser( cls , user_id ):
        query = """
            SELECT * 
            FROM post
            WHERE post.user_id = %(user_id)s;
            """
        data = {"user_id":user_id}
        results = connectToMySQL(cls.db).query_db( query , data )
        return (len(results))


    @classmethod     # This method will retrieve the post with all the likes that are associated with the post.
    def getNumFollowingforUser( cls , user_id ):
        query = """
            SELECT * 
            FROM follower
            WHERE follower.follower_id = %(user_id)s;
            """
        data = {"user_id":user_id}
        results = connectToMySQL(cls.db).query_db( query , data )
        return (len(results))


    @classmethod     # This method will retrieve the post with all the likes that are associated with the post.
    def getNumFollowersforUser( cls , user_id ):
        query = """
            SELECT * 
            FROM follower
            WHERE follower.user_id = %(user_id)s;
            """
        data = {"user_id":user_id}
        results = connectToMySQL(cls.db).query_db( query , data )
        return (len(results))


    @classmethod #get list of followers following this user
    def get_user_with_followers( cls , data ): #like get_posts_with_likes
        query = """
        SELECT u.*, u2.*
        FROM follower
        LEFT JOIN user u
        ON follower.user_id = u.id
        LEFT JOIN user u2
        ON follower.follower_id = u2.id
        WHERE follower.user_id = %(id)s;
        """

        results = connectToMySQL(cls.db).query_db( query , data )
        # results will be a list of user objects with the user/follower attached to each row. 
        
        if len(results)<1:
            return False
        
        print("HERERESULTS",results)
        user_info = cls( results[0] ) #makes a class instance (user object out of user columns in first row)

        for row_from_db in results:
            # Now parse the user data to make instances of followers and add them into the list.
            follower_data = {
                "id" : row_from_db["u2.id"],
                "first_name" : row_from_db["u2.first_name"],
                "last_name" : row_from_db["u2.last_name"],
                "email" : row_from_db["u2.email"],

                "password":row_from_db["u2.password"],

                "created_at" : row_from_db["u2.created_at"],
                "updated_at" : row_from_db["u2.updated_at"]
            }
            user_info.followers.append(User( follower_data ) ) #calls User constructor method

        return user_info #get a list of followers for this user 


    @classmethod
    def get_user_with_posts( cls , data ):
        query = """
        SELECT * FROM user 
        LEFT JOIN post ON post.user_id = user.id 
        WHERE user.id = %(id)s;
        """
        results = connectToMySQL(cls.db).query_db( query , data )
        # results will be a list of user objects with the post attached to each row. 

        user = cls( results[0] )
        for row_from_db in results:
            # Now parse the post data to make instances of posts and add them into the list.
            post_data = {
                "id" : row_from_db["post.id"],  #posts.__ because id overlaps with id in other tables
                "image_path" : row_from_db["image_path"], #added
                "text" : row_from_db["text"],
                "user_id" : row_from_db['user_id'],
                "created_at" : row_from_db["post.created_at"],
                "updated_at" : row_from_db["post.updated_at"]
                
            }
            user.posts.append( post.Post( post_data ) ) #call post class, then call Post constructor
        return user     #returns an object with a list of posts inside 

    @classmethod
    def add_to_user_likes( cls , data ):
        query = "INSERT INTO likes ( user_id , post_id ) VALUES (%(user_id)s, %(post_id)s);"
        return connectToMySQL(cls.db).query_db(query,data) 

    @classmethod
    def delete_user_likes( cls , data ): 
        query = "DELETE FROM likes WHERE (user_id = %(user_id)s AND post_id = %(post_id)s);"
        return connectToMySQL(cls.db).query_db(query,data) 


    @classmethod
    def add_to_user_followers( cls , data ): 
        query = "INSERT INTO follower ( user_id , follower_id ) VALUES (%(user_id)s, %(follower_id)s);"
        return connectToMySQL(cls.db).query_db(query,data) 

    @classmethod
    def delete_user_followers( cls , data ): 
        query = "DELETE FROM follower WHERE (user_id = %(user_id)s AND follower_id = %(follower_id)s);"
        return connectToMySQL(cls.db).query_db(query,data) 



# REGISTRATION
    @classmethod
    def save(cls, data ):
        query = "INSERT INTO user ( first_name , last_name  , email, password, created_at, updated_at ) VALUES ( %(first_name)s , %(last_name)s , %(email)s , %(password)s ,NOW() , NOW() );"
        result = connectToMySQL(cls.db).query_db( query, data )  # returns an ID because of insert statement
        return result
    

#LOGIN
    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM user WHERE email = %(email)s;"
        result = connectToMySQL(cls.db).query_db(query,data)
        #result is a list of dictionaries

        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0]) 

    @staticmethod
    def validate_user(user):
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
        is_valid = True # we assume this is true

        currentUser = User.get_by_email({'email':user['email']})
        if currentUser: #falsy/truthy -> get_by_email returns either empty tuple or a tuple if it already exists
            flash("User already exists")
            is_valid = False
        if len(user['fname']) < 2:
            flash("First name is required.")
            is_valid = False
        if len(user['lname']) < 2:
            flash("Last name is required.")
            is_valid = False
        if len(user['email']) < 1:
            flash("Email is required.")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password should be a minimum of 8 characters.")
            is_valid = False
        # test whether a field matches the pattern
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!")
            is_valid = False

        return is_valid


    @staticmethod
    def validate_login(user):
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
        is_valid = True # we assume this is true
        if len(user['email']) < 1:
            flash("Email is required.")
            is_valid = False
        if len(user['password']) < 1:
            flash("Password is required.")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!")
            is_valid = False
        return is_valid



    @classmethod
    def get_all(cls):
        query = "SELECT * FROM user;"
        results = connectToMySQL(cls.db).query_db(query)
        users = []      # Create an empty list to append instances of users
        for user in results: # Iterate over the db results and create instances of users with cls.
            users.append( cls(user) )
        return users #returns list of class objects (list of dictionaries)
            

    @classmethod
    def get_one(cls, data):
        # data = {'id': id}
        query = "SELECT * FROM user WHERE id = %(id)s ;" #%(id)s is the key of the dictionary data and returns id
        results = connectToMySQL(cls.db).query_db(query, data) #query_db returns list of objects
        print ("here",results)
        return cls(results[0])   

    @classmethod
    def delete(cls, data ):     # class method to remove one user from the database
        query = "DELETE FROM user WHERE id=%(id)s;"
        return connectToMySQL(cls.db).query_db( query, data )

    @classmethod     # class method to edit one user in the database
    def update(cls, data ):
        query = "UPDATE user SET first_name = %(fname)s , last_name = %(lname)s  , email = %(email)s , updated_at=NOW() WHERE id=%(id)s"
        return connectToMySQL(cls.db).query_db( query, data )
