import os
import re
import unittest

import webtest
from webtest import TestApp, AppError

import app

class TestWebApp(unittest.TestCase):
    def setUp(self):
        app.credentials['username'] = 'user'
        app.credentials['password'] = 'pass'
        self.app = TestApp(app.app)
        self.app.authorization = ('Basic', ('user', 'pass'))

    def test_unauthorized(self):
        self.app.authorization = ('Basic', ('user', 'wrong pass'))
        with self.assertRaises(AppError):
            self.app.get('/')

    def test_index(self):
        res = self.app.get('/')
        self.assertEqual('200 OK', res.status)
        self.assertEqual('private short-term memory', res.html.find('h1').text)

    def test_restore_text(self):
        res = self.app.get('/text')
        self.assertEqual('200 OK', res.status)
        self.assertTrue(res.html.find('textarea'))

    def test_store_text(self):
        res = self.app.post('/text', {
            't': 'テキスト'
        }, content_type='multipart/form-data')
        self.assertEqual('302 Found', res.status)
        res = res.follow()
        self.assertEqual('テキスト', res.html.find('textarea').text)

    def test_restore_file(self):
        res = self.app.get('/file')
        self.assertEqual('200 OK', res.status)
        self.assertTrue(res.html.find('input', {'type': 'file'}))

    def test_store_file(self):
        res = self.app.post('/file', {
            'f': webtest.Upload('あいうえお.txt', 'かきくけこ'.encode('utf-8'))
        }, content_type='multipart/form-data')
        self.assertEqual('302 Found', res.status)
        res = res.follow()
        self.assertTrue(res.html.find(text=re.compile('あいうえお.txt')))

    def test_download_file(self):
        _ = self.app.post('/file', {
            'f': webtest.Upload('あいうえお.txt', 'かきくけこ'.encode('utf-8'))
        }, content_type='multipart/form-data')
        res = self.app.get('/download')
        self.assertEqual('200 OK', res.status)
        self.assertTrue('かきくけこ', res.body.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
