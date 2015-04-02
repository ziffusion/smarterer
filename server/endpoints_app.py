import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import httplib
import flask
import flask.ext.login as flask_login
import packages.S3 as S3
import datetime

from utils import log, config
import datatypes.webapi as webapi
from server.webapp import Webapp
from dal.sentence_manager import SentenceManager
from dal.db import Db
from dal.dbo import SentenceRecorded

##############################################################################
#
##############################################################################

@Webapp.flask.context_processor
def template_context():
    context = {}
    context["site_live"] = config.server.live
    context["site_notice"] = config.server.notice
    context["js_minify"] = config.server.js_minify
    context["user_logged_in"] = Webapp.context.user != None
    return context

##############################################################################
#
##############################################################################

@Webapp.route("/record")
@flask_login.login_required
def record():

    if config.server.live:
        return flask.render_template("record.html")

    else:
        return flask.render_template("index.html")

##############################################################################
#
##############################################################################

@Webapp.route("/session-start", methods=["POST"])
@flask_login.login_required
def session_start(webapi_object=None):

    if not (webapi_object and isinstance(webapi_object, webapi.SessionStart)):
        raise Webapp.Error(httplib.BAD_REQUEST, "missing: SessionStart")

    return SentenceManager.session_start(Webapp.context.user.id)

##############################################################################
#
##############################################################################

@Webapp.route("/session-next", methods=["POST"])
@flask_login.login_required
def session_next(webapi_object=None):

    if not (webapi_object and isinstance(webapi_object, webapi.SessionNext)):
        raise Webapp.Error(httplib.BAD_REQUEST, "missing: SessionNext")

    return SentenceManager.session_next(Webapp.context.user.id, webapi_object.order)

##############################################################################
#
##############################################################################

@Webapp.route("/session-end", methods=["POST"])
@flask_login.login_required
def session_end(webapi_object=None):
    pass

##############################################################################
#
##############################################################################

@Webapp.route("/sentence-save", methods=["POST"])
@flask_login.login_required
def sentence_save():

    if len(Webapp.context.request.files) < 1:
        raise Webapp.Error(httplib.BAD_REQUEST, "missing sound file")

    for name in Webapp.context.request.files:
        mfile = Webapp.context.request.files[name]
        break

    fields = Webapp.form(("session_id", "rms", "noise", "snr", "platform", "filename"))

    if not fields:
        raise Webapp.Error(httplib.BAD_REQUEST, "missing parameters")

    if not fields["filename"] in SentenceManager.sentences:
        raise Webapp.Error(httplib.BAD_REQUEST, "bad sentence name")

    id = Webapp.context.user.id
    dob = Webapp.context.user.dob.strftime("%Y-%m") if Webapp.context.user.dob else "na"
    gender = Webapp.context.user.gender if Webapp.context.user.gender else "na"
    text = SentenceManager.sentences[fields["filename"]].text

    key = "{0}/donor{0}-{1}-{2}-{3}-{4}-{5}-{6}-UTC.wav".format(
            id,
            dob,
            gender,
            fields["platform"],
            fields["filename"],
            text,
            datetime.datetime.utcnow()
            )

    ### flask FileObjects are based on files or buffers depending on the size of data
    ### the buffer based FileObject doesn't support the file interface needed by S3

    try:
        mfile.fileno()
        data = mfile
    except Exception as ee:
        data = mfile.read()

    try:
        ### push to S3
        obj = S3.S3Object(data, {'title': fields["filename"]})
        headers = {'Content-Type': 'audio/wav'}
        conn = S3.AWSAuthConnection(config.aws.access_key.id, config.aws.access_key.secret)
        response = conn.put(config.aws.bucket, key, obj, headers)

        ### push to Db
        sentence = SentenceRecorded(fields)
        sentence.user_id = id
        sentence.create()

        return None, response.http_response.status, response.message

    except Exception as ee:
        log.exception("sentence_save")
        raise Webapp.Error(httplib.INTERNAL_SERVER_ERROR, "could not save file")


##############################################################################
#
##############################################################################

@Webapp.route("/favicon.ico")
def favicon():
    return Webapp.flask.send_static_file("images/favicon.ico")

##############################################################################
#
##############################################################################

@Webapp.route("/fonts/<font>")
def font(font):
    return Webapp.flask.send_static_file("fonts/" + font)

##############################################################################
#
##############################################################################

@Webapp.route("/", defaults={"path":"index"})
@Webapp.route("/<path:path>")
def path(path):
    try:
        response = flask.render_template("{0}.html".format(path))
    except:
        response = flask.render_template("404.html"), 404
    finally:
        return response

##############################################################################
#
##############################################################################

@Webapp.flask.errorhandler(404)
def error_404(error):
    return flask.render_template("404.html"), 404
