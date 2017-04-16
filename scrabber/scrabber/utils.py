import os
import requests
from PIL import Image
import re

#
# image utils
#

# image download


def get_image_name(url):
    try:
        is_image_regex = re.compile(r'.*/(.*.je?pg|png|tiff).*')
        return re.findall(is_image_regex, url)[0]
    except IndexError:
        return None


def download_image(url, dir_to_save):
    img_data = requests.get(url).content
    image_name = get_image_name(url)
    if not os.path.exists(dir_to_save):
        os.makedirs(dir_to_save)
    file_dir = os.path.join(dir_to_save, image_name)
    try:
        handler = open(file_dir, 'wb')
        handler.write(img_data)
    except:
        return None
    return file_dir


#
# image compression
#


def compress_image(path, min_size=300):
    try:
        image = Image.open(path)
        ratio = image.width / image.height
        if image.width > image.height:
            image.save(path, dpi=[min_size * ratio, min_size])
        else:
            image.save(path, dpi=[min_size, min_size / float(ratio)])
    except IOError:
        print("Warning: file at {} is not image. Removing...".format(path))
        os.remove(path)
    except ZeroDivisionError:
        print("Warning: file at {} has corrupted size. Removing...".format(path))
        os.remove(path)


def compress_images_at_dir(path):
    with os.scandir(path) as d:
        for entry in d:
            if not entry.name.startswith('.') and entry.is_file():
                image_path = entry.path
                compress_image(image_path)