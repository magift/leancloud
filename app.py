# coding: utf-8

try:
    from gevent import monkey
    monkey.patch_all()
except:
    print 'no use gevent'
    pass

import tornado.web
import tornado.wsgi
from controller import *
from mako.template import Template
from mako.lookup import TemplateLookup


mylookup = TemplateLookup(
    directories=['/docs'], 
    module_directory='/tmp/mako_modules',
    disable_unicode=True,
    input_encoding='utf-8',
    output_encoding='utf-8',
    default_filters=['decode.utf8'],
    encoding_errors='replace'
)

def serve_template(templatename, **kwargs):
    mytemplate = mylookup.get_template(templatename)
    print(mytemplate.render(**kwargs))

import logging
logging.basicConfig()

urls = [
    (r"/admin", AdminHandler),
    (r"/question/add", AddQuestionHandler),
    (r"/question/(.*?)/", QuestionHandler),
    (r"/question/(.*?)/option/add", AddOptionHandler),
    (r"/option/(.*?)/update", UpdateOptionHandler),
    (r"/option/(.*?)/up", UpOptionHandler),
    (r"/review/add", AddReviewHandler),
    (r"/", MainHandler),
]
application = tornado.wsgi.WSGIApplication(urls, cookie_secret="__TODO:LIFE_IS_GOOD_BY_USING_TIAOYI")


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

