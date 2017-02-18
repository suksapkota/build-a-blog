#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                                       autoescape= True)

class Post(db.Model):
    title=db.StringProperty(required=True)
    art= db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class BlogFront(webapp2.RequestHandler):
    def get(self):
        arts=db.GqlQuery ("SELECT * From Post Order by created Desc Limit 5")
        t = jinja_env.get_template("front.html")
        content = t.render(arts=arts)
        self.response.write(content)


class NewPost(webapp2.RequestHandler):
    def get(self):
        t = jinja_env.get_template("newpost.html")
        content = t.render()
        self.response.write(content)


    def post(self):
        title=self.request.get("title")
        art= self.request.get("art")

        if title and art:
            a=Post(title= title, art=art)
            a.put()
            self.redirect("/blog/%s" % str(a.key().id()))

        else:
            error ="We need both a title and a body!"
            t = jinja_env.get_template("newpost.html")
            content = t.render(title= title, art=art,error=error)
            self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self,id):
        key=Post.get_by_id(int(id))
        t = jinja_env.get_template("permalink.html")
        content = t.render(key=key)
        if not key:
            self.error(404)
            return
        self.response.write(content)



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog/newpost', NewPost),
    ('/blog' ,BlogFront),
    webapp2.Route('/blog/<id:\d+>',ViewPostHandler)
], debug=True)
