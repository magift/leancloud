#coding=utf8
from urlparse import urlparse
from model import *
import tornado.web
from mako.template import Template
from mako.lookup import TemplateLookup
from lib import urlnorm 
import sys
import re
import traceback
from lib.utils import save_file, pager
import lib.utils as utils
from model import People as User

mylookup = TemplateLookup(
	directories=['./templates'], 
    #module_directory='/tmp/mako_modules',
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
            
    def write_error(self, status_code, **kwargs):
        ## no print in product env
        #self.write(str(traceback.format_exc()))
	pass

class MainHandler(BaseHandler):
    def get(self):
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        token = 'lifeisgood'
        array = [token, timestamp, nonce]
        array.sort()
        array = ''.join(array)
        import hashlib
        sha1=hashlib.sha1()
        map(sha1.update,array)
        hashcode=sha1.hexdigest()

        if hashcode == signature:
                self.write(self.get_argument('echostr', ''))
        else:
                self.write('hehe')

    def post(self):
        body = self.request.body.decode('utf-8')
        self.write(str(body))

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
        tag = self.get_argument('tag', '').strip()
        tags = Tag.tops()
        if tag == '':
            questions, options, reviews = Question.hotest(p)
        else:
            if tag not in [i.get('title') for i in tags[:3]]:
                temp = tags[2]
                for j, t in enumerate(tags):
                    if t.get('title') == tag:
                        tags[2] = t
                        tags[j] = temp
                        
            tag2question = Tag2Question.gets_by_tag(tag, p)
            questions = [i.get('question') for i in tag2question] 
            options, reviews = Question.get_other_by_questions(questions)
        prev, next = pager(self.request.uri, p)
        is_mobile = utils.is_mobile(self.request)

        tag_tree = []
        if tag == '' and p == 0:
            tag_tree = Tag.get_tree()
        self.write(render('main.html', questions=questions, options=options, reviews=reviews, tags=tags, tag=tag, prev=prev, next=next, is_mobile=is_mobile, tag_tree=tag_tree, user=self.get_current_user()))

class TagTreeHandler(BaseHandler):
    def get(self):
        tag_tree = Tag.get_tree()
        self.write(render('tag_tree.html', tag_tree=tag_tree, user=self.get_current_user()))

class AddQuestionHandler(BaseHandler):
    def get(self):
        self.write(render('add_question.html'))

    def post(self):
        title = self.get_argument('title').strip()
        if not title:
            self.redirect('/question/add')
        question = Question.add(title, self.get_current_user())
        self.redirect('/')

class DeleteQuestionHandler(BaseHandler):
    def get(self, qid):
        question = Question.take(qid)
        if question and question.can_delete(self.get_current_user()):
            Question.delete(qid)
        self.redirect('/')

class DeleteOptionHandler(BaseHandler):
    def get(self, id):
        option = Option.take(id)
        if option and option.can_delete(self.get_current_user()):
            Option.delete(id)
        self.redirect('/question/%s/' % option.question.id)

class DeleteReviewHandler(BaseHandler):
    def get(self, id):
        review = Review.take(id)
        qid = review.question.id
        if review and review.can_delete(self.get_current_user()):
            Review.delete(id)
        self.redirect('/question/%s/#%s' % (qid, review.option.id))

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
        review = self.get_argument('review', '').strip()
        link = self.get_argument('link', '').strip()
        link = urlnorm.norms(link)
        nickname = self.get_argument('nickname', '')
        if not title: 
            return self.redirect('/question/%s/option/add' % question.id)
        author.update_nickname(nickname)

        img = save_file(self.request.files)

        option = Option.add(title, author, question, link, nickname, img)
        if review:
            Review.add(review, author, option, nickname)
        return self.redirect('/question/%s/#%s' % (question.id, option.id))

class UpdateOptionHandler(BaseHandler):
    def get(self, option_id):
        option = Option.take(option_id)
        question = option.question
        user = self.get_current_user()
        self.write(render('update_option.html', option=option, question=question, user=user))

    def post(self, option_id):
        option = Option.take(option_id)
        question = option.question
        author = self.get_current_user()
        title = self.get_argument('title').strip()
        link = self.get_argument('link').strip()
        link = urlnorm.norms(link)
        if not option.can_edit(author) or not title:
            self.redirect('/option/%s/update' % option.id)
        img = save_file(self.request.files)
        option = option.update(title, link, img)
        self.redirect('/question/%s/#%s' % (question.id, option.id))


class AddReviewHandler(BaseHandler):
    def post(self):
        option_id = self.get_argument('oid')
        option = Option.take(option_id)
        title = self.get_argument('title').strip()
        nickname = self.get_argument('nickname', '').strip()
        author = self.get_current_user()

        if title:
            review = Review.add(title=title, author=author, option=option)
        if nickname:
            author.update_nickname(nickname)

        self.redirect('/question/%s/#%s' % (option.question.id,review.id))

class UpOptionHandler(BaseHandler):        
    def post(self, option_id):
        user = self.get_current_user()
        option = Option.take(option_id)
        option.up(user)
        self.write(str(len(option.get('vote_users'))))
        #self.redirect('/question/%s/#%s' % (option.question.id, option.id))

class UpdateQuestionTagHandler(BaseHandler):
    def post(self, question_id):
        question = Question.take(question_id)
        tags = self.get_argument('tags').strip()
        Tag2Question.update(question, tags)
        self.redirect('/question/%s/' % (question.id))
        
class TagHandler(BaseHandler):
    def get(self, tag):
        tag = tag.strip()
        tag2question = Tag2Question.gets_by_tag(tag)
        questions = [i.get('question') for i in tag2question] 
        questions = [i for i in questions if i]
        options, reviews = Question.get_other_by_questions(questions)
        self.write(render('tag.html', questions=questions, tag=tag, options=options, reviews=reviews))

"""
