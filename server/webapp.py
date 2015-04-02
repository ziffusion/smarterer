import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import timedelta
import httplib
import functools

import flask
import werkzeug.contrib.fixers as werkzeug_fixers

from utils import config, log

from datatypes.api_object import ApiObject
 
##############################################################################
#
##############################################################################

class Webapp(object):

    class Error(Exception):
        """
        endpoints can throw this exception for the error paths
        """
        def __init__(self, code, msg=None):
            self.code = code
            self.msg = msg

    def __init__(self):
        ### flask app
        static = config.path.www.static
        templates = config.path.www.templates
        self.flask = flask.Flask("webapp", static_folder=static, template_folder=templates)

        ### flask fixes
        self.flask.wsgi_app = werkzeug_fixers.ProxyFix(self.flask.wsgi_app)

        ### flask config
        self.flask.config["DEBUG"] = config.server.debug
        self.flask.config["LOGGER_NAME"] = log.name
        self.flask.config["SECRET_KEY"] = config.server.secret
        self.flask.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=config.server.session.lifetime)
        self.flask.config["SESSION_COOKIE_NAME"] = config.server.session.cookie
        self.flask.config["SESSION_PROTECTION"] = "strong"

    def run(self):
        log.info("server: http:{0} flash:{1}".format(config.ports.http, config.ports.flash))
        self.flask.run("0.0.0.0", config.ports.http, threaded=True, use_debugger=config.server.debug)

    def dump(self, msg):
        if config.server.dump: log.debug(msg)

    def route(self, *args, **kwargs):
        """
        composite decorator for endpoints
        combines endpoint decorator and flask.route decorator
        """
        def decorator(endpoint):
            ### apply endpoint decorator
            if not hasattr(endpoint, "_webapp_endpoint"):
                endpoint = self.endpoint(endpoint)

            ### apply flask decorator
            decorator = self.flask.route(*args, **kwargs)
            endpoint = decorator(endpoint)

            ### mark
            endpoint._webapp_endpoint = True

            return endpoint

        return decorator

    def endpoint(self, endpoint):
        """
        endpoint decorator - handles json serialization
        json in the request is parsed into an object and passed to the endpoint
        endpoints may return objects, or raise Error() exceptions for error paths
        returned objects and exceptions are converted to json and returned in the response
        """
        @functools.wraps(endpoint)
        def execute_endpoint(*args, **kwargs):
            log.debug("{0} {1}{2}".format(
                flask.request.method,
                flask.request.url_rule.rule,
                "?" + flask.request.query_string if flask.request.query_string else ""
            ))

            try:
                obj = self.execute_endpoint_inner(endpoint, *args, **kwargs)
                if not obj: obj = ApiObject()
                obj.code = httplib.OK
                obj.msg = None

            except self.Error as error:
                obj = ApiObject()
                obj.code = error.code
                obj.msg = error.msg
                log.exception(obj.msg)

            except:
                obj = ApiObject()
                obj.code = httplib.INTERNAL_SERVER_ERROR
                obj.msg = None
                log.exception(obj.msg)

            obj.msg = obj.msg if obj.msg else httplib.responses[obj.code]

            data = obj.encode()

            self.dump("response:\n{0}".format(data))

            response = flask.Response(
                data,
                obj.code,
                headers=None,
                mimetype="application/json"
            )

            return response

        return execute_endpoint

    def execute_endpoint_inner(self, endpoint, *args, **kwargs):
        """
        endpoint implementation helper
        """
        if flask.request.mimetype == "application/json":
            try:
                obj = ApiObject(flask.request.data)
                self.dump("request:\n{0}".format(obj))

            except:
                self.dump("request:\n{0}".format(flask.request.data))
                raise self.Error(httplib.BAD_REQUEST, "json parsing error")

        else:
            self.dump("request:\n{0}".format(flask.request.data))
            obj = None

        return endpoint(*args, obj=obj, **kwargs)

##############################################################################
#
##############################################################################

webapp = Webapp()
