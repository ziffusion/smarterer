import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import httplib
import flask

from utils import log, config
from server.webapp import webapp
from datatypes.api_object import ApiObject
import data.db as db
from server.dsl import dsl

##############################################################################
#
##############################################################################
def validate(obj):
    fields = ["n0", "n1", "n2", "op", "distractors"]
    for field in fields:
        if not hasattr(obj, field):
            return False

    if not isinstance(obj.distractors, list):
        return False

    return True

##############################################################################
#
##############################################################################

@webapp.route("/question/<int:id>", methods=["GET"])
def question_get(id, obj=None):
    question = db.Question.query.filter(db.Question.id == id).first()
    if not question:
        raise webapp.Error(httplib.NOT_FOUND)

    obj = ApiObject()
    obj.id = question.id
    obj.op = question.op
    obj.n0 = question.n0
    obj.n1 = question.n1
    obj.n2 = question.n2
    obj.distractors = []
    for distractor in question.distractors:
        obj.distractors.append(distractor.n2)

    resp = ApiObject()
    resp.question = obj

    return resp

##############################################################################
#
##############################################################################

@webapp.route("/question/<int:id>", methods=["POST"])
def question_post(id, obj=None):
    if not validate(obj):
        raise webapp.Error(httplib.BAD_REQUEST)

    question = db.Question.query.filter(db.Question.id == id).first()
    if not question:
        raise webapp.Error(httplib.NOT_FOUND)

    for distractor in question.distractors:
        db.db.session.delete(distractor)

    question.op = obj.op
    question.n0 = obj.n0
    question.n1 = obj.n1
    question.n2 = obj.n2

    for distractor in obj.distractors:
        dbo = db.Distractor(n2=distractor)
        dbo.question = question
        db.db.session.add(dbo)

    db.db.session.commit()

##############################################################################
#
##############################################################################

@webapp.route("/question", methods=["PUT"])
def question_put(obj=None):
    if not validate(obj):
        raise webapp.Error(httplib.BAD_REQUEST)

    question = db.Question()
    question.op = obj.op
    question.n0 = obj.n0
    question.n1 = obj.n1
    question.n2 = obj.n2
    db.db.session.add(question)

    for distractor in obj.distractors:
        dbo = db.Distractor(n2=distractor)
        dbo.question = question
        db.db.session.add(dbo)

    db.db.session.commit()

    resp = ApiObject()
    resp.question = obj
    resp.question.id = question.id

    return resp

##############################################################################
#
##############################################################################

@webapp.route("/question/<int:id>", methods=["DELETE"])
def question_delete(id, obj=None):
    question = db.Question.query.filter(db.Question.id == id).first()
    if not question:
        raise webapp.Error(httplib.NOT_FOUND)

    for distractor in question.distractors:
        db.db.session.delete(distractor)

    db.db.session.delete(question)

    db.db.session.commit()

##############################################################################
#
##############################################################################

@webapp.route("/question", methods=["GET"])
def question_query(obj=None):

    resp = ApiObject()
    query = db.Question.query

    ### process clause: where
    where = flask.request.args.get("where")
    if where:
        try:
            exprs = dsl.where(where)
            resp.where = where
        except:
            raise webapp.Error(httplib.BAD_REQUEST, "bad where clause")

        for expr in exprs:
            col = expr[0]

            op = {
                "==":"__eq__",
                "!=":"__ne__",
                 ">":"__gt__",
                ">=":"__ge__",
                 "<":"__lt__",
                "<=":"__le__",
                "||":"in_",
            }[expr[1]]

            val = tuple(expr[2]) if op == "in_" else expr[2]

            query = query.filter(getattr(getattr(db.Question, col), op)(val))

    ### process clause: sort
    sort  = flask.request.args.get("sort")
    if sort:
        try:
            cols = dsl.sort(sort)
            resp.sort = sort
        except:
            raise webapp.Error(httplib.BAD_REQUEST, "bad sort clause")

        for col in cols:
            query = query.order_by(getattr(db.Question, col))

    ### process clause: start
    start  = flask.request.args.get("start")
    if start:
        try:
            start = int(start)
        except:
            raise webapp.Error(httplib.BAD_REQUEST, "bad start clause")
    else:
        start = 0
    resp.start = start
    query = query.filter(db.Question.id >= start)

    ### process clause: limit
    limit  = flask.request.args.get("limit")
    if limit:
        try:
            limit = int(limit)
        except:
            raise webapp.Error(httplib.BAD_REQUEST, "bad limit clause")
    else:
        limit = config.app.limit
    resp.limit = limit
    query = query.limit(limit)

    ### execute query and build response
    resp.questions = []
    for question in query.all():
        obj = ApiObject()
        resp.questions.append(obj)
        obj.id = question.id
        obj.op = question.op
        obj.n0 = question.n0
        obj.n1 = question.n1
        obj.n2 = question.n2
        obj.distractors = []
        for distractor in question.distractors:
            obj.distractors.append(distractor.n2)

    return resp
