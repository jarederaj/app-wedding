import os
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def globalVals(ctx):
    if users.get_current_user():
        url = users.create_logout_url(ctx.request.uri)
        linkText = 'Logout'
        notes = True;
        name = users.get_current_user().nickname()
    else:
        url = users.create_login_url(ctx.request.uri)
        linkText = 'Login'
        notes= False
        name = ""
    _get = ctx.request.GET
    return {
        'url': url,
        'linkText': linkText,
        'notes': notes,
        'name': name,
        '_get': _get,
    }



class MainPage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            linkText = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            linkText = 'Login'

        pageVars = globalVals(self)
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(pageVars))

def guestbook_key(guestbookName=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbookName."""
    return ndb.Key('Guestbook', guestbookName)

class Greeting(ndb.Model):
    """Models an individual Guestbook entry."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class RSVP(ndb.Model):
    """Models an individual RSVP entry."""
    author = ndb.UserProperty()
    fullName = ndb.StringProperty(indexed=False)
    nickname = ndb.StringProperty(indexed=False)
    note = ndb.TextProperty(indexed=False)
    willAttendWedding = ndb.TextProperty(indexed=False)
    willAttendReception = ndb.TextProperty(indexed=False)
    attendants = ndb.IntegerProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Response(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/rsvp.html')
        pageVars = globalVals(self)
        pageVars['title'] = "RSVP"
        self.response.write(template.render(pageVars))

    def post(self):
        guestbookName = self.request.get('guestbookName',
                                          DEFAULT_GUESTBOOK_NAME)
        rsvp = RSVP(parent=guestbook_key(guestbookName))

        if users.get_current_user():
            rsvp.author = users.get_current_user()

        rsvp.fullName = self.request.get('fullName')
        rsvp.nickname = self.request.get('nickname')
        rsvp.willAttendWedding = self.request.get('willAttendWedding')
        rsvp.willAttendReception = self.request.get('Wedding')
        rsvp.attendants = int(self.request.get('attendants'))
        rsvp.note = self.request.get('note')
        rsvp.put()
        self.redirect('/?msg=Thank you for submitting your RSVP')



class Registry(webapp2.RequestHandler):
    def get(self):
        guestbookName = self.request.get('guestbookName',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbookName)).order(-Greeting.date)
        greetings = greetings_query.fetch(100)

        pageVars = globalVals(self)
        pageVars['greetings'] =  greetings
        pageVars['guestbookName'] = urllib.quote_plus(guestbookName)

        template = JINJA_ENVIRONMENT.get_template('templates/registry.html')
        self.response.write(template.render(pageVars))

class Guestbook(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each Greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity group
        # should be limited to ~1/second.
        guestbookName = self.request.get('guestbookName',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbookName))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        queryParams = {'guestbookName': guestbookName}
        self.redirect('/?' + urllib.urlencode(queryParams))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/registry', Registry),
    ('/rsvp', Response),
    ('/responded', Response),
    ('/sign', Guestbook),
], debug=True)

#Empty view class
#class Response(webapp2.RequestHandler):
#    def get(self):
#        template = JINJA_ENVIRONMENT.get_template('templates/rsvp.html')
#        pageVars = globalVals(self)
#        self.response.write(template.render(pageVars))

