from operator import attrgetter
import unittest2
from couchdbkit import Server
import couchdbkit
import couchjock


class CouchjockTestCase(unittest2.TestCase):
    server_url = 'http://localhost:5984/'
    db_name = 'couchjock__test'

    schema = couchjock

    def setUp(self):
        self.server = Server(uri=self.server_url)
        self.db = self.server.create_db(self.db_name)

    def tearDown(self):
        self.server.delete_db(self.db_name)

    def test_save(self):
        class Foo(self.schema.Document):
            _db = self.db
            pass
        foo = Foo()
        foo.save()
        foo_id = foo._id
        self.assertIsNotNone(foo_id)
        foo2 = Foo.get(foo_id)
        self.assertEqual(foo2._id, foo_id)

    def test_simple_schema(self):
        class Foo(self.schema.Document):
            _db = self.db
            string = self.schema.StringProperty()
            boolean = self.schema.BooleanProperty(default=True)

        foo1 = Foo()
        foo1.save()
        foo1_id = foo1._id
        foo1_rev = foo1._rev
        self.assertIsNotNone(foo1_id)
        self.assertIsNotNone(foo1_rev)
        foo1 = Foo.get(foo1_id)
        self.assertEqual(foo1.to_json(), {
            'doc_type': 'Foo',
            '_id': foo1_id,
            '_rev': foo1_rev,
            'string': None,
            'boolean': True,
        })

        foo1._doc.update({'boolean': False})
        self.assertEqual(foo1.boolean, False)

    def _individual_save(self, docs):
        for doc in docs:
            doc.save()

    def _bulk_save(self, docs):
        self.db.bulk_save(docs)

    def _test_simple_view(self, save_fn):
        class Foo(self.schema.Document):
            _db = self.db
            string = self.schema.StringProperty()
        foo1 = Foo(string='fun one')
        foo2 = Foo(string='poop')
        save_fn([foo1, foo2])

        self.assertEqual(
            map(lambda x: x.to_json(), Foo.view('_all_docs', include_docs=True).all()),
            map(lambda x: x.to_json(), sorted([foo1, foo2], key=attrgetter('_id')))
        )

    def test_simple_view(self):
        self._test_simple_view(self._individual_save)

    def test_bulk_save(self):
        self._test_simple_view(self._bulk_save)


class CouchdbkitTestCase(CouchjockTestCase):
    schema = couchdbkit
