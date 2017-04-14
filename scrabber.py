import requests
import instabot as inst
from utils import download_image, compress_image
from urllib.parse import urlparse

# bot = inst.Bot()
# bot.login(username=username, password=pwd)


class InstagramScrabber():

    def __init__(self, username, password):
        self.bot = inst.Bot()
        self.bot.login(username=username, password=password)

    def get_media_url(self, media_id):
        try:
            return self.bot.get_media_info(media_id)[0]['image_versions2']['candidates'][0]['url']
        except IndexError:
            return None

    def scrab_full_info(self, username, dir_to_save="./"):
        # self.save_user_stats(username)
        media = self.bot.get_user_medias(username, filtration=False)
        media_urls = [self.get_media_url(media_id) for media_id in media]
        dir_to_save += username
        for url in media_urls:
            print("Downloading image: {}, saving to: {}".format(url, dir_to_save))
            result_url = download_image(url, dir_to_save)
            compress_image(result_url)