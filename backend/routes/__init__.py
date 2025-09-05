from .auth import bp as auth_bp
from .users import bp as users_bp
from .mood import bp as mood_bp
from .quiz import bp as quiz_bp
from .label_options import bp as label_options_bp
from .range_config import bp as range_config_bp
from .encouragement import bp as encouragement_bp
from .friends import bp as friends_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(mood_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(label_options_bp)
    app.register_blueprint(range_config_bp)
    app.register_blueprint(encouragement_bp)
    app.register_blueprint(friends_bp)
