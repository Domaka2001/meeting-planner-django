from django import template
from planner.models import Vote

register = template.Library()

@register.filter
def get_vote(option, participant):
    if not participant:
        return None
    try:
        return Vote.objects.get(option=option, participant=participant)
    except Vote.DoesNotExist:
        # Zwracamy "pusty" obiekt głosu z domyślnym wyborem 'maybe' lub None
        return {'choice': 'none'}