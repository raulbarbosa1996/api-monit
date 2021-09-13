from couchdb.mapping import DictField, Mapping, BooleanField, ListField
from flaskext_.couchdb import (CouchDBManager, Document, TextField,
                               DateTimeField, ViewField, paginate, IntegerField, ViewDefinition)

class Intents(Document):
    doc_type = 'intents'
    IntentType = TextField()
    Intent_Target = TextField()
    Intent_State=TextField()
    Conditions = ListField(DictField(Mapping.build(
        Policy=TextField(),
        Constraints=ListField(DictField(Mapping.build(
            Domains=ListField(DictField(Mapping.build(
                Name=TextField(),
                Domain=TextField(),
                Action=TextField(),
                Traffic_Type=TextField(),
                Period=TextField(),
                Limit=TextField(),
                Source=TextField(),
                Acess=ListField(TextField()),
                Destination=TextField(),
                Performance=IntegerField(),
                Level=TextField(),
                Bool=BooleanField()

            ))),
            Level=TextField(),
            Bool=BooleanField()
        )))

    )))


    all = ViewField('intents', '''
        function (doc) {
                emit(doc.Intent, doc);
        }''', descending=True)

    intents_by_type = ViewField('intents', '''
        function(doc, meta) {
          if (doc.IntentType) {
             emit(doc.IntentType.toLowerCase(),doc);
          }
}''', descending=True)


    intents_by_Intent_Target = ViewField('intents', '''
        function(doc) {
          if (doc.Intent_Target) {
             emit(doc.Intent_Target.toLowerCase(),doc);
          }
}''', descending=True)

    intents_by_Id = ViewField('intents', '''
        function(doc) {
          if (doc.id) {
             emit(doc.id,doc);
          }
}''', descending=True)


manager = CouchDBManager()
manager.add_document(Intents)

