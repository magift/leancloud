from urlparse import urlparse
from model import *
import tornado.web
from mako.template import Template
from mako.lookup import TemplateLookup
from lib import urlnorm 
import sys
import traceback

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
        user_id = self.get_secure_cookie('user')
        user = User()
        if user_id:
            user.login(user_id, 'test')
        else:
            import random
            rand = str(random.random())
            user.set('username', rand)
            user.set('password', 'test')
            user.sign_up()
            user.login(rand, 'test')
            self.set_secure_cookie('user', rand)
        return user 
            
    def write_error(self, status_code, **kwargs):
        ## no print in product env
        self.write(str(traceback.format_exc()))

class MainHandler(BaseHandler):
    def get(self):
        questions, options, reviews = Question.hotest()
        self.write(render('main.html', questions=questions, options=options, reviews=reviews))

class AddQuestionHandler(BaseHandler):
    def get(self):
        self.write(render('add_question.html'))

    def post(self):
        title = self.get_argument('title').strip()
        if not title:
            self.redirect('/question/add')
        question = Question.add(title, self.get_current_user())
        #self.redirect('/question/%s/' % question.id)
        self.redirect('/')

class QuestionHandler(BaseHandler):
    def get(self, id):
        question = Question.take(id)
        user = self.get_current_user()
        self.write(render('question.html', question=question, user=user))

class AddOptionHandler(BaseHandler):
    def get(self, question_id):
        question = Question.take(question_id)
        ##user = self.get_current_user()

        import random
        from leancloud import User
        rand = str(random.random())
        user = User()
        user.set('username', rand)
        user.set('password', 'test')
        user.sign_up()
        user = User()
        user.login(rand, 'test')
        user.set('nickname', 'haha')
        user.save()

        self.write(render('add_option.html', question=question, user=user))

    def post(self, question_id):
        question = Question.take(question_id)
        author = self.get_current_user()
        title = self.get_argument('title').strip()
        review = self.get_argument('review').strip()
        link = self.get_argument('link').strip()
        link = urlnorm.norms(link)
        nickname = self.get_argument('nickname')
        if not title: 
            self.redirect('/question/%s/option/add' % question.id)
        if nickname:
            author.set('nickname', nickname)
            author.save()
        option = Option.add(title, author, question, link)
        if review:
                review = Review.add(review, author, option)
        self.redirect('/question/%s/' % question.id)

class UpdateOptionHandler(BaseHandler):
    def get(self, option_id):
        option = Option.take(option_id)
        question = option.question
        self.write(render('update_option.html', option=option, question=question))

    def post(self, option_id):
        option = Option.take(option_id)
        question = option.question
        author = self.get_current_user()
        title = self.get_argument('title').strip()
        review = self.get_argument('review').strip()
        link = self.get_argument('link').strip()
        link = urlnorm.norms(link)
        if not title: 
            self.redirect('/option/%s/update' % option.id)
        option = option.update(title, link, review)
        self.redirect('/question/%s/' % question.id)

class StaticHandler(BaseHandler):
    def get(self):
        questions = Question.get_date_news()
        option = Option.get_date_news()
        self.write(render('static.html', questions=questions, option=option))

class AddReviewHandler(BaseHandler):
    def post(self):
        option_id = self.get_argument('oid')
        option = Option.take(option_id)
        title = self.get_argument('title')
        Review.add(title=title, author=self.get_current_user(), option=option
)
        self.redirect('/question/%s/' % option.question.id)

        
