from flask import Flask
# from flask_cors import CORS
from api.routes import api
from api.models import db
# from flask_uploads import configure_uploads

app = Flask(__name__)
# CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideas.db'
app.config['UPLOADED_FILES_DEST'] = 'uploads/'
db.init_app(app)
# configure_uploads(app, uploads)
app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)