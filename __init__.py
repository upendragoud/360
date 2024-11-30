from flask import Flask, request, jsonify, g
import datetime
from datetime import timedelta
from flask_caching import Cache
from flask_cors import CORS, cross_origin
from .log_handler import get_logger
from flasgger import Swagger
from .swagger_config import SWAGGER_TEMPLATE
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import verify_jwt_in_request, JWTManager

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache(config={'CACHE_TYPE': 'simple'})


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    CORS(app, origins="*", headers=['Content-Type','Authorization'])

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    swagger = Swagger(app, template=SWAGGER_TEMPLATE)

    logger = get_logger()

    # Blueprints
    from app.main import main
    from app.authentication import bp as auth_bp
    from app.account import bp as account_bp
    from app.sso import bp as sso_bp
    from app.plugins.routes import plugins_bp
    from app.user.routes import bp as user_bp
    from app.maturity_frameworks.routes import bp as maturity_frameworks_bp
    from app.store.routes import bp as store_bp
    from app.hub.routes import bp as hub_bp
    from app.authentication.models import User
    from app.organizations.routes import bp as org_bp
    from app.resources.routes import bp as resources_bp
    from app.assessments.routes import bp as assessments_bp
    from app.recommendations.routes import bp as recommendations_bp
    from app.tasks.routes import bp as tasks_bp
    from app.notifications.routes import bp as notifications_bp
    from app.billing.routes import bp as billing_bp
    from app.pricing.routes import bp as pricing_bp
    from app.dashboard.routes import bp as dashboard_bp
    from app.activities.routes import bp as activities_bp
    from app.consultants.routes import bp as consultants_bp
    from app.settings.routes import bp as settings_bp
    from app.socket.routes import bp as socket_bp
    from app.posts.routes import bp as posts_bp
    from app.meetings.routes import bp as meetings_bp
    from apscheduler.schedulers.background import BackgroundScheduler
    from .scheduler import rotate_api_keys
    from app.meetings.routes import bp as meetings_bp
    from app.healthz.routes import healthz_bp
    from app.maturity_models.routes import bp as maturity_models_bp

    # Initialize scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(rotate_api_keys, 'interval', days=180)
    scheduler.start()

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main)
    app.register_blueprint(plugins_bp, url_prefix='/plugins')
    app.register_blueprint(sso_bp, url_prefix='/sso')
    app.register_blueprint(maturity_frameworks_bp)
    app.register_blueprint(maturity_models_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(hub_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(assessments_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(pricing_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(consultants_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(socket_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(healthz_bp)


    @app.route('/app/invalidate_cache', methods=['POST'])
    def invalidate_cache():
        cache.clear()
        logger.info("All cache has been cleared!")
        return jsonify(message="Cache has been cleared"), 200
    

    # @app.before_request
    # def ensure_authentication_present():
    #     excluded_routes = [
    #         'authentication.login',
    #         'authentication.check-sso',
    #         'sso.login',
    #         'sso.callback',
    #         'flasgger.static',
    #         'flasgger.apidocsjson',
    #         'flasgger.apidocsspec',
    #         'orgs.get_orgs'
            
    #     ]

    #     excluded_patterns = [
    #         '/sso/login/<account_id>',
    #         '/sso/callback/<account_id>',
    #         '/auth/check-sso/<account_id>',
    #         '/apidocs/',
    #         '/apispec_1.json',
    #         '/orgs/',
    #         '/healthz'
    #     ]

    #     if request.method == "OPTIONS":
    #         return
        
    #     if request.endpoint in excluded_routes:
    #         return None

    #     if request.url_rule and any(rule == request.url_rule.rule for rule in excluded_patterns):
    #         return None

    #     jwt_token = request.headers.get('Authorization')
    #     api_key = request.headers.get('X-API-KEY')
    #     # if not jwt_token and not api_key:
    #     #     return jsonify({"msg": "Authentication missing! Either JWT or API key required."}), 401

    #     if api_key:
    #         application_name_header = request.headers.get('X-APP-NAME')

    #         if not application_name_header:
    #             return jsonify({"msg": "Missing application name header!"}), 400

    #         if not request.headers.get('PROTOCOL'):
    #             user = User.query.filter_by(api_key=api_key).first()

    #             # Restrict to one application at a time
    #             if user.last_used_app and user.last_used_app != application_name_header:
    #                 return jsonify({"msg": "API key is already active for a different application!"}), 401

    #             if not user or user.application_name != application_name_header:
    #                 return jsonify({"msg": "Invalid API key or application!"}), 401

    #             # Update the last used application and timestamp
    #             user.last_used_app = application_name_header
    #             user.last_used_timestamp = datetime.datetime.utcnow()
    #             db.session.commit()
    #             g.current_user = user
    #             g.is_authenticated_via_api_key = True
    #         else:
    #             # print(request.headers.get('PROTOCOL'), flush=True)
    #             g.is_authenticated_via_api_key = True

    @app.before_request
    def ensure_jwt_required():
        # If authenticated via API key, bypass this check
        if 'is_authenticated_via_api_key' in g and g.is_authenticated_via_api_key:
            return

        # List of routes to exclude from the JWT required check
        excluded_routes = [
            'authentication.login',
            'authentication.check-sso',
            'sso.login',
            'sso.callback',
            'flasgger.static',
            'flasgger.apidocsjson',
            'flasgger.apidocsspec',
            'orgs.get_orgs'
        ]

        # For dynamic routes, you can also check the rule
        excluded_patterns = [
            '/sso/login/<account_id>',
            '/sso/callback/<account_id>',
            '/auth/check-sso/<account_id>',
            '/apidocs/',
            '/apispec_1.json',
            '/healthz',
            '/orgs/',
        ]

        if request.method == "OPTIONS":
            return

        
        if request.endpoint not in excluded_routes and request.url_rule and request.url_rule.rule not in excluded_patterns:
            try:
                pass
                verify_jwt_in_request()
            except Exception as e:
                return jsonify(msg="Token is missing or invalid!"), 401
    return app
