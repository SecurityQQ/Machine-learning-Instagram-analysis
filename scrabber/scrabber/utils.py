import os
import requests
from PIL import Image
import re

#
# image utils
#

# image download

def get_tsv_line(dictionary):
    line = ""
    for key in sorted(dictionary):
        line += str(dictionary[key]) + "\t"
    return line[:-2] + "\n"


def get_header_line(dictionary):
    line = "\t".join(dictionary)
    return line + "\n"


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory) and len(directory) > 0:
        os.makedirs(directory)


def dump_data(data, path):
    ensure_dir(path)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(get_header_line(data))
            f.write(get_tsv_line(data))
    else:
        with open(path, "a") as f:
            f.write(get_tsv_line(data))


def get_image_name(url):
    try:
        is_image_regex = re.compile(r'.*/(.*.je?pg|png|tiff).*')
        return re.findall(is_image_regex, url)[0]
    except IndexError:
        return None


def download_image(url, dir_to_save, file_prefix=''):
    try:
        img_data = requests.get(url).content
        image_name = get_image_name(url)
        if not os.path.exists(dir_to_save):
            os.makedirs(dir_to_save)
        image_name = file_prefix + image_name
        file_dir = os.path.join(dir_to_save, image_name)
        handler = open(file_dir, 'wb')
        handler.write(img_data)
    except Exception as e:
        print("Warning: Exception at download_image {}".format(e))
        return None
    return file_dir

def download_image_multi_wrapped(args):
    return download_image(*args)


#
# image compression
#


def compress_image(path, min_size=220):
    try:
        image = Image.open(path)
        ratio = image.width / float(image.height)
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
    except Exception as e:
        print("Warning: unknown exception at {}".format(path))


def compress_images_at_dir(path):
    with os.scandir(path) as d:
        for entry in d:
            if not entry.name.startswith('.') and entry.is_file():
                image_path = entry.path
                compress_image(image_path)