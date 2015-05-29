# coding: utf-8

from gevent import monkey
monkey.patch_all()

import tornado.web
import tornado.wsgi
from controller import *
from mako.template import Template
from mako.lookup import TemplateLookup


mylookup = TemplateLookup(directories=['/docs'], module_directory='/tmp/mako_modules')

def serve_template(templatename, **kwargs):
    mytemplate = mylookup.get_template(templatename)
    print(mytemplate.render(**kwargs))

import logging
logging.basicConfig()

urls = [
    (r"/question/add", AddQuestionHandler),
    (r"/question/(.*?)/", QuestionHandler),
    (r"/question/(.*?)/option/add", AddOptionHandler),
    (r"/option/(.*?)/update", UpdateOptionHandler),
    (r"/review/add", AddReviewHandler),
    (r"/static", StaticHandler),
    (r"/", MainHandler),
]
application = tornado.wsgi.WSGIApplication(urls)


if __name__ == "__main__":
    port = 8888
    try:
        import config
        leancloud.init(config.leancloud_id, master_key=config.leancloud_key)
        port = config.port
    except:
        pass
        
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

