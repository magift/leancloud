from datetime import datetime, timedelta
import leancloud
from leancloud import Object
from leancloud import LeanCloudError
from leancloud import Query


PAGE_SIZE = 30

class Data(Object):
    @property
    def title(self):
        return self.get('title')

    @classmethod
    def take(cls, id):
        query = Query(cls)
        return query.get(id)

    @property
    def createdAt(self):
        return self.created_at.replace(tzinfo=None) + timedelta(hours=8)
        

    @property
    def author(self):
        return self.get('author')

    def can_edit(self, user):
	admin = People().login('admin', 'lifeisgood')
	author_id = self.author and self.author.id or None
	return author_id == user.id or user.id == admin.id

class Question(Data):
    #title; author; 
    @classmethod
    def add(cls, title, author):
        question = Question(title=title, author=author)
        question.save()
        return question


    @property
    def options(self):
        query = Query(Option) 
        options = query.equal_to('question', self).include('img')
        query.descending('updatedAt').descending('vote_users')
        return query.find()


    @classmethod
    def hotest(self, page=0):
        query = Query(Question)
        query.descending('updatedAt')
        questions = query.skip(page*PAGE_SIZE).limit(PAGE_SIZE).find()

        #TODO sql inject
        result = Query.do_cloud_query('select * from Option where question in (%s) order by createdAt desc limit 1000' % ','.join(["pointer('Question', '%s')" % i.id for i in questions]))
        result = result.results
        options = {}
        for r in result:
            if r.question.id not in [i for i in options.keys()]:
                options[r.question.id] = [r,]
            else:
                options[r.question.id].append(r)

        result = Query.do_cloud_query('select * from Review where option in (%s) order by createdAt desc limit 1000' % ','.join(["pointer('Option', '%s')" % i[0].id for i in options.values()]))
        result = result.results
        reviews = {}
        for r in  result:
            if r.option.id not in [i for i in reviews.keys()]:
                reviews[r.option.id] = r

        return questions, options, reviews

    @property
    def new_option(self):
        return self.options and self.options[0] or None

    
class Option(Data):
    #title;author;link;question;
    @classmethod
    def add(cls, title, author, question, link='', nickname='', img=None):
        option = Option(title=title, author=author, question=question, link=link, nickname=nickname, img=img)
        option.save()
        question.set('updatedAt', datetime.now())
        question.save()
        return option

    def update(self, title, link, review, img):
        self.set('title', title)
        self.set('link', link)
        if img:
            self.set('img', img)
        if self.review:
                self.review.update(review)
        else:
                option = Option.take(self.id)
                Review.add(review, option.author, option)
        self.save()
        return Option.take(self.id)

    @classmethod
    def take(cls, id):
        query = Query(cls)
        query.include('question')
        return query.get(id)

    @property
    def reviews(self):
        query = Query(Review)
        reviews = query.equal_to('option', self)
        query.ascending('updateAt')
        return query.find()

    @property
    def review(self):
        return self.reviews and self.reviews[0] or []

    @property 
    def new_review(self):
        return self.reviews and self.reviews[0] or None

    @property
    def question(self):
        return self.get('question')

    @property
    def link(self):
        return self.get('link')

    def up(self, user):
        vote_users = self.get('vote_users') or []
        if user.id in vote_users:
            vote_users.remove(user.id)
        else:
            vote_users.append(user.id)
        self.set('vote_users', vote_users)
        self.save()
        return 
         
        

class Review(Data):
    #title; author; kind; option
    @classmethod
    def add(cls, title, author, option):
        review = Review(title=title, author=author, option=option)
        review.save()
        return review

    def update(self, title):
        self.set('title', title)
        self.save()
        return Review.take(self.id)

    @property
    def option(self):
        return self.get('option')

class People(Data):
    def sign_up(self):
        username = self.get('username')
        password = self.get('password')
        people = People(username=username, password=password)
        people.save()
        return self.login(username, password)

    def login(self, username, password):
        assert username
        assert password

        query = Query(People)
        query.equal_to('username', username).equal_to('password', password)
        people = query.find()
        people = people and people[0] or None
        return people

if __name__ == '__main__':
    #Question.add('haha', 'hehe')
    pass

