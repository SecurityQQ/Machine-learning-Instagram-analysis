#!/usr/local/bin/python
# -*- coding: utf-8 -*-
try:
    from instabot import *
    from utils import download_image, download_image_multi_wrapped, compress_image, dump_data
except ModuleNotFoundError:  # pycharm magic
    from .instabot import *
    from .utils import download_image, download_image_multi_wrapped, compress_image, dump_data

from collections import Counter
from itertools import izip, repeat
import os
from multiprocessing import Pool
IMAGE = 1
VIDEO = 2


class InstagramScrabber():

    def __init__(self, username='ohrana228', password='GoStartUp1337'):
        self.bot = Bot(
                                whitelist=False,
                                blacklist=False,
                                comments_file=False,
                                max_likes_per_day=1000,
                                max_unlikes_per_day=1000,
                                max_follows_per_day=350,
                                max_unfollows_per_day=350,
                                max_comments_per_day=100,
                                max_blocks_per_day=100,
                                max_unblocks_per_day=100,
                                max_likes_to_like=100,
                                filter_users=True,
                                max_followers_to_follow=2000,
                                min_followers_to_follow=10,
                                max_following_to_follow=2000,
                                min_following_to_follow=10,
                                max_followers_to_following_ratio=10,
                                max_following_to_followers_ratio=2,
                                min_media_count_to_follow=3,
                                max_following_to_block=2000,
                                like_delay=10,
                                unlike_delay=10,
                                follow_delay=30,
                                unfollow_delay=30,
                                comment_delay=60,
                                block_delay=30,
                                unblock_delay=30,
                                stop_words=['shop', 'store', 'free']
                            )
        self.usernames_to_collect = []
        self.bot.login(username=username, password=password)

    def get_media_info(self, media_id):
        try:
            return self.bot.get_media_info(media_id)[0]
        except Exception as e:
            print("Warning: get_media_info exception: {}".format(e))

    def get_media_url(self, media_info):
        try:
            if media_info['media_type'] == IMAGE:
                return media_info['image_versions2']['candidates'][0]['url']
        except IndexError:
            return None
        except Exception as e:
            print("Warning: get_media_url exception: {}".format(e))

    def get_parsed_info(self, media_info):
        try:
            return {
                'text': media_info['caption']['text'],
                'taken_at': media_info['taken_at'],
                'comments_count': media_info['comment_count'],
                'comments': media_info['comments']
             }
        except Exception as e:
            return None

    def get_comments(self, media_info):
        return [item for item in media_info['comments'] if item['content_type'] == 'comment']

    def get_active_users_by_media_id(self, media_id):
        likers = self.bot.get_media_likers(media_id)
        commenters = self.bot.get_media_commenters(media_id)
        return Counter(likers + commenters).most_common(20)

    def get_active_users(self, username):
        # TODO: make w/o get_user_medias UPD: probably, unimplementable
        media = self.bot.get_user_medias(username, filtration=False)
        cache_path = os.path.join("./images/", username, 'cache_active_users.tsv')
        set_counter = {}
        if os.path.exists(cache_path):
            with open(cache_path) as cache:
                keys = cache.readline().split()
                values = cache.readline().split()
                set_counter = {int(k): int(v) for (k, v) in zip(keys, values)}
        else:
            counter = Counter()
            for media_id in media:
                counter.update(self.get_active_users_by_media_id(media_id))
            set_counter = {a[0]: a[1] for a in sorted(list(counter), key=lambda x: -x[1])}
            dump_data(set_counter, path=cache_path)
        return set_counter

    def collect_infos(self, username):
        # media = self.bot.get_user_medias(username, filtration=False)
        # media_infos = [self.get_media_info(media_id) for media_id in media]
        # parsed_info = [self.get_parsed_info(info) for info in media_infos]
        # pprint(media_infos[1])
        # print(self.get_comments(media_infos[1]))
        # TODO:
        pass


    def collect_images_with_followers(self, username, dir_to_save="./images/", depth=20):
        print("-- Running collect images with followers".format())
        if depth == -1:  # no limit
            depth = 100000
        username = self.bot.convert_to_user_id(username)
        active_users = self.get_active_users(username)
        i = 0
        total_num_of_users = min(depth, len(active_users))
        saved_users = {}
        for user_id, count in active_users.items():
            print("Collecting user {}/{}".format(i, total_num_of_users))
            try:
                self.collect_images(user_id, dir_to_save=dir_to_save)
                saved_users[user_id] = count
            except Exception as e:
                print("Exception at collect_images_with_followers: {}".format(e))
            i += 1
            if i >= depth:
                break
        print('Finished collecting images')
        return saved_users


    def small_pic_url(self, json_item):
        pics = json_item['image_versions2']['candidates']
        return (x for x in pics if x['height'] < 350 and x['width'] < 350).next()['url']

    def get_media_urls(self, user_id):
        media_json = self.bot.get_media_json(user_id)
        return [self.small_pic_url(json_item) for json_item in media_json['items']]

    def convert_to_user_id(self, username):
        username = self.bot.convert_to_user_id(username)
        return username

    def collect_images(self, username, dir_to_save="./images/"):
        username = self.bot.convert_to_user_id(username)
        media_urls = self.get_media_urls(username)
        dir_to_save = os.path.join(dir_to_save, username)
        media_urls = [url for url in media_urls if url is not None]
        if not os.path.exists(dir_to_save):
            os.makedirs(dir_to_save)
        pool = Pool(4)
        pool.map(download_image_multi_wrapped, izip(media_urls, repeat(dir_to_save)))


    def __update_statistics(self, delay=60 * 60):
        # TODO:
        pass


    def gather_statistics_async(self):
        # TODO:
        self.__update_statistics()


def get_data(username, password):
    scr = InstagramScrabber(username=username, password=password)
    return scr.collect_images_with_followers(username)