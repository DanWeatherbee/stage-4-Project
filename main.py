import os
import jinja2
import webapp2
import cgi
import urllib
from time import sleep
from google.appengine.api import users
from google.appengine.ext import ndb

# I had a lot of fun with this and
# have at least 20 versions on my desktop :)

# Set up Jinja environment

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                            autoescape = False)
# I escaped all the fields inside the APP rather than
# using Jinjas autoescape because I got unwanted results in
# the posts after it rendered.

DEFAULT_WALL = 'Public'
my_notes ='''
  I am close to completing my nanodgree in front end programming.

  I am creating an APP that uses the Google Cloud Platform.
  There are no traditional databases, it uses whats called the
   Google data store using there mega infrastructure.

  The APP is extremely scalable.

  The Database can grow forever and still deliver your data in a
  second and its persistent data.

  Several years from now every post would be there for you to
   iterate through and grab what data you want, like facebook's
    time-line.

  I have one page of code that creates the database object and
   fills in the custom fields with the data from the
    text box of the post.

  The code includes a web page generator that writes pages on
   the fly and renders it for you to see.

  Its all in memory(no actual pages!).

  Your wall or page is rendered with the data collected
   from the database useing the code just put there and
   then self directs you to that page.

  This is how facebook can cross the world  and the data is
   consistent and quick regardless of how many users input
    at what time or how many country's or servers.

  It stays lightning quick and will not collapse at
   a million users (that number is not exaggerated).

  Many CMS Platforms use a lot of different languages that
   must be updated and are limited because not every server
   has the required languages.

  Python is found on nearly all servers along with HTML CSS
   Java and templates.

  This APP utilizes all of that.

  All the code is separated to its perspective file.

  There is no HTML in your Python and so on.

  This keeps your site hack proof.

  The text box input is also cgi escaped to
  remove unwanted characters from would be hacker posts.

  List of note worthy errors, causes and fixes;

  Bug 1

    unbound method notes_method() must be called with
    ClassNotes instance as first argument (got nothing instead)

    cause: forgot brackets () on the end of a function.

  Bug 2

    cause:

     Tried to split a statement into two lines at the plus sign.

  fix;
    Use triple quotes.

     have to flush the engine and delete tables to get it to load again,
     sometimes stopping and starting as an extra measure.

  bug 3

    cause;

    It seams Jinja does not like it when I indent code
      inside of a form. This bug got me good :).
    It some how breaks my Python code or over rides it more
     likely I am thinking.

    Fix:

    Unindented the code. This makes me more cautious about indenting
     HTML in Jinja.

    Reference;

    This video helped a lot understanding the get and post requests.

    https://www.youtube.com/watch?v=bfgO-LXGpTM video on appengine.

    p.s.

      I wanted error detection for white space but I did not
        want to give up the formating.
        # Lession 4.7: Escaping Templates

    Udacity Quote to remember; Escaping HTML characters is an important
     function to learn because this prevents unintended HTML code from
     rendering on the browser, stopping malicious users from
      abusing your site.
  '''

# I found this pseudo code to be necessary for reference.
# So I left it here.
# We set a parent key on the 'Post' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent.  However, the write rate should be limited to
# ~1/second.

def wall_key(wall_name=DEFAULT_WALL):
  """Constructs a Datastore key for a Wall entity.

  We use wall_name as the key.
  """
  return ndb.Key('Wall', wall_name)

# These are the objects that will represent our Author and our Post. We're using
# Object Oriented Programming to create objects in order to put them in Google's
# Database. These objects inherit Googles ndb.Model class.
class Author(ndb.Model):
  """Sub model for representing an author."""
  identity = ndb.StringProperty(indexed=True)
  name = ndb.StringProperty(indexed=False)
  email = ndb.StringProperty(indexed=False)

class Post(ndb.Model):
  """A Sub model for representing an individual post entry."""

  author = ndb.StructuredProperty(Author)
  content = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):

  def get(self):

    wall_name = self.request.get('wall_name',DEFAULT_WALL)
    # Here I make sure users do not enter HTML in the wall variable.
    wall_name = cgi.escape(wall_name)
    # Here I keep the wall name clean without white space front and back.
    wall_name = wall_name.strip()

    # This is my validation method for the wall input.
    if len(wall_name) < 1 or len(wall_name) > 15:
      sign_query_params = urllib.urlencode({'wall_name': wall_name})

      template_values = {'sign_query_params' : (sign_query_params)}

      # Here is where I had to learn how to load a template properly.
      # I watched the appengine video and video on Jinja Templating
      # and got through it.

      template = jinja_env.get_template('error_wall.html')

      self.response.out.write(template.render(template_values))
    else:

      if wall_name == DEFAULT_WALL.lower():
       wall_name = DEFAULT_WALL

      else:
          # Ancestor Queries, as shown here, are strongly consistent
          # with the High Replication Datastore. Queries that span
          # entity groups are eventually consistent. If we omitted the
          # ancestor from this query there would be a slight chance that
          # Greeting that had just been written would not show up in a
          # query.

          # [START query]
          posts_query = Post.query(ancestor = wall_key(wall_name)).order(-Post.date)

          # The function fetch() returns all posts that satisfy our query. The function returns a list of
          # post objects
          posts =  posts_query.fetch()
          # [END query]

          # If a person is logged into Google's Services
          user = users.get_current_user()
      if user:
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
          user_name = user.nickname()
      else:
          url = users.create_login_url(self.request.uri)
          url_linktext = 'Login'
          user_name = 'Anonymous Poster'

      # Create our posts html
      posts_html = ''

      for post in posts:
        # Check if the current signed in user matches with the author's identity from this particular
        # post. Newline character '\n' tells the computer to print a newline when the browser is
        # is rendering our HTML
          if user and user.user_id() == post.author.identity:
            posts_html += '''<h3>You</h3><div class="msg_box"><h3>
            ''' + post.author.name  + '</h3></div>\n'
          else:
            posts_html += '''<div class="msg_box"><div class="author"><h3>
            ''' + post.author.name  + '</h3></div><p>\n'
          posts_html += '''
                        <div class="wrote">wrote:</div><blockquote>&nbsp;&nbsp;&nbsp;<pre>
                        ''' +  cgi.escape(post.content) + '''
                        &nbsp;&nbsp;&nbsp;</blockquote></pre>\n
                        '''
          posts_html += '</div><p>\n'


      sign_query_params = urllib.urlencode({'wall_name': wall_name})
      choose = 'Choose a wall to Post on.'
      wall_label = 'Wall:'
      wall_label += wall_name
      template_values = {'sign_query_params' : (sign_query_params),
                         'wall_name' : (wall_name),
                         'user_name' : (user_name), 'url' : (url),
                         'url_linktext' : (url_linktext),
                         'posts_html' : (posts_html),
                         'choose' : (choose),
                         'wall_label' : (wall_label),
                         'my_notes' : (my_notes)
                         }
      # This is the code for the value in the dictionary
      # I am going to need this to change toggle validated values.

      template = jinja_env.get_template('index.html')
      # Write Out Page here
      self.response.out.write(template.render(template_values))


class PostWall(webapp2.RequestHandler):

  def post(self):
    # We set the same parent key on the 'Post' to ensure each
    # Post is in the same entity group. Queries across the
    # single entity group will be consistent. However, the write
    # rate to a single entity group should be limited to
    # ~1/second.
    wall_name = self.request.get('wall_name',DEFAULT_WALL)

    post = Post(parent=wall_key(wall_name))
    # When the person is making the post, check to see whether the person
    # is logged into Google
    if users.get_current_user():
      post.author = Author(
            identity=users.get_current_user().user_id(),
            name=users.get_current_user().nickname(),
            email=users.get_current_user().email())
    else:
      post.author = Author(
            name='anonymous@anonymous.com',
            email='anonymous@anonymous.com')
    # Get the content from our request parameters, in this case, the message
    # is in the parameter 'content' and strip the white space front and back.
    post.content = self.request.get('content')
    no_space = post.content
    post.content = no_space.strip()

    # Here I prevent the user from a: leaving no input and b: too many characters
    # witch i tested and it broke therefore I needed protection.

    if len(post.content) < 1 or len(post.content) > 1000:
      sign_query_params = urllib.urlencode({'wall_name': wall_name})

      template_values = {'sign_query_params' : (sign_query_params),
                         'wall_name' : (wall_name)}
      # Here is where I had to learn how to load a template properly.
      # I watched the appengine video and video on Jinja Templating
      # and got through it.

      template = jinja_env.get_template('error.html')

      self.response.out.write(template.render(template_values))

    else:

      post.put()
      # This was suggested in the above statement on large query's.
      # the write rate should be limited to
      # ~1/second. I think I put it in the right place :).
      sleep(.5)

      self.redirect('/?wall_name=' + wall_name)

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/index', PostWall), ('/admin', PostWall)
], debug=True)