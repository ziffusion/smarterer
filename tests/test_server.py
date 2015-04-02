import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import urllib

import server.endpoints
from server.webapp import webapp
from datatypes.api_object import ApiObject
from utils import log, config

##############################################################################
#
##############################################################################

class Test(unittest.TestCase):

    def setUp(self):
        webapp.flask.config["TESTING"] = True
        self.client = webapp.flask.test_client()

    def tearDown(self):
        pass

    def response(self, response, code):
        self.assertEqual(response.headers["content-type"], "application/json")
        self.assertEqual(response.status_code, code)
        return ApiObject(response.data)

    def rest(self, method, path, query, obj, code):
        if query: path += "?" + urllib.urlencode(query)
        kwargs = {"headers":{"content-type":"application/json"}}
        if obj: kwargs["data"] = obj.encode()
        response = getattr(self.client, method)(path, **kwargs)
        return self.response(response, code)

    def get(self, path, query, code):
        return self.rest("get", path, query, None, code)

    def post(self, path, query, obj, code):
        return self.rest("post", path, query, obj, code)

    def put(self, path, query, obj, code):
        return self.rest("put", path, query, obj, code)

    def delete(self, path, query, code):
        return self.rest("delete", path, query, None, code)

    def test_api(self):
        ### GET: query
        obj = self.get("/question", None, 200)
        obj = self.get("/question", {"where":"n0 > 3008"}, 200)
        obj = self.get("/question", {"where":"n0 || 1754 3009"}, 200)
        obj = self.get("/question", {"where":"n0 || 1754 3009 && op || *"}, 200)
        obj = self.get("/question", {"where":"n0 > 500", "sort":"op", "start":2, "limit":"2"}, 200)
        obj = self.get("/question", {"where":"n0 > 500", "sort":"op", "start":2, "limit":"2"}, 200)

        ### DELETE
        obj = self.delete("/question/3", None, 200)

        ### GET: validate
        obj = self.get("/question/3", None, 404)
        self.assertEqual(obj.code, 404)

        ### GET
        obj = self.get("/question/2", None, 200)
        self.assertEqual(obj.question.distractors, [3572, 8772, 9415])
        self.assertEqual(obj.question.id, 2)
        self.assertEqual(obj.question.n0, 3009)
        self.assertEqual(obj.question.n1, 5075)
        self.assertEqual(obj.question.n2, 15270675)
        self.assertEqual(obj.question.op, "*")

        ### POST: update
        obj = ApiObject()
        obj.distractors = [5, 6, 7]
        obj.n0 = 1
        obj.n1 = 2
        obj.n2 = 3
        obj.op = "+"
        obj = self.post("/question/2", None, obj, 200)

        ### GET: validate
        obj = self.get("/question/2", None, 200)
        self.assertEqual(obj.question.distractors, [5, 6, 7])
        self.assertEqual(obj.question.id, 2)
        self.assertEqual(obj.question.n0, 1)
        self.assertEqual(obj.question.n1, 2)
        self.assertEqual(obj.question.n2, 3)
        self.assertEqual(obj.question.op, "+")

        ### PUT: create
        obj = ApiObject()
        obj.distractors = [50, 60, 70]
        obj.n0 = 10
        obj.n1 = 20
        obj.n2 = 30
        obj.op = "+"
        obj = self.put("/question", None, obj, 200)
        id = obj.question.id

        ### GET: validate
        obj = self.get("/question/" + str(id), None, 200)
        self.assertEqual(obj.question.distractors, [50, 60, 70])
        self.assertEqual(obj.question.id, id)
        self.assertEqual(obj.question.n0, 10)
        self.assertEqual(obj.question.n1, 20)
        self.assertEqual(obj.question.n2, 30)
        self.assertEqual(obj.question.op, "+")
