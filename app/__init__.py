from flask import Flask
# Added
from flask_cors import CORS, cross_origin

app = Flask(__name__)
# Added
cors = CORS(app)

if app.config["ENV"] == "production":

    app.config.from_object("config.ProductionConfig")

elif app.config["ENV"] == "development":

    app.config.from_object("config.DevelopmentConfig")

else:

    app.config.from_object("config.ProductionConfig")

#Added
app.config['CORS_HEADERS'] = 'Content-Type'


from app import views
# https://stackoverflow.com/questions/25594893/how-to-enable-cors-in-flask
