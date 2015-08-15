import leancloud
from leancloud import Object
from leancloud import LeanCloudError
from leancloud import Query
from model import *

def update_tag_count():
    query = Query(Tag)
    tags = query.limit(1000).find()
    for tag in tags:
        count = len(Tag2Question.gets_by_tag(tag.get('title')))
        tag.set('count', count)
        tag.save()

if __name__ == "__main__":
    import config
    leancloud.init(config.leancloud_id, master_key=config.leancloud_key)
    update_tag_count()
