# -*- coding:utf-8 -*-
#
import os
import json
import torndb
import tornado.web
import tornado.httpserver
import tornado.gen
import tornado.ioloop
from tornado.options import define, options
from tornado.httpclient import AsyncHTTPClient



define("port", default=8000, type=int, help="server port ")


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Server", "nzc")

    def initialize(self):
        pass

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_dict = json.loads(self.request.body)
        else:
            self.json_dict = None


class IndexHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        json_dict = yield self.get_ip_info("47.94.136.135")
        self.write(json_dict)

    @tornado.gen.coroutine
    def get_ip_info(self, ip):
        http = AsyncHTTPClient()
        resp = yield http.fetch("http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=json&ip="+ip)
        if resp.error:
            self.send_error(500)
        else:
            json_dict = json.loads(resp.body)
        raise tornado.gen.Return(json_dict)


class Application(tornado.web.Application):
    def __init__(self):
        urls = [
            (r"/", IndexHandler),
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            debug=True,
        )
        super(Application, self).__init__(handlers=urls, **settings)


if __name__ == '__main__':
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
