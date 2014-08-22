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
      <div><input style="width:200pt" type=text name="content"></input> <input type="submit" value="Search"></div>
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
        uri = self.request.get('content')
        results = self.fetch(uri)
        self.response.write('<p>Found %d tracks:</p>' % (len(results),))
        self.response.write('<ul>')
        for result in results:
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
                return self.spotify(result['artist'], result['name'])
            else:
                return '<p>Unable to fetch track info<p/>'
        return response

    def spotify(self, artist, track):
        baseurl = 'https://api.spotify.com/v1/search?'
        query = urllib.urlencode({'q': 'artist:%s track:%s' % (artist, track,), 'type': 'track'})
        result = []
        response = json.loads(urllib.urlopen(baseurl + query).read())
        for item in response['tracks']['items']:
            open_link = item['external_urls']['spotify']
            artists = ', '.join([artist['name'] for artist in item['artists']])
            track = item['name']
            album = item['album']['name']
            catalog = 'available' if 'US' in item['album']['available_markets'] else 'unavailable'
            result.append('<a href="%s">%s - %s [%s] (%s)</a>' % (open_link, artists, track, album, catalog))
        return result


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
