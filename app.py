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


def serve_template(templatename, **kwargs):
    mytemplate = mylookup.get_template(templatename)
    print(mytemplate.render(**kwargs))

import logging
logging.basicConfig()

urls = [
    (r"/", MainHandler),
]
"""
    (r"/admin", AdminHandler),
    (r"/question/add", AddQuestionHandler),
    (r"/question/(.*?)/delete", DeleteQuestionHandler),
    (r"/question/(.*?)/", QuestionHandler),
    #TODO no more question id
    (r"/question/(.*?)/option/add", AddOptionHandler),
    (r"/question/(.*?)/tag/update", UpdateQuestionTagHandler),
    (r"/option/(.*?)/update", UpdateOptionHandler),
    (r"/option/(.*?)/up", UpOptionHandler),
    (r"/option/(.*?)/delete", DeleteOptionHandler),
    (r"/review/add", AddReviewHandler),
    (r"/review/(.*?)/delete", DeleteReviewHandler),
    (r"/tag/(.*?)/", TagHandler),
    (r"/", MainHandler),
    (r"/tags/", TagTreeHandler),
"""
application = tornado.wsgi.WSGIApplication(urls, cookie_secret="__TODO:LIFE_IS_GOOD_BY_USING_TIAOYI")


if __name__ == "__main__":
	import config
	leancloud.init(config.leancloud_id, master_key=config.leancloud_key)
	port = config.port
	application.listen(port)
	tornado.ioloop.IOLoop.instance().start()
