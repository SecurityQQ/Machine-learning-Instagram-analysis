import unittest
from scrabber import InstagramScrabber

class TestScrabber(unittest.TestCase):

    @staticmethod
    def username():
        return 'ohrana228'

    @staticmethod
    def password():
        return 'GoStartUp1337'

    @staticmethod
    def test_base_function():
        try:
            my_inst_username = 'alexm.shots'
            scrabber = InstagramScrabber(TestScrabber.username(), TestScrabber.password())
            scrabber.scrab_full_info(my_inst_username)
        except:
            assert False

if __name__ == '__main__':
    unittest.main()
