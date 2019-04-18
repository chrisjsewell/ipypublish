""" serve HTML page
TODO the RevealServer setting should be available at front end
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import os
import signal
import webbrowser

from tornado import web, ioloop, httpserver, log, gen
from tornado.httpclient import AsyncHTTPClient
from traitlets import Bool, Unicode, Int
from ipypublish.postprocessors.base import IPyPostProcessor


class ProxyHandler(web.RequestHandler):
    """handler the proxies requests from a local prefix to a CDN"""

    @gen.coroutine
    def get(self, prefix, url):
        """proxy a request to a CDN"""
        proxy_url = "/".join([self.settings['cdn'], url])
        client = self.settings['client']
        client.fetch(proxy_url, callback=self.finish_get)
        response = yield client.fetch(proxy_url)

        for header in ["Content-Type", "Cache-Control",
                       "Date", "Last-Modified", "Expires"]:
            if header in response.headers:
                self.set_header(header, response.headers[header])
        self.finish(response.body)


class RevealServer(IPyPostProcessor):
    """Post processor designed to serve files

    Proxies reveal.js requests to a CDN if no local reveal.js is present
    """
    @property
    def allowed_mimetypes(self):
        return ("text/html")

    @property
    def requires_path(self):
        return True

    @property
    def logger_name(self):
        return "reveal-server"

    open_in_browser = Bool(
        True,
        help="Should the browser be opened automatically?"
    ).tag(config=True)

    reveal_cdn = Unicode(
        "https://cdnjs.cloudflare.com/ajax/libs/reveal.js/3.1.0",
        help="""URL for reveal.js CDN."""
    ).tag(config=True)

    reveal_prefix = Unicode(
        "reveal.js", help="URL prefix for reveal.js").tag(config=True)

    ip = Unicode(
        "127.0.0.1", help="The IP address to listen on.").tag(config=True)

    port = Int(
        8000, help="port for the server to listen on.").tag(config=True)

    def run_postprocess(self, stream, mimetype, filepath, resources):
        """Serve the build directory with a webserver."""

        if not filepath.exists():
            self.handle_error(
                'the target file path does not exist: {}'.format(
                    filepath), IOError)

        # TODO rewrite this as pathlib
        dirname, filename = os.path.split(str(filepath))

        handlers = [
            (r"/(.+)", web.StaticFileHandler, {'path': dirname}),
            (r"/", web.RedirectHandler, {"url": "/%s" % filename})
        ]

        if '://' in self.reveal_prefix or self.reveal_prefix.startswith("//"):
            # reveal specifically from CDN, nothing to do
            pass
        elif os.path.isdir(os.path.join(dirname, self.reveal_prefix)):
            # reveal prefix exists
            self.logger.info("Serving local %s", self.reveal_prefix)
            self.logger.info("Serving local %s", self.reveal_prefix)
        else:
            self.logger.info("Redirecting %s requests to %s",
                             self.reveal_prefix, self.reveal_cdn)
            self.logger.info("Redirecting %s requests to %s",
                             self.reveal_prefix, self.reveal_cdn)
            handlers.insert(0, (r"/(%s)/(.*)" %
                                self.reveal_prefix, ProxyHandler))

        app = web.Application(handlers,
                              cdn=self.reveal_cdn,
                              client=AsyncHTTPClient(),
                              )

        # hook up tornado logging to our self.logger
        log.app_log = self.logger

        http_server = httpserver.HTTPServer(app)

        # find an available port
        port_attempts = list(range(10))
        for port_attempt in port_attempts:
            try:
                url = "http://%s:%i/%s" % (self.ip, self.port, filename)
                self.logger.info("Attempting to serve at %s" % url)
                http_server.listen(self.port, address=self.ip)
                break
            except IOError:
                self.port += 1
        if port_attempt == port_attempts[-1]:
            self.handle_error(
                'no port available to launch slides on, '
                'try closing some slideshows',
                IOError)

        self.logger.info("Serving your slides at %s" % url)
        self.logger.info("Use Control-C to stop this server")

        # don't let people press ctrl-z, which leaves port open
        def handler(signum, frame):
            self.logger.info('Control-Z pressed, but ignored, use Control-C!')

        signal.signal(signal.SIGTSTP, handler)

        if self.open_in_browser:
            #  2 opens the url in a new tab
            webbrowser.open(url, new=2)

        try:
            ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            # dosen't look like line below is necessary
            ioloop.IOLoop.instance().stop()
            self.logger.info("\nInterrupted")

        return stream, filepath, resources
