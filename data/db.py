import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re

from flask.ext.sqlalchemy import SQLAlchemy

from server.webapp import webapp
from utils import config, log

##############################################################################
# db init
##############################################################################

try:
    os.remove(config.db.path)
except:
    pass

webapp.flask.config["SQLALCHEMY_DATABASE_URI"] = config.db.uri

db = SQLAlchemy(webapp.flask)

##############################################################################
# dbo
##############################################################################

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    op = db.Column(db.Enum("+", "-", "*", "/", name="op"))
    n0 = db.Column(db.Integer)
    n1 = db.Column(db.Integer)
    n2 = db.Column(db.Integer)
    distractors = db.relationship("Distractor", backref="question")

class Distractor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n2 = db.Column(db.Integer)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))

##############################################################################
# create schema
##############################################################################

db.create_all()

##############################################################################
# import data
##############################################################################

data = os.path.join(config.path.data, config.db.data)

with open(data, "r") as fileo:
    for line in fileo:
        break

    for line in fileo:
        tok = line.split("|")

        question = tok[0].strip()
        match = re.match("^what\s+is\s+(\d+)\s*([*/+-])\s*(\d+)\s*[?]$", question, flags=re.IGNORECASE)
        op = match.group(2)
        n0 = int(match.group(1))
        n1 = int(match.group(3))
        n2 = int(tok[1].strip())

        dbo_question = Question(op=op, n0=n0, n1=n1, n2=n2)
        db.session.add(dbo_question)

        for n2 in tok[2].strip().split(","):
            dbo_distractor = Distractor(n2=int(n2.strip()))
            dbo_distractor.question = dbo_question
            db.session.add(dbo_distractor)

    db.session.commit()
