cherrymusic
===========

cherrymusic is a standalone music server based on CherryPy and jPlayer. It is intended to be an 
alternative to edna.

Current Features:

  - browse and stream your music inside the browser (locally or remote)
  - search your music
  - completely AJAX based (no page reloads on click, super fast)
  - create playlists
  - basic authentication for multiple users
    
Upcoming features:

  - saving and sharing playlists
  - searching ID3 tags

Getting Started
===============

1. Checkout or download the cherry music sources.

        $ mkdir cherrymusic
        $ git clone git://github.com/devsnd/cherrymusic.git ./cherrymusic
        $ cd cherrymusic

2. Copy the `config.sample` to `config` and modify to your wishes.

        $ cp config.sample config
        $ vi config

3. To use cherrymusic you need [CherryPy](http://www.cherrypy.org). 
Either install it using your favorite package-manager, or download it 
[straight from their website](http://download.cherrypy.org/cherrypy/3.2.2/) to install it 
yourself. To proceed without installing, just extract the `cherrypy` subfolder from the archive 
you downloaded into your cherrymusic folder. That's it. 

4. Now simply start the main script using python; it will prompt you for anything else.

        $ python cherrymusic.py

5. Open your browser and play some music!

        $ firefox localhost:8080

Side Notes
==========

By default it uses HTML5 for music playback and supports flash as fallback. 

Requirements
============
* [Python 3](http://python.org/download/releases/)
* [CherryPy](http://www.cherrypy.org)
