import cgi
import urllib
import oauth2 as oauth
import json

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

MAIN_PAGE_HEADER_TEMPLATE = """\
<html><body>
    <form action="/" method="post">
      <div><input style="width:200pt" type=text name="content"></input> <input type="submit" name="rdio" value="Rdio link"><input type="submit" name="spotify" value="Search Spotify"></div>
    </form>
"""
MAIN_PAGE_FOOTER_TEMPLATE = """\
  </body>
</html>
"""

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(MAIN_PAGE_HEADER_TEMPLATE)
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE)

    def post(self):
        self.response.write(MAIN_PAGE_HEADER_TEMPLATE)
        if self.request.get('spotify'):
            query = self.request.get('content')
            available, unavailable = self.spotify(query=query)
        else:
            uri = self.request.get('content')
            available, unavailable = self.fetch(uri)

        self.response.write('<p>Found %d track%s:</p>' % (len(available), 's' if len(available) > 1 else ''))
        self.response.write('<ul>')
        for result in available:
            self.response.write('<li>%s</li>' % (result,))
        self.response.write('</ul>')

        self.response.write('<span>Unavailable tracks:</span>')
        self.response.write('<ul>')
        for result in unavailable:
            self.response.write('<li>%s</li>' % (result,))
        self.response.write('</ul>')

        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE)

    def fetch(self, url):
        client = oauth.Client(oauth.Consumer('fxmhxjk9g4dhvsnmb8m376yy', 'azNqD6Cft7'))
        response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'getObjectFromUrl', 'url': url}))
        parsed = json.loads(response[1])
        if 'result' in parsed:
            result = parsed['result']
            if 'artist' in result:
                return self.spotify(artist=result['artist'], track=result['name'])
            else:
                return '<p>Unable to fetch track info<p/>'
        return response

    def spotify(self, query=None, artist=None, track=None):
        baseurl = 'https://api.spotify.com/v1/search?'
        search = '%s %s %s' % (query if query else '', 'artist:%s' % artist if artist else '', 'track:%s' % track if track else '')
        query = urllib.urlencode({'q': search.strip(), 'type': 'track'})
        available = []
        unavailable = []
        response = json.loads(urllib.urlopen(baseurl + query).read())
        for item in response['tracks']['items']:
            open_link = item['external_urls']['spotify']
            artists = ', '.join([artist['name'] for artist in item['artists']])
            track = item['name']
            album = item['album']['name']
            if 'US' in item['album']['available_markets']:
                available.append('<a href="%s">%s - %s [%s]</a>' % (open_link, artists, track, album))
            else:
                unavailable.append('<a href="%s">%s - %s [%s]</a>' % (open_link, artists, track, album))

        return available, unavailable


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
