#!/usr/bin/python3
#
# CherryMusic - a standalone music server
# Copyright (c) 2012 Tom Wallroth & Tilman Boerner
#
# Project page:
#   http://fomori.org/cherrymusic/
# Sources on github:
#   http://github.com/devsnd/cherrymusic/
#
# CherryMusic is based on
#   jPlayer (GPL/MIT license) http://www.jplayer.org/
#   CherryPy (BSD license) http://www.cherrypy.org/
#
# licensed under GNU GPL version 3 (or later)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

"""This class provides the api to talk to the client.
It will then call the cherrymodel, to get the 
requested information"""

import os #shouldn't have to list any folder in the future!
import json
import cherrypy

from cherrymusic import renderjson
from cherrymusic import userdb
from cherrymusic import playlistdb
import cherrymusic as cherry
from urllib import parse

debug = True


class HTTPHandler(object):
    def __init__(self, config, model):
        self.model = model
        self.config = config
        self.jsonrenderer = renderjson.JSON()
        self.mainpage = open('res/main.html').read()
        self.loginpage = open('res/login.html').read()
        self.firstrunpage = open('res/firstrun.html').read()
        self.userdb = userdb.UserDB()
        self.playlistdb = playlistdb.PlaylistDB()

    def issecure(self, url):
        return parse.urlparse(url).scheme == 'https'
        
    def getSecureUrl(self,url):
        u = parse.urlparse(url).netloc
        ip = u[:u.index(':')]
        return 'https://'+ip+':'+cherry.config.server.ssl_port.str

    def index(self, action='', value='', filter='', login=None, username=None, password=None):
        
        if cherry.config.server.use_ssl.bool and not self.issecure(cherrypy.url()):
            print('Not secure, redirecting...')
            raise cherrypy.HTTPRedirect(self.getSecureUrl(cherrypy.url()),302)
            
        firstrun = 0 == self.userdb.getUserCount();
        if debug:
            #reload pages everytime in debig mode
            self.mainpage = open('res/main.html').read()
            self.loginpage = open('res/login.html').read()
            self.firstrunpage = open('res/firstrun.html').read()
        if login == 'login':
            self.session_auth(username,password)
            if cherrypy.session['username']:
                print('user '+cherrypy.session['username']+' just logged in.')
        elif login == 'create admin user':
            if firstrun:
                if username.strip() and password.strip():
                    self.userdb.addUser(username, password, True)
                    self.session_auth(username,password)
                    return self.mainpage
            else:
                return "No, you can't."
        if firstrun:
                return self.firstrunpage
        else:
            if cherrypy.session.get('username', None):
                return self.mainpage
            else:
                return self.loginpage
    index.exposed = True

    def session_auth(self, username, password):
        userid, authuser, isadmin = self.userdb.auth(username,password)
        cherrypy.session['username'] = authuser
        cherrypy.session['userid'] = userid
        cherrypy.session['admin'] = isadmin

    def api(self, action='', value='', filter=''):
        return self.handle(self.jsonrenderer, action, value, filter)
    api.exposed = True
    
    def handle(self, renderer, action, value, filter):
        if action=='search':
            if not value.strip():
                return """<span style="width:100%; text-align: center; float: left;">if you're looking for nothing, you'll be getting nothing.</span>"""
            return renderer.render(self.model.search(value.strip()))
        elif action == 'getmotd':
            return self.model.motd()
        elif action == 'rememberplaylist':
            pl = json.loads(value)
            cherrypy.session['playlist'] = pl['playlist']
        elif action == 'restoreplaylist':
            return json.dumps(cherrypy.session.get('playlist',[]))
        elif action == 'saveplaylist':
            pl = json.loads(value)
            return self.playlistdb.savePlaylist(
                userid = cherrypy.session['userid'],
                public = 1 if pl['public'] else 0,
                playlist = pl['playlist'],
                playlisttitle = pl['playlistname']);
        elif action == 'loadplaylist':
            return  json.dumps(self.playlistdb.loadPlaylist(
                                playlistid=value,
                                userid=cherrypy.session['userid']
                    ));
        elif action == 'showplaylists':
            return json.dumps(self.playlistdb.showPlaylists(cherrypy.session['userid']));
        elif action == 'logout':
            cherrypy.lib.sessions.expire()
        elif action == 'getuserlist':
            if cherrypy.session['admin']:
                return json.dumps(self.userdb.getUserList())
            else:
                return {'id':'-1','username':'nobody','admin':0}
        elif action == 'adduser':
            if cherrypy.session['admin']:
                new = json.loads(value)
                return self.userdb.addUser(new['username'],new['password'],new['isadmin'])
            else:
                return "You didn't think that would work, did you?"
        else:
            dirtorender = value
            dirtorenderabspath = os.path.join(cherry.config.media.basedir.str,value)
            if os.path.isdir(dirtorenderabspath):
                if action=='compactlistdir':
                    return renderer.render(self.model.listdir(dirtorender,filter))
                else: #if action=='listdir':
                    return renderer.render(self.model.listdir(dirtorender))
            else:
                return 'Error rendering dir [action: "'+action+'", value: "'+value+'"]'