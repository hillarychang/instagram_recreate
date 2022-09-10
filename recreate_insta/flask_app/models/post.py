# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

from flask_app import app

import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'C:/Users/hilla/dojo/coding_dojo/projects/recreate_insta/flask_app/static/images'
#maybe get path from fie
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from flask_bcrypt import Bcrypt   
bcrypt = Bcrypt(app)   

import re	# the regex module

class Post: # model the class after the user table from  database
    
    db='recreate_insta' #database (in mySQL workbench)

    def __init__( self , data ):
        self.id = data['id']
        self.image_path = data['image_path']
        self.text = data['text']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']  # hidden input 

        self.numLike = 0
        self.likes = [] # use this to determine if the user likes the post (many to many)
        self.likedUsers = []

        self.poster = { }

        self.comment = []




    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# FIX THIS 9/7: change query?? get comments for each post + the user who commented??
    @classmethod
    def get_post_with_comments( cls , data ):

        print("id__",data)

        query = """
        SELECT * FROM post 
        LEFT JOIN comment ON comment.post_id = post.id 
        LEFT JOIN user ON user.id = comment.user_id
        WHERE post.id = %(id)s
        """
#     add line to sort by order: ORDER BY comment.created_at DESC;

        results = connectToMySQL(cls.db).query_db(query, data) #results returns a list of dictionaries (key is column, value is row in specific column)

        # results will be a list of user objects with the post attached to each row. 


        post = cls( results[0] )
        for row_from_db in results:
            # Now parse the post data to make instances of posts and add them into the list.
            join_data = {
                "post_id" : row_from_db["post_id"],  #posts.__ because id overlaps with id in other tables
                "comment_id" : row_from_db["comment.id"],  
                "comment" : row_from_db["comment"],
                "first_name" : row_from_db['first_name'],
                "user_id" : row_from_db['comment.user_id']
                
            }

            print("herearetheresults",join_data)
            post.comment.append( join_data ) #call post class, then call Post constructor
        # print("POST OBJECT",post.comment)
        # for i in post.comment:
        #     print("WHATISTHIS",i)
        #     print("OKTHISSHOULDWORK",i['comment'])
        #     print("Commented",i['first_name'])
        return post.comment     #returns an object with a list of posts inside 


    # @classmethod
    # def get_post_with_comments( cls , data ):
    #     query = """SELECT * FROM comment 
    #     LEFT JOIN post ON comment.post_id = post.id
    #     LEFT JOIN user ON comment.user_id = user.id 
    #     WHERE post.id = %(id)s;"""

    #     results = connectToMySQL(cls.db).query_db( query , data )
    #     # results will be a list of post objects with the likes attached to each row. 
    #     post = cls( results[0] )

    #     for row_from_db in results:
    #         # Now parse the post data to make instances of likers and add them into the list.
    #         comment_data = {
                # "comment_id" : row_from_db["comment.id"],  #posts.__ because id overlaps with id in other tables
                # "comment" : row_from_db["comment"],
                # "user_id" : row_from_db['user.id']
    #         }
    #         post.comment.append(user.User( comment_data ) )

    #     return post #^get a list of users for that post that like it 


    @classmethod
    def checkFollowStatus(cls, data):
        query = "SELECT * FROM follower WHERE (user_id = %(user_id)s AND follower_id = %(follower_id)s);"
        results = connectToMySQL(cls.db).query_db(query, data) #results returns a list of dictionaries (key is column, value is row in specific column)
    
        var = None
        print("length",len(results))
        if len(results) == 1:
            var = True
        else:
            var = False
        return var 

    
    @classmethod
    def checkStatus(cls, data): #checkStatus for like
        #*changed this method
        query = "SELECT * FROM likes WHERE (user_id = %(user_id)s AND post_id = %(post_id)s);"
        results = connectToMySQL(cls.db).query_db(query, data) #results returns a list of dictionaries (key is column, value is row in specific column)
        
        var = None
        print("length",len(results))
        if len(results) == 1: #post is liked by user
            var = True
        else:
            var = False #post is not liked by user
        return var 


    @classmethod
    def findPosterById(cls, data):
        query = """
            SELECT post.*, user.first_name, user.last_name  
            FROM post 
            JOIN user ON post.user_id = user.id 
            WHERE post.id = %(id)s;
            """
        results = connectToMySQL(cls.db).query_db( query , data )
        output = cls( results[0] )
        for row_from_db in results:
            join_data = {
                "first_name" : row_from_db["first_name"],
                "last_name" : row_from_db["last_name"]
            }
            output.poster = ( join_data ) 
        return output 


    @classmethod     # This method will retrieve the post with all the likes that are associated with the post.
    def getNumLikesforPost( cls , post_id ):
        query = """
            SELECT * 
            FROM likes
            WHERE likes.post_id = %(post_id)s;
            """
        data = {"post_id":post_id}
        results = connectToMySQL(cls.db).query_db( query , data )
        return (len(results))


    @classmethod
    def getAmtLike(cls, data):
        #*changed this method
        query = "SELECT * FROM likes WHERE post_id = %(post_id)s;"
        results = connectToMySQL(cls.db).query_db(query, data) #results returns a list of dictionaries (key is column, value is row in specific column)
        return len(results)


    @classmethod
    def get_posts_with_likes( cls , data ):
        query = """
            SELECT * 
            FROM post 
            LEFT JOIN likes ON likes.post_id = post.id 
            LEFT JOIN user ON likes.user_id = user.id 
            WHERE post.id = %(id)s;
            """
        results = connectToMySQL(cls.db).query_db( query , data )
        # results will be a list of post objects with the likes attached to each row. 
        post = cls( results[0] )

        for row_from_db in results:
            # Now parse the post data to make instances of likers and add them into the list.
            user_data = {
                "id" : row_from_db["user.id"],
                "first_name" : row_from_db["first_name"],
                "last_name" : row_from_db["last_name"],
                "email" : row_from_db["email"],

                "password":row_from_db["password"],

                "created_at" : row_from_db["user.created_at"],
                "updated_at" : row_from_db["user.updated_at"]
            }
            post.likedUsers.append(user.User( user_data ) )

        return post #^get a list of users for that post that like it 





    @classmethod
    def save(cls, data ):
        query = "INSERT INTO post ( image_path, text , user_id, created_at , updated_at ) VALUES ( %(image_path)s, %(text)s , %(user_id)s , NOW() , NOW() );"
        result = connectToMySQL(cls.db).query_db( query, data )  # returns an ID because of insert statement
        return result
    
    @classmethod     # class method to remove one user from the database
    def delete(cls, data ):
        query = "DELETE FROM post WHERE id=%(id)s;"
        return connectToMySQL(cls.db).query_db( query, data )

    @classmethod
    def get_all(cls):

        query = """
        SELECT * FROM post 
        LEFT JOIN user ON post.user_id = user.id
        ORDER BY post.created_at DESC;
        """

        results = connectToMySQL(cls.db).query_db(query)
        
        # if len(results) < 1:
        #     return

        posts = []      # Create an empty list to append instances of posts
        
        for post in results: # Iterate over the db results and create instances of posts with cls.
            one_post = cls(post)


            user_data = {
                "id":post["user.id"], 
                "first_name":post["first_name"], 
                "last_name":post["last_name"],
                "email":post["email"],
                "password":post["password"],
                "created_at" :post['user.created_at'],
                "updated_at": post['user.updated_at']
            }

            one_post.user = user.User(user_data)
            posts.append( one_post)
        return posts #returns list of class objects (list of dictionaries)



    
    def validate_post(post):
        is_valid = True # we assume this is true
        if len(post['text']) < 1:
            flash("Text must not be blank.")
            is_valid = False
        return is_valid




    @classmethod
    def get_one(cls, data):
        query = "SELECT * FROM post WHERE id = %(id)s ;" #%(id)s is the key of the dictionary data and returns id
        results = connectToMySQL(cls.db).query_db(query, data) #query_db returns list of objects
        return cls(results[0])   


    @classmethod     # if logged in as user, can delete post
    def delete(cls, data ):
        query = "DELETE FROM post WHERE id=%(id)s;"
        return connectToMySQL(cls.db).query_db( query, data )

    @classmethod     # class method to edit one post in the database
    def update(cls, data ):
        query = "UPDATE post SET text = %(text)s, created_at =NOW(), updated_at=NOW() WHERE id=%(id)s"
        return connectToMySQL(cls.db).query_db( query, data )


    @classmethod
    def saveComment(cls, data ):
        query = "INSERT INTO comment ( comment , user_id, post_id, created_at) VALUES ( %(comment)s , %(user_id)s , %(post_id)s, NOW());"
        result = connectToMySQL(cls.db).query_db( query, data )  # returns an ID because of insert statement
        return result
    

    # edit this make it more specific
    @classmethod
    def deleteComment( cls , data ): 
        query = "DELETE FROM comment WHERE (id = %(comment_id)s);"
        return connectToMySQL(cls.db).query_db(query,data) 

    # @classmethod
    # def deleteComment( cls , data ): 
    #     query = "DELETE FROM comment WHERE (user_id = %(user_id)s AND comment_id = %(comment_id)s);"
    #     return connectToMySQL(cls.db).query_db(query,data) 