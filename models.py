import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2.types import Geometry
from shapely.geometry import Point
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography
from sqlalchemy.sql.expression import cast
from geoalchemy2.shape import from_shape
#importing extension from tutorial(video6)

from flask_login import UserMixin, LoginManager



db = SQLAlchemy()

'''
setup_db(app):
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    database_path = os.getenv('DATABASE_URL', 'postgresql://crvrudabwiisgs:a61a32d0f71f884e16e2bf98416762c50e507c36487c15970277fb4b27b1cea9@ec2-44-199-52-133.compute-1.amazonaws.com:5432/dq386rv0n6bh7')

    # https://stackoverflow.com/questions/62688256/sqlalchemy-exc-nosuchmoduleerror-cant-load-plugin-sqlalchemy-dialectspostgre
    database_path = database_path.replace('postgres://', 'postgresql://')

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
    drops the database tables and starts fresh
    can be used to initialize a clean database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

   
   
    # Initial sample data:
    insert_sample_locations()

def insert_sample_locations():
    loc1 = SampleLocation(
        description='Brandenburger Tor',
        geom=SampleLocation.point_representation(
            latitude=52.516247, 
            longitude=13.377711
        )
    )
    loc1.insert()

    loc2 = SampleLocation(
        description='Schloss Charlottenburg',
        geom=SampleLocation.point_representation(
            latitude=52.520608, 
            longitude=13.295581
        )
    )
    loc2.insert()

    loc3 = SampleLocation(
        description='Tempelhofer Feld',
        geom=SampleLocation.point_representation(
            latitude=52.473580, 
            longitude=13.405252
        )
    )
    loc3.insert()

class SpatialConstants:
    SRID = 4326
    @staticmethod
    def point_representation(latitude, longitude):
        point = 'POINT(%s %s)' % (longitude, latitude)
        wkb_element = WKTElement(point, srid=SpatialConstants.SRID)
        return wkb_element
    @staticmethod
    def get_location_latitude(geom):
        point = to_shape(geom)
        return point.y
    @staticmethod
    def get_location_longitude(geom):
        point = to_shape(geom)
        return point.x



class SampleLocation(db.Model):
    __tablename__ = 'sample_locations'

    id = Column(Integer, primary_key=True)
    description = Column(String(80))
    geom = Column(Geometry(geometry_type='POINT', srid=SpatialConstants.SRID))  

    @staticmethod
    def point_representation(latitude, longitude):
        point = 'POINT(%s %s)' % (longitude, latitude)
        wkb_element = WKTElement(point, srid=SpatialConstants.SRID)
        return wkb_element

    @staticmethod
    def get_items_within_radius(lat, lng, radius):
        """Return all sample locations within a given radius (in meters)"""

        #TODO: The arbitrary limit = 100 is just a quick way to make sure 
        # we won't return tons of entries at once, 
        # paging needs to be in place for real usecase
        results = SampleLocation.query.filter(
            ST_DWithin(
                cast(SampleLocation.geom, Geography),
                cast(from_shape(Point(lng, lat)), Geography),
                radius)
            ).limit(100).all() 

        return [l.to_dict() for l in results]    

    def get_location_latitude(self):
        point = to_shape(self.geom)
        return point.y

    def get_location_longitude(self):
        point = to_shape(self.geom)
        return point.x  

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'location': {
                'lng': self.get_location_longitude(),
                'lat': self.get_location_latitude()
            }
        }    

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()    

#--------------created the database model like in the tutorials-------#
 #@login_manager.user_loader
    #def load_user(user_id):
   # return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username= db.Column(db.String(20), unique=True, nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    image_file= db.Column(db.String(20), nullable=False, default='icon-runner.png')
    password= db.Column(db.String(60), nullable= False)
    
    about_me = db.Column(db.Text, nullable= False)
    area= db.Column(db.String(100), nullable= False)
    level= db.Column(db.String(100), nullable= False)
    geom = Column(Geometry(geometry_type='POINT', srid=SpatialConstants.SRID))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}','{self.image_file}','{self.about_me},'{self.level},'{self.area})"

    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email':self.email,
            'image_file':self.image_file,
            'about_me':self.about_me,
            'level':self.level,
            'location': {
                'lng': SpatialConstants.get_location_longitude(self.geom),
                'lat': SpatialConstants.get_location_latitude(self.geom)
            }
        }  

    @staticmethod
    def get_items_within_radius(lat, lng, radius):
        """Return all sample locations within a given radius (in meters)"""

        #TODO: The arbitrary limit = 100 is just a quick way to make sure 
        # we won't return tons of entries at once, 
        # paging needs to be in place for real usecase
        results = User.query.filter(
            ST_DWithin(
                cast(User.geom, Geography),
                cast(from_shape(Point(lng, lat)), Geography),
                radius)
            ).limit(100).all() 

        return [l.to_dict() for l in results]    
