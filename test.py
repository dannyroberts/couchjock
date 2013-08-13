import unittest
from couchdbkit import Server
import couchjock


class BasicTestCase(unittest.TestCase):
    server_url = 'http://localhost:5984/'
    db_name = 'couchjock__test'

    def setUp(self):
        self.server = Server(uri=self.server_url)
        self.db = self.server.create_db(self.db_name)

    def tearDown(self):
        self.server.delete_db(self.db_name)

    def test_save(self):
        class Foo(couchjock.Document):
            _db = self.db
            pass
        foo = Foo()
        foo.save()
        foo_id = foo._id
        self.assertIsNotNone(foo_id)
        foo2 = Foo.get(foo_id)
        self.assertEqual(foo2._id, foo_id)
