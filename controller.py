from urlparse import urlparse
from model import *
import tornado.web
from mako.template import Template
from mako.lookup import TemplateLookup
from lib import urlnorm 
import sys
import traceback
from lib.utils import save_file
from model import People as User

mylookup = TemplateLookup(
	directories=['./templates'], 
    module_directory='/tmp/mako_modules',
    #disable_unicode=True,
    input_encoding='utf-8',
    output_encoding='utf-8',
    default_filters=['decode.utf8', 'h'],
    encoding_errors='replace'
)

def render(templatename, **kwargs):
    mytemplate = mylookup.get_template(templatename)
    return mytemplate.render(**kwargs)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        #from leancloud import User 
        user_id = self.get_secure_cookie('user')
        user = None
	admin = User().login('admin', 'lifeisgood')
	if user_id == admin.id:
	    return admin
        if user_id:
            user = User()
            user = user.login(user_id, 'test')
        if not user:
            user = User()
            import random
            rand = str(random.random())
            user.set('username', rand)
            user.set('password', 'test')
            user = user.sign_up()
            user.set('username', user.id)
            user.save()
            user = user.login(user.id, 'test')
            self.set_secure_cookie('user', user.id)
        return user 
            
    """
    def write_error(self, status_code, **kwargs):
        ## no print in product env
        #self.write(str(traceback.format_exc()))
	pass
    """

class AdminHandler(BaseHandler):
    def get(self):
        password = self.get_argument('password', '')
	if not password:
		self.redirect('/')

	user = User()
	user = user.login('admin', password)
	if user:
		self.set_secure_cookie('user', user.id)
        self.redirect('/')
        
class MainHandler(BaseHandler):
    def get(self):
	p = int(self.get_argument('p',0))
        questions, options, reviews = Question.hotest(p)
        self.write(render('main.html', questions=questions, options=options, reviews=reviews, p=p))

class AddQuestionHandler(BaseHandler):
    def get(self):
        self.write(render('add_question.html'))

    def post(self):
        title = self.get_argument('title').strip()
        if not title:
            self.redirect('/question/add')
        question = Question.add(title, self.get_current_user())
        self.redirect('/')

class QuestionHandler(BaseHandler):
    def get(self, id):
        question = Question.take(id)
        user = self.get_current_user()
        self.write(render('question.html', question=question, user=user))

class AddOptionHandler(BaseHandler):
    def get(self, question_id):
        question = Question.take(question_id)
        user = self.get_current_user()
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

        img = save_file(self.request.files)

        option = Option.add(title, author, question, link, nickname, img)
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
	if not option.can_edit(author) or not title:
            self.redirect('/option/%s/update' % option.id)
        img = save_file(self.request.files)
        option = option.update(title, link, review, img)
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

        
