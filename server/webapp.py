import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import timedelta
import httplib
import functools

import flask
import flask.ext.login as flask_login
import flask.ext.assets as flask_assets
import flask_sslify
import werkzeug.contrib.fixers as werkzeug_fixers

from utils import config, log, Context
import datatypes.webapi as webapi
from dal.user import User
 
##############################################################################
#
##############################################################################

class WebappMeta(type):

    #########################################

    class Error(Exception):
        def __init__(self, status, message, headers={}):
            self.message = message
            self.status = status
            self.headers = headers

    #########################################

    class WebappContext(Context):
        pass

    #########################################

    def __init__(cls, classname, bases, classdict):

        ### parent init
        type.__init__(cls, classname, bases, classdict)

        ### flask app
        static = os.path.join(config.path.www, "static")
        templates = os.path.join(config.path.www, "templates")

        cls.flask = flask.Flask("webapp", static_folder=static, template_folder=templates)

        ### flask fixes
        cls.flask.wsgi_app = werkzeug_fixers.ProxyFix(cls.flask.wsgi_app)

        ### flask config
        cls.flask.config["DEBUG"] = config.server.debug
        cls.flask.config["LOGGER_NAME"] = log.name
        cls.flask.config["SECRET_KEY"] = config.server.secret
        cls.flask.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=config.server.session.lifetime)
        cls.flask.config["SESSION_COOKIE_NAME"] = config.server.session.cookie
        cls.flask.config["SESSION_PROTECTION"] = "strong"

        ### flask ssl
        if config.server.ssl:
            cls.flask.config["DEBUG"] = False
            cls.sslify = flask_sslify.SSLify(cls.flask)

        ### flask assets
        cls.flask_assets = flask_assets.Environment(cls.flask)

        ### flask login manager
        cls.login_manager = flask_login.LoginManager()
        cls.login_manager.setup_app(cls.flask)
        cls.login_manager.user_loader(User.get)

        ### context management
        cls.context = cls.WebappContext()
        cls.flask.before_request(cls.before_request)
        cls.flask.after_request(cls.after_request)
        cls.flask.teardown_appcontext(cls.context_teardown)

    #########################################

    def run(cls):
        log.info("server: http:{0} flash:{1}".format(config.ports.http, config.ports.flash))
        cls.flask.run("0.0.0.0", config.ports.http, threaded=True, use_debugger=config.server.debug)

    #########################################

    def form(cls, fields):
        if hasattr(fields, "__iter__"):
            mdict = {}
            for name in fields:
                if name in cls.context.request.form:
                    mdict[name] = cls.context.request.form[name]
                else:
                    return None
            return mdict

        if fields in cls.context.request.form:
            return cls.context.request.form[fields]
        else:
            return None

    #########################################

    def before_request(cls):
        try:
            log.debug("context: setup")

            Context.setup()

            cls.context.request = flask.request
            cls.context.request_is_json = flask.request.mimetype == "application/json"

            if flask_login.current_user.is_authenticated():
                cls.context.user = flask_login.current_user
                log.context_set(str(cls.context.user.id))
            else:
                cls.context.user = None

            log.debug("request: {0} - {1} {2}".format(
                flask.request.remote_addr,
                flask.request.method,
                flask.request.path
                ))

        except:
            log.exception("context: setup")

    def after_request(cls, response):
            log.debug("response: {0} - {1} {2} - {3}".format(
                flask.request.remote_addr,
                flask.request.method,
                flask.request.path,
                response.status
                ))
            return response

    def context_teardown(cls, *args, **kwargs):
        try:
            log.debug("context: teardown")
            Context.teardown()
        except:
            log.exception("context: teardown")

    #########################################

    def route(cls, *args, **kwargs):
        """
        decorator for endpoints
        proxy for flask.route
        applies endpoint decorator, and then flask.route decorator
        """
        def decorator(endpoint):
            ### apply endpoint decorator
            if not hasattr(endpoint, "_webapp_endpoint"):
                endpoint = cls.endpoint(endpoint)

            ### apply flask decorator
            decorator = cls.flask.route(*args, **kwargs)
            endpoint = decorator(endpoint)

            ### mark
            endpoint._webapp_endpoint = True

            return endpoint

        return decorator

    #########################################

    def endpoint(cls, endpoint):
        """
        decorator for endpoints
        allows endpoints to deal with WebapiType objects, handling json automatically
        """
        @log.trace("endpoint")
        @functools.wraps(endpoint)
        def execute_endpoint(*args, **kwargs):

            ### execute endpoint

            response = None
            status = httplib.OK
            message = None
            headers = None

            try:
                if cls.context.request_is_json:
                    response = cls.execute_json_endpoint(endpoint, *args, **kwargs)
                else:
                    response = cls.execute_rest_endpoint(endpoint, *args, **kwargs)

                ### handle response

                ### response can be a flask response or a WebapiType response
                ### flask response is Response, or a (partial) tuple
                ### WebapiType response is WebapiType, or a (partial) tuple
                ### unpack and handle WebapiType response

                if isinstance(response, webapi.WebapiType):
                    response = (response,)

                if isinstance(response, tuple) and (not response[0] or isinstance(response[0], webapi.WebapiType)):
                    response = response + (None, None, None, None)

                    headers  = response[3]
                    message  = response[2]
                    status   = response[1] if response[1] else httplib.OK
                    response = response[0]

                    ### wrap WebapiType into a WebapiType.Response
                    response = cls.webapi_response(response)

            ### exceptions from and endpoint execution and response handling

            except cls.Error as error:
                log.error("error: {0}".format(error.message))
                response = None
                status = error.status
                message = error.message
                headers = error.headers

            except Exception as exception:
                log.exception("server error")
                response = None
                status = httplib.INTERNAL_SERVER_ERROR
                message = "server error"
                headers = None

            ### build flask.Response

            if not response:
                response = webapi.Response()

            if isinstance(response, webapi.Response):
                response.status = httplib.responses[status]
                response.status_code = status
                response.message = message

                if config.server.dump:
                    log.debug("dump: response object:\n{0}".format(str(response)))

                response = flask.Response(
                    response.encode(),
                    response.status_code,
                    headers,
                    mimetype='application/json'
                )

            return response

        return execute_endpoint

    #########################################

    @log.trace()
    def execute_rest_endpoint(cls, endpoint, *args, **kwargs):

        if config.server.dump:

            for name in flask.request.form:
                log.debug("dump: form: " + name + " = " + flask.request.form[name])

            for mfile in flask.request.files:
                log.debug("dump: file: " + mfile)

        return endpoint(*args, **kwargs)

    #########################################

    @log.trace()
    def execute_json_endpoint(cls, endpoint, *args, **kwargs):

        if config.server.dump:
            log.debug("request:\n{0}".format(flask.request.data))

        try:
            request = webapi.WebapiType.decode(flask.request.data)
        except:
            log.exception("json decode")
            raise cls.Error(httplib.BAD_REQUEST, "json could not be parsed")

        if not isinstance(request, webapi.Request):
            raise cls.Error(httplib.BAD_REQUEST, "invalid object type")

        try:
            request.validate()
        except:
            log.exception("request validation")
            raise cls.Error(httplib.BAD_REQUEST, "incomplete request object")

        if config.server.dump:
            log.debug("dump: request object:\n{0}".format(str(request)))

        return endpoint(*args, webapi_object=request.body, **kwargs)

    #########################################

    def webapi_response(cls, body):

        response = webapi.Response()

        if body:
            try:
                body.validate()

            except:
                log.exception("response validation")
                raise cls.Error(httplib.INTERNAL_SERVER_ERROR, "incomplete response object")

            response.body = body

        return response

##############################################################################
#
##############################################################################

class Webapp(object):
    __metaclass__ = WebappMeta
