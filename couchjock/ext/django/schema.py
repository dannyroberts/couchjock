import couchdbkit.ext.django.schema
import jsonobject
import inspect

DocumentMeta = type(
    'DocumentMeta',
    (jsonobject.base.JsonObjectMeta,),
    dict(inspect.getmembers(
        couchdbkit.ext.django.schema.DocumentMeta,
        lambda key, value: not key.startswith('__')
    ))
)
