import copy
import functools
from jsonobject import *
from couchdbkit import schema
from restkit import ResourceNotFound
from couchjock.proxy_dict import ProxyDict

SchemaProperty = ObjectProperty
SchemaListProperty = ListProperty
StringListProperty = functools.partial(ListProperty, unicode)
SchemaDictProperty = DictProperty


class DocumentSchema(JsonObject):

    @StringProperty
    def doc_type(self):
        return self.__class__.__name__

    @property
    def _doc(self):
        return ProxyDict(self, self._obj)


class DocumentBase(DocumentSchema):

    _id = StringProperty()
    _rev = StringProperty()
    _attachments = DictProperty()

    _db = None

    def to_json(self):
        doc = copy.copy(super(DocumentBase, self).to_json())
        for special in ('_id', '_rev', '_attachments'):
            if not doc[special]:
                del doc[special]
        return doc

    # The rest of this class is mostly copied from couchdbkit 0.5.7

    @classmethod
    def set_db(cls, db):
        cls._db = db

    @classmethod
    def get_db(cls):
        db = cls._db
        if db is None:
            raise TypeError("doc database required to save document")
        return db

    def save(self, **params):
        """ Save document in database.

        @params db: couchdbkit.core.Database instance
        """
        # self.validate()
        db = self.get_db()

        doc = self.to_json()
        db.save_doc(doc, **params)
        if '_id' in doc and '_rev' in doc:
            self.update(doc)
        elif '_id' in doc:
            self.update({'_id': doc['_id']})

    store = save

    @classmethod
    def save_docs(cls, docs, use_uuids=True, all_or_nothing=False):
        """ Save multiple documents in database.

        @params docs: list of couchdbkit.schema.Document instance
        @param use_uuids: add _id in doc who don't have it already set.
        @param all_or_nothing: In the case of a power failure, when the database
        restarts either all the changes will have been saved or none of them.
        However, it does not do conflict checking, so the documents will
        be committed even if this creates conflicts.

        """
        db = cls.get_db()
        docs_to_save = [doc for doc in docs if doc._doc_type == cls._doc_type]
        if not len(docs_to_save) == len(docs):
            raise ValueError("one of your documents does not have the correct type")
        db.bulk_save(docs_to_save, use_uuids=use_uuids, all_or_nothing=all_or_nothing)

    bulk_save = save_docs

    @classmethod
    def get(cls, docid, rev=None, db=None, dynamic_properties=True):
        """ get document with `docid`
        """
        if not db:
            db = cls.get_db()
        cls._allow_dynamic_properties = dynamic_properties
        return db.get(docid, rev=rev, wrapper=cls.wrap)

    @classmethod
    def get_or_create(cls, docid=None, db=None, dynamic_properties=True, **params):
        """ get  or create document with `docid` """

        if db:
            cls.set_db(db)
        cls._allow_dynamic_properties = dynamic_properties
        db = cls.get_db()

        if docid is None:
            obj = cls()
            obj.save(**params)
            return obj

        rev = params.pop('rev', None)

        try:
            return db.get(docid, rev=rev, wrapper=cls.wrap, **params)
        except ResourceNotFound:
            obj = cls()
            obj._id = docid
            obj.save(**params)
            return obj

    new_document = property(lambda self: self._doc.get('_rev') is None)

    def delete(self):
        """ Delete document from the database.
        @params db: couchdbkit.core.Database instance
        """
        if self.new_document:
            raise TypeError("the document is not saved")

        db = self.get_db()

        # delete doc
        db.delete_doc(self._id)

        # reinit document
        del self._doc['_id']
        del self._doc['_rev']


class Document(DocumentBase, schema.QueryMixin, schema.AttachmentMixin):

    @property
    def get_id(self):
        return self._id

    @property
    def get_rev(self):
        return self._rev
