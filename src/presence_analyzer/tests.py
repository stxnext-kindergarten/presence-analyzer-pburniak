# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils  # pylint: disable=unused-import


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers['Location'].endswith('/presence_weekday'))

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_mean_weekday_view(self):
        """
        Test mean presence time grouped by weekday
        """
        response = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data)
        self.assertEqual(len(data), 7)
        self.assertEqual(data[0], [u'Mon', 0])
        self.assertEqual(data[1], [u'Tue', 30047.0])
        self.assertEqual(data[6], [u'Sun', 0])

    def test_fail_mean_weekday_view(self):
        """
        Test fail scenario mean time presence time for unknown user
        """
        response = self.client.get('/api/v1/mean_time_weekday/999999')
        self.assertEqual(response.status_code, 404)

    def test_total_weekday_view(self):
        """
        Test total presence time grouped by weekday
        """
        response = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data)
        self.assertEqual(len(data), 8)
        self.assertEqual(data[0], [u'Weekday', u'Presence (s)'])
        self.assertEqual(data[1], [u'Mon', 0])
        self.assertEqual(data[2], [u'Tue', 30047])
        self.assertEqual(data[7], [u'Sun', 0])

    def test_fail_total_weekday_view(self):
        """
        Test fail scenario total presence time for unknown user
        """
        response = self.client.get('/api/v1/presence_weekday/999999')
        self.assertEqual(response.status_code, 404)

    def test_start_end(self):
        """
        Test mean start and end time by weekdays.
        """
        response = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0], [u'Mon', 34745, 64792])
        self.assertEqual(data[2], [u'Wed', 38926, 62631])

    def test_fail_start_end(self):
        """
        Test fail scenario mean start and end time for unknown user.
        """
        response = self.client.get('/api/v1/presence_start_end/999999')
        self.assertEqual(response.status_code, 404)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_get_mean_start_end_times(self):
        """
        Test helper fuction for calculating mean start and end time by weekdays.
        """
        user_data = {
            datetime.date(2013, 9, 10): {
                'start': datetime.time(9, 39, 5),
                'end': datetime.time(17, 59, 52)},
            datetime.date(2013, 9, 12): {
                'start': datetime.time(10, 48, 46),
                'end': datetime.time(17, 23, 51)},
            datetime.date(2013, 9, 17): {
                'start': datetime.time(9, 19, 52),
                'end': datetime.time(16, 7, 37)}}

        counted_means = utils.mean_start_end(user_data)
        self.assertEqual(len(counted_means), 2)
        expected_means = [(34168, 61424), (38926, 62631)]
        self.assertEqual(counted_means, expected_means)


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
