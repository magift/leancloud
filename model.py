from datetime import datetime, timedelta
import leancloud
from leancloud import Object
from leancloud import LeanCloudError
from leancloud import Query



class Data(Object):
    @property
    def title(self):
        return self.get('title')

    @classmethod
    def take(cls, id):
        query = Query(cls)
        return query.get(id)

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
        options = query.equal_to('question', self)
        query.descending('updatedAt')
        return query.find()

    @classmethod
    def hotest(self):
        query = Query(Question)
        query.descending('updatedAt')
        questions = query.limit(50).find()

        #TODO sql inject
        result = Query.do_cloud_query('select * from Option where question in (%s) order by updatedAt desc' % ','.join(["pointer('Question', '%s')" % i.id for i in questions]))
        result = result.results
        options = {}
        for r in result:
            if r.question.id not in [i for i in options.keys()]:
                options[r.question.id] = r

        result = Query.do_cloud_query('select * from Review where option in (%s) order by updatedAt desc' % ','.join(["pointer('Option', '%s')" % i.id for i in options.values()]))
        result = result.results
        reviews = {}
        for r in  result:
            if r.option.id not in [i for i in reviews.keys()]:
                reviews[r.option.id] = r

        return questions, options, reviews

    @property
    def new_option(self):
        return self.options and self.options[0] or None

    @classmethod
    def get_date_news(self):
        query = Query(Question)
        query.greater_than("createdAt", datetime.now() - timedelta(days=1))
        r = query.find()

        return [i for i in r if i not in [j.question for j in Option.get_date_news()]]
    
class Option(Data):
    #title;author;link;question;
    @classmethod
    def add(cls, title, author, question, link=''):
        option = Option(title=title, author=author, question=question, link=link)
        option.save()
        question.set('updatedAt', datetime.now())
        question.save()
        return option

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

    @classmethod
    def get_date_news(self):
        query = Query(Option)
        query.include("question").greater_than('createdAt', datetime.now() - timedelta(days=1)).descending('createdAt')
        r = query.find()
        d = dict()
        for i in r:
            if i.question in d:
                continue
            else:
                d.update({i.question:i})
        return d.values()
        

class Review(Data):
    #title; author; kind; option
    @classmethod
    def add(cls, title, author, option):
        review = Review(title=title, author=author, option=option)
        review.save()
        return review

    @property
    def option(self):
        return self.get('option')





if __name__ == '__main__':
    #Question.add('haha', 'hehe')
    pass

