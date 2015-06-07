from leancloud import File
from StringIO import StringIO

def save_file(f):
    img = None
    if f != {} and 'img' in f: 
         image_type_list = ['image/gif', 'image/jpeg', 
          'image/pjpeg', 'image/bmp', 'image/png', 'image/x-png'] 
         f =f['img'][0]
         content_type = f['content_type']
         if content_type in image_type_list:
            if len(f['body']) < 4 * 1024 * 1024:
                suffix = content_type.split('/')[-1]
                img = File(suffix, StringIO(f['body']), content_type)
                img.save()
    return img
