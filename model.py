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
        options = options.find()
        options.sort(key=lambda x:len(x.get('vote_users') or []), reverse=True)
        return options

    @classmethod
    def get_other_by_questions(cls, questions):
        #TODO sql inject
        questions = [i for i in questions if i]
        result = Query.do_cloud_query('select include img, * from Option where question in (%s) order by updatedAt desc limit 1000' % ','.join(["pointer('Question', '%s')" % i.id for i in questions]))
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
        return options, reviews

    @classmethod
    def hotest(cls, page=0):
        query = Query(Question)
        query.descending('updatedAt')
        questions = query.skip(page*PAGE_SIZE).limit(PAGE_SIZE).find()

        options, reviews =  cls.get_other_by_questions(questions)

        return questions, options, reviews

    @property
    def new_option(self):
        return self.options and self.options[0] or None

    @property
    def tags(self):
        tags = Tag2Question.gets_by_question(self)
        return ' '.join([t.get('tag').get('title') for t in tags])

    
class Option(Data):
    #title;author;link;question;
    @classmethod
    def add(cls, title, author, question, link='', nickname='', img=None):
        option = Option(title=title, author=author, question=question, link=link, nickname=nickname, img=img)
        option.save()
        question.set('updatedAt', datetime.now())
        question.save()
        return option

    def update(self, title, link, img):
        self.set('title', title)
        self.set('link', link)
        if img:
            self.set('img', img)
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
        reviews = query.equal_to('option', self).include('author')
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
            self.question.set('updatedAt', datetime.now())
            self.question.save()
        self.set('vote_users', vote_users)
        self.save()
        return 
         
        

class Review(Data):
    #title; author; kind; option
    @classmethod
    def add(cls, title, author, option, nickname=''):
        review = Review(title=title, author=author, option=option, nickname=nickname)
        review.save()
        option.question.set('updatedAt', datetime.now())
        option.question.save()
        return review

    def update(self, title):
        self.set('title', title)
        self.save()
        return Review.take(self.id)

    @property
    def option(self):
        return self.get('option')

    def get_name(self):
        name = self.get('nickname') or ''
        if not name:
            author = self.get('author')
            if author and author.get('nickname'):
                name = author.get('nickname')
        return name
            

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

    def update_nickname(self, name):
        self.set('nickname', name)
        self.save()

    def is_admin(self):
        if self.get('username') == 'admin' and self.get('password') == 'lifeisgood':
            return True
        return False

class Tag2Question(Data):
    #question, tag
    @classmethod
    def update(cls, question, tags):
        tags = list(set([t for t in tags.split() if t]))
        query = Query(Tag2Question)
        for tq in query.equal_to('question', question).find():
			tq.destroy()
        for tag_name in tags:
            tag = Tag.get_by_title(tag_name)
            if not tag:
                tag = Tag.add(tag_name)
            t = Tag2Question(tag=tag, question=question) 
            t.save()

    @classmethod
    def gets_by_tag(cls, tag_name, page=0):
        tag = Tag.get_by_title(tag_name.strip())
        if not tag:
            return []

        query = Query(cls)
        #r = query.equal_to('tag', tag).include('question').descending('question.createdAt').skip(page*PAGE_SIZE).limit(PAGE_SIZE).find()
        #r = Query.do_cloud_query('select include question, * from Tag2Question where tag = pointer("Tag", "%s") order by question.updatedAt desc limit %s, %s' % (tag.id, page*PAGE_SIZE, PAGE_SIZE))
        #r = r.results
        r = query.equal_to('tag', tag).include('question').descending('createdAt').skip(page*PAGE_SIZE).limit(PAGE_SIZE).find()
        return [i for i in r if i]

    @classmethod
    def gets_by_question(cls, question):
        query = Query(cls)
        r = query.equal_to('question', question).include('tag').find()
        return r

class Tag(Data):
    @classmethod
    def add(cls, title):
        title = title.strip()
        query = Query(cls)
        tag = query.equal_to('title', title).find()
        if not tag:
            tag = Tag(title=title)
            tag.save()
        tag = query.equal_to('title', title).find()
        return tag and tag[0] or None

    @classmethod
    def takes(cls, limit=20):
        query = Query(cls)
        tags = query.limit(limit).ascending('sort').find()
        return tags

    @classmethod
    def get_by_title(cls, title):
        title = title.strip()
        query = Query(cls)
        tag = query.equal_to('title', title).find()
        return tag and tag[0] or None
        


if __name__ == '__main__':
    #Question.add('haha', 'hehe')
    pass
