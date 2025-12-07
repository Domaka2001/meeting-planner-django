import uuid
from django.db import models

class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True) # Nowe pole z mockupu
    created_at = models.DateTimeField(auto_now_add=True)

class Option(models.Model):
    OPTION_TYPES = [('date', 'Termin'), ('location', 'Lokalizacja')]
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=OPTION_TYPES, default='date') # Rozróżnienie

class Participant(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=100)

class Vote(models.Model):
    CHOICES = [('yes', 'Tak'), ('maybe', 'Może'), ('no', 'Nie')]
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    choice = models.CharField(max_length=10, choices=CHOICES, default='maybe')