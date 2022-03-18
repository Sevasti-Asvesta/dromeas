import os
import sys
import secrets
from PIL import Image
from flask import Flask, request, abort, jsonify, render_template, url_for, flash, redirect
from flask_cors import CORS
import traceback
from models import setup_db, SampleLocation,  User, db #,db_drop_and_create_all
#importing from forms.py the classes and then create routes
from forms import RegistrationForm, LoginForm, UpdateSettingsForm
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from models import SQLAlchemy
from flask_login import LoginManager
from flask_login import login_user, current_user, logout_user, login_required


app=Flask(__name__)


#maps code

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    
    db = SQLAlchemy(app)
    setup_db(app)
    CORS(app)
    """ uncomment at the first time running the app """
    #db_drop_and_create_all()

    csrf = CSRFProtect(app)

    app.config['SECRET_KEY']= 'cd94e39eea42d9b40641e9f18885fc22'
    app.config['WTF_CSRF_SECRET_KEY'] = "cd94e39eea42d9b40641e9f18885fc22"
    csrf.init_app(app)
    bcrypt= Bcrypt(app)
    login_manager= LoginManager(app)
    login_manager.init_app(app)
    login_manager.login_view='login' 
    login_manager.login_message_category='info'
    
    
    #according to the tutorial(vid.6) this has to be above 
    #User class in the models file

    @login_manager.user_loader
    def load_user(user_id):
       return User.query.get(int(user_id))



    #templates
    @app.route("/")
    @app.route("/index")
    def index():
        return render_template('index.html')
      #templates

   

   #sign up page
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('settings'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user= User(username=form.username.data, email=form.email.data, password= hashed_password, about_me=form.about_me.data, area=form.area.data, level=form.level.data)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}', 'success')
            return redirect(url_for('login'))
        return render_template('signup.html', title= 'Sign Up', form= form)
    
    #login page
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('profile'))
        form = LoginForm()
        if form.validate_on_submit():
            user= User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                #next_page= request.args.get('next')
                return  redirect(url_for('profile'))
            else:    
               flash('Login Unsuccessful. Please check email and password', 'danger')     
        return render_template('login.html', title= 'Log In', form= form)

    #logout page
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    
    #profile page
    @app.route('/profile')
    @login_required
    def profile():
        
        image_file = url_for('static', filename= 'images/' + current_user.image_file)
        return render_template('profile.html', title='Profile', image_file= image_file)

    
    #function for the images
    
    def save_picture(form_picture):
      random_hex = secrets.token_hex(8)
      _, f_ext = os.path.splitext(form_picture.filename)
      picture_fn = random_hex + f_ext
      picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
      
      output_size = (300, 300)
      i= Image.open(form_picture)
      i.thumbnail(output_size)
      i.save(picture_path)

      return picture_fn



   
    #settings page
    @app.route('/settings', methods=['GET', 'POST'])
       
    def settings():
        form= UpdateSettingsForm()
        
        if form.validate_on_submit():
          if form.picture.data:
              picture_file = save_picture(form.picture.data)
              current_user.image_file = picture_file
                
          current_user.username = form.username.data
          current_user.email = form.email.data 
          current_user.about_me= form.about_me.data
          current_user.area= form.area.data
          current_user.level = form.level.data
          db.session.commit()
          flash('your changes have been saved🎊', 'success')
          return redirect(url_for('settings'))
        elif request.method == 'GET' :
            form.about_me.data = current_user.about_me
            form.area.data = current_user.area
            form.level.data =current_user.level
            form.username.data = current_user.username
            form.email.data = current_user.email
        image_file= url_for('static', filename='images/' + current_user.image_file)
        return render_template('settings.html', title='Settings', image_file = image_file, form=form )
        
    
    
    


    #map page
    @app.route('/map', methods=['GET'])
    def map():
        return render_template(
            'map.html', 
            map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
        )

    @app.route("/api/store_item")
    def store_item():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            description = request.args.get('description')

            location = SampleLocation(
                description=description,
                geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude)
            )   
            location.insert()

            return jsonify(
                {
                    "success": True,
                    "location": location.to_dict()
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.route("/api/get_items_in_radius")
    def get_items_in_radius():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            radius = int(request.args.get('radius'))
            
            locations = SampleLocation.get_items_within_radius(latitude, longitude, radius)
            return jsonify(
                {
                    "success": True,
                    "results": locations
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500

    
    


    return app
#maps code

app= create_app()  

if __name__ == '__main__':
    #port = int(os.environ.get("PORT",5000))
    app.run(debug=True) #host='127.0.0.1',port=port,

  