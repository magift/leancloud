from urlparse import urlparse
from model import *
import tornado.web
from mako.template import Template
from mako.lookup import TemplateLookup
from lib import urlnorm 

mylookup = TemplateLookup(
	directories=['./templates'], 
#	module_directory='/tmp/mako_modules',
#	collection_size=500, 
	input_encoding='utf-8',
	output_encoding='utf-8', 
	encoding_errors='replace',
    default_filters=['h'],
)

def render(templatename, **kwargs):
    mytemplate = mylookup.get_template(templatename)
    return mytemplate.render(**kwargs)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        from leancloud import User 
        QIU_USER = User()
        QIU_USER.login("test2", "test2")
        return QIU_USER

class MainHandler(BaseHandler):
    def get(self):
        questions = Question.hotest()
        self.write(render('main.html', questions=questions))

class AddQuestionHandler(BaseHandler):
    def get(self):
        self.write(render('add_question.html'))

    def post(self):
        title = self.get_argument('title').strip()
        if not title:
            self.redirect('/question/add')
        question = Question.add(title, self.current_user)
        #self.redirect('/question/%s/' % question.id)
        self.redirect('/')

class QuestionHandler(BaseHandler):
    def get(self, id):
        question = Question.take(id)
        self.write(render('question.html', question=question))

class AddOptionHandler(BaseHandler):
    def get(self, question_id):
        question = Question.take(question_id)
        self.write(render('add_option.html', question=question
))

    def post(self, question_id):
        question = Question.take(question_id)
        author = self.current_user
        title = self.get_argument('title').strip()
        review = self.get_argument('review').strip()
        link = self.get_argument('link').strip()
        link = urlnorm.norms(link)
        if not title: 
            self.redirect('/question/%s/option/add' % question.id)
        option = Option.add(title, author, question, link)
        if review:
                review = Review.add(review, author, option)
        self.redirect('/question/%s/' % question.id)

class StaticHandler(BaseHandler):
    def get(self):
        questions = Question.get_date_news()
        options = Option.get_date_news()
        self.write(render('static.html', questions=questions, options=options))

class AddReviewHandler(BaseHandler):
    def post(self):
        option_id = self.get_argument('oid')
        option = Option.take(option_id)
        title = self.get_argument('title')
        Review.add(title=title, author=self.current_user, option=option
)
        self.redirect('/question/%s/' % option.question.id)

        
