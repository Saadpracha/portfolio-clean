from mongoengine import Document, StringField, DateTimeField
from django.utils import timezone

# Create your models here.

class Contact(Document):
    name = StringField(required=True, max_length=100)
    email = StringField(required=True, max_length=100)
    subject = StringField(required=True, max_length=200)
    message = StringField(required=True)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'contacts',
        'ordering': ['-created_at']
    }

    def __str__(self):
        return f"{self.name} - {self.subject}"
