#!/usr/local/bin/python
# -*- coding: utf-8 -*-
try:
    from instabot import *
    from utils import download_image, download_image_multi_wrapped, compress_image, dump_data
except ModuleNotFoundError:  # pycharm magic
    from .instabot import *
    from .utils import download_image, download_image_multi_wrapped, compress_image, dump_data

from time import sleep
from collections import Counter
from itertools import izip, repeat
import os
from multiprocessing import Pool
from pprint import pprint
IMAGE = 1
VIDEO = 2

from datetime import datetime

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
        if depth == -1:  # no limit
            depth = 100000
        username = self.bot.convert_to_user_id(username)
        active_users = self.get_active_users(username)
        # print(active_users)
        # sleep(3)
        i = 0
        for user_id, count in active_users.items():
            self.collect_images(user_id, dir_to_save=dir_to_save)
            i += 1
            if i >= depth:
                break
            # sleep(1)
        return active_users


    def small_pic_url(self, json_item):
        pics = json_item['image_versions2']['candidates']
        return (x for x in pics if x['height'] < 350 and x['width'] < 350).next()['url']

    def get_media_urls(self, user_id):
        media_json = self.bot.get_media_json(user_id)
        return [self.small_pic_url(json_item) for json_item in media_json['items']]


    def collect_images(self, username, dir_to_save="./images/"):
        now_ci = datetime.now()
        now = datetime.now()
        username = self.bot.convert_to_user_id(username)
        end = datetime.now()
        print('convert_to_user_id: ', (end - now).total_seconds())
        now = datetime.now()
        media_urls = self.get_media_urls(username)
        end = datetime.now()
        print('get_media_urls: ', (end - now).total_seconds())

        dir_to_save = os.path.join(dir_to_save, username)
        media_urls = [url for url in media_urls if url is not None]
        if not os.path.exists(dir_to_save):
            os.makedirs(dir_to_save)
        pool = Pool(4)
        res = pool.map(download_image_multi_wrapped, izip(media_urls, repeat(dir_to_save)))
        print('total_time:', (end - now_ci).total_seconds())


    def __update_statistics(self, delay=60 * 60):
        usernames = self.usernames_to_collect
        print("Updating statistics: {}".format(usernames))
        for username in usernames:
            self.bot.save_user_stats(username)
        sleep(delay)


    def gather_statistics_async(self):
        # while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        #     username = sys.stdin.readline()
        #     if username:
        #         usernames = self.usernames_to_collect
        #         print("Adding username: {} to updating list".format(username))
        #         usernames.append(username)
        #         if username in usernames:
        #             print("Success")
        #         else:
        #             print("Failed")
        #     else:
        #         print('Terminating...')
        #         exit(0)
        # else:
        #     self.__update_statistics()
        # TODO:
        self.usernames_to_collect = ['alexm.shots',
                                     'alexm.daily',
                                     'varlamov',
                                     'wylsacom',
                                     'muakate',
                                     'ogdencitizensclub',
                                     'davidwallaceshoots']
        self.__update_statistics()


# scr = InstagramScrabber()
# scr.collect_images_with_followers('alexm.daily')


# Counter({('1445166739', 1): 9, ('4895012071', 1): 9, ('1411672190', 1): 7, ('1293971559', 1): 6, ('2318921324', 1): 6, ('1467534818', 1): 4, ('4865660047', 1): 4, ('619132351', 1): 4, ('500835755', 1): 4, ('33172702', 1): 4, ('3212039470', 1): 4, ('2978911382', 1): 3, ('574803774', 1): 3, ('2463172314', 1): 3, ('2210105502', 1): 3, ('3424910531', 1): 3, ('1557268134', 1): 3, ('3032427999', 1): 3, ('2009029052', 1): 3, ('3260098968', 1): 3, ('191841799', 1): 3, ('1924613073', 1): 3, ('822117162', 1): 3, ('3960804756', 1): 2, ('3857890553', 1): 2, ('55184', 1): 2, ('3130084907', 1): 2, ('2997688898', 1): 2, ('1505441528', 1): 2, ('302969134', 1): 2, ('2206503320', 1): 2, ('4902486793', 1): 2, ('4625182101', 1): 2, ('1595267420', 1): 2, ('403941225', 1): 2, ('1651539116', 1): 2, ('1537741987', 1): 2, ('1662967191', 1): 2, ('430106409', 1): 2, ('4828817795', 1): 2, ('4109196556', 1): 2, ('324573119', 1): 2, ('1640288715', 1): 2, ('1468645962', 1): 2, ('3119974145', 1): 2, ('3040679298', 1): 2, ('1962419534', 1): 2, ('1439638200', 1): 2, ('4778205911', 1): 2, ('2085437204', 1): 2, ('2078489546', 1): 2, ('3219285593', 1): 2, ('202804377', 1): 2, ('2415450985', 1): 2, ('587864293', 1): 2, ('1637168168', 1): 2, ('340193435', 1): 2, ('2694059289', 1): 1, ('4512049440', 1): 1, ('185089695', 1): 1, ('4119630651', 1): 1, ('357987876', 1): 1, ('807071781', 1): 1, ('3529501255', 1): 1, ('1830155413', 1): 1, ('3604096194', 1): 1, ('416587843', 1): 1, ('1810982947', 1): 1, ('1619541466', 1): 1, ('4453181288', 1): 1, ('2000223297', 1): 1, ('195900109', 1): 1, ('37141857', 2): 1, ('3617207626', 1): 1, ('3807129961', 1): 1, ('3084409474', 1): 1, ('3644708563', 1): 1, ('773851138', 1): 1, ('2309193798', 1): 1, ('1639851534', 1): 1, ('591523001', 1): 1, ('638431584', 1): 1, ('1517813210', 1): 1, ('1569743552', 1): 1, ('1413781970', 1): 1, ('2154493810', 1): 1, ('4536606425', 1): 1, ('317368764', 1): 1, ('1448151012', 1): 1, ('1495572309', 1): 1, ('1384006493', 1): 1, ('1487315899', 1): 1, ('3242166009', 1): 1, ('44158411', 1): 1, ('1013961199', 1): 1, ('3660235803', 1): 1, ('1317409318', 1): 1, ('1503083645', 1): 1, ('3894508503', 1): 1, ('2960409490', 1): 1, ('499649325', 1): 1, ('2251037622', 1): 1, ('49619752', 2): 1, ('2588498473', 1): 1, ('3645169405', 1): 1, ('4597581755', 1): 1, ('3488427107', 1): 1, ('763656115', 1): 1, ('2002692606', 1): 1, ('1982173033', 1): 1, ('286140718', 1): 1, ('2238265748', 1): 1, ('905874190', 1): 1, ('4470626446', 1): 1, ('4570167904', 1): 1, ('1663393723', 1): 1, ('343787831', 1): 1, ('1611741498', 1): 1, ('398370941', 1): 1, ('3679262128', 1): 1, ('4831444360', 3): 1, ('33172702', 2): 1, ('2405264349', 1): 1, ('189700383', 1): 1, ('651209559', 1): 1, ('4358534767', 1): 1, ('3207335745', 1): 1, ('521927802', 1): 1, ('4465457583', 1): 1, ('3231870292', 1): 1, ('180140691', 1): 1, ('1693316023', 1): 1, ('2056238419', 1): 1, ('4625182101', 2): 1, ('3905056881', 2): 1, ('303324622', 1): 1, ('644309518', 1): 1, ('4837449513', 1): 1, ('4921376373', 1): 1, ('1715057275', 1): 1, ('367822240', 1): 1, ('24586142', 1): 1, ('4366026575', 1): 1, ('1637078551', 1): 1, ('2044538053', 1): 1, ('4813334120', 1): 1, ('1412974993', 1): 1, ('370123863', 1): 1, ('367603948', 1): 1, ('3528591008', 1): 1, ('383941636', 1): 1, ('3247586148', 1): 1, ('4525918775', 1): 1, ('1443215294', 1): 1, ('783485447', 1): 1, ('4831018034', 1): 1, ('1451742894', 1): 1, ('1683116332', 1): 1, ('2460284415', 1): 1, ('3486070232', 1): 1, ('4526571401', 1): 1, ('4788354145', 1): 1, ('1368010459', 1): 1, ('537602478', 1): 1, ('586589905', 1): 1, ('284846477', 1): 1, ('30076797', 1): 1, ('3536318355', 1): 1, ('773980377', 1): 1, ('2274684287', 1): 1, ('193019722', 1): 1, ('2155128286', 1): 1, ('917538968', 1): 1, ('449426044', 1): 1, ('616624863', 1): 1, ('1330223781', 1): 1, ('3195285113', 2): 1, ('4194018128', 1): 1, ('28477510', 1): 1, ('2230738092', 1): 1, ('2011809874', 1): 1, ('1521915501', 1): 1, ('1314896054', 1): 1, ('516050886', 1): 1, ('1557268318', 1): 1, ('2333676137', 1): 1, ('4710472145', 1): 1, ('508277516', 1): 1, ('2245568802', 2): 1, ('3533823200', 1): 1, ('1609607467', 1): 1, ('1527867956', 1): 1, ('4358979489', 1): 1, ('1549226415', 1): 1, ('189678739', 1): 1, ('611951048', 1): 1, ('22352329', 2): 1, ('4342463684', 1): 1, ('4114491983', 1): 1, ('4293806637', 1): 1, ('735209401', 2): 1, ('4473397197', 1): 1, ('4070049420', 1): 1, ('445990594', 1): 1, ('3023826478', 2): 1, ('1559984638', 2): 1, ('22352329', 1): 1, ('178522292', 1): 1, ('3164599924', 1): 1, ('21791461', 1): 1, ('1240460376', 1): 1, ('1489248265', 1): 1, ('1414632536', 1): 1, ('1737740362', 2): 1, ('1185212669', 1): 1, ('216085013', 1): 1, ('12093856', 1): 1, ('1452618480', 1): 1, ('3467985559', 1): 1, ('230498298', 1): 1, ('277018255', 1): 1, ('4103286590', 1): 1, ('2988955150', 1): 1, ('822117162', 2): 1, ('1556882487', 1): 1, ('2226187171', 2): 1, ('4636789413', 1): 1, ('1172537099', 1): 1, ('1096346479', 1): 1, ('3416225987', 1): 1, ('1973234353', 2): 1, ('4583497542', 1): 1, ('300024725', 1): 1, ('2002191669', 1): 1, ('3138004758', 1): 1, ('4723128537', 1): 1, ('336369655', 1): 1, ('3288684708', 1): 1, ('3985361247', 1): 1, ('1783310282', 1): 1, ('4120265207', 1): 1, ('2319205401', 1): 1, ('2205313596', 1): 1, ('30579456', 1): 1, ('2311591635', 1): 1, ('4761735098', 1): 1, ('145742400', 1): 1, ('1791061984', 1): 1, ('327702940', 1): 1, ('237689341', 1): 1, ('882053836', 1): 1, ('2250766139', 1): 1})




# info = media_info=scr.get_media_info(media_id=1464703964850245099)
# pprint(info)
# scr.get_active_users(media_info=info)
# pprint(scr.get_active_users(media_id=1465616589683585466))