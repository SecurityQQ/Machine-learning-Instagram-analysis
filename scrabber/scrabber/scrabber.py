import instabot as inst
from .utils import download_image, compress_image
from time import sleep


class InstagramScrabber():

    def __init__(self, username='ohrana228', password='GoStartUp1337'):
        self.bot = inst.Bot(
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

    def get_media_url(self, media_id):
        try:
            return self.bot.get_media_info(media_id)[0]['image_versions2']['candidates'][0]['url']
        except IndexError:
            return None

    def collect_images(self, username, dir_to_save="./images/"):
        media = self.bot.get_user_medias(username, filtration=False)
        media_urls = [self.get_media_url(media_id) for media_id in media]
        dir_to_save += username
        for url in media_urls:
            print("Downloading image: {}, saving to: {}".format(url, dir_to_save))
            result_url = download_image(url, dir_to_save)
            compress_image(result_url)

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