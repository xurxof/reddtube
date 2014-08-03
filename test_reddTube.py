import unittest
import urllib2

import mock

from utils import attempts

'''
class ReddTubeTest(unittest.TestCase):
    @mock.patch('urllib2.urlopen')
    def test_get_all_youtube_url_returnsEmpty_When429ContiuousErrorHTTP(self, mock_urlopen):
        mock_urlopen.side_effect = urllib2.HTTPError("url", 429, "msg", None, None)
        result = reddTube.get_all_youtube_url("url")
        self.assertSequenceEqual(result, [])

    @mock.patch('urllib2.urlopen')
    def test_get_all_youtube_url_(self, mock_urlopen):
        mock_urlopen.return_value = "<a link='https://www.youtube.com/watch?v=gVVHSfvrBmg>.</a>"
        result = reddTube.get_all_youtube_url("url")
        self.assertSequenceEqual(result, ['gVVHSfvrBmg'])
'''


@attempts(5, [], 0)
def function(arg):
    if function.iterations_before_not_fail > 0:
        function.iterations_before_not_fail -= 1
        raise urllib2.HTTPError(None, None, None, None, None)
    return arg


class AttemptsDecoratorTest(unittest.TestCase):
    def test_attempts_nofail(self):
        function.iterations_before_not_fail = 0
        result = function(4)
        self.assertEqual(4, result)

    def test_attempts_partialfail(self):
        function.iterations_before_not_fail = 2
        result = function(4)
        self.assertEqual(4, result)

    def test_attempts_continuousfail(self):
        function.iterations_before_not_fail = 20
        result = function(4)
        self.assertSequenceEqual([], result)

    def test_attempts_admitsnamedargs(self):
        function.iterations_before_not_fail = 0
        result = function(arg=4)
        self.assertEqual(4, result)

if __name__ == "__main__":
    unittest.main()