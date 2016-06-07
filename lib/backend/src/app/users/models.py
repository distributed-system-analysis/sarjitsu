from app import db
 
class Graph(db.EmbeddedDocument):
    x = db.StringField() #db.DecimalField()
    y = db.StringField() #db.DecimalField()
    data = db.ListField() #db.ListField(db.DictField())
    data_type = db.StringField()
    parameter_name = db.StringField()

class Plots(db.EmbeddedDocument):
    graphs = db.ListField(db.EmbeddedDocumentField(Graph))
    # images = db.ListField(db.ImageField(size=(800,600,True)))

class Report(db.EmbeddedDocument):
    goal = db.StringField(max_length=140, required=True)
    summary = db.StringField(max_length=500, required=True) 
    #db.EmbeddedDocumentField(Summary)
    results = db.StringField(max_length=500, required=True)
    #db.EmbeddedDocumentField(Results)
    datapath = db.URLField()
    analysis = db.EmbeddedDocumentField(Plots)
    created = db.DateTimeField(help_text='date it was created')
    modified = db.DateTimeField(help_text='last modified')

class User(db.Document):
    username = db.StringField(max_length=20, 
                              unique=True,
                              required=True)
    email = db.EmailField(unique=True, required=True)
    password = db.StringField(required=True)
    #reports =  db.ListField(db.EmbeddedDocumentField(Report))
    #ReferenceField(Report)
    reports =  db.DictField()
    #recents = db.ListField(db.ListField()) 
    #db.ListField(db.StringField())

class PublicLink(db.Document):
    current = db.ListField()
