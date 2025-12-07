from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Meeting, Option, Participant, Vote
from django.urls import reverse

def create_meeting(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')

        # Pobieramy listy z formularza
        dates = request.POST.getlist('dates')
        locations = request.POST.getlist('locations')

        meeting = Meeting.objects.create(title=title, description=description)

        # Zapisujemy daty
        for date in dates:
            if date.strip():
                Option.objects.create(meeting=meeting, label=date, type='date')

        # Zapisujemy lokalizacje
        for loc in locations:
            if loc.strip():
                Option.objects.create(meeting=meeting, label=loc, type='location')

        return redirect('meeting_success', meeting_id=meeting.id)

    return render(request, 'create.html')

# Widok HTMX dla przycisku "Dodaj termin/lokalizację"
def add_option_input(request):
    input_type = request.GET.get('type', 'location')
    if input_type == 'date':
        html = '''<div class="relative mt-3"><i data-lucide="calendar" class="absolute left-3 top-3 w-5 h-5 text-gray-400"></i><input type="date" name="dates" class="w-full border border-gray-300 rounded-lg p-2.5 pl-10 focus:ring-blue-500 focus:border-blue-500"></div>'''
    else:
        html = '''<div class="relative mt-3"><i data-lucide="map-pin" class="absolute left-3 top-3 w-5 h-5 text-gray-400"></i><input type="text" name="locations" placeholder="Kolejna lokalizacja..." class="w-full border border-gray-300 rounded-lg p-2.5 pl-10 focus:ring-blue-500 focus:border-blue-500"></div>'''

    # Musimy dodać skrypt inicjalizujący ikony dla nowo dodanego elementu
    html += '<script>lucide.createIcons();</script>'
    return HttpResponse(html)

def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    participant_id = request.session.get(f'participant_{meeting_id}')
    current_participant = None

    if participant_id:
        current_participant = Participant.objects.filter(id=participant_id).first()

    if request.method == "POST" and 'new_participant' in request.POST:
        name = request.POST.get('new_participant')
        if name:
            p = Participant.objects.create(meeting=meeting, name=name)
            request.session[f'participant_{meeting_id}'] = p.id
            return redirect('meeting_detail', meeting_id=meeting.id)

    # Opcja resetowania sesji (dla testów)
    if request.GET.get('reset'):
        if f'participant_{meeting_id}' in request.session:
            del request.session[f'participant_{meeting_id}']
        return redirect('meeting_detail', meeting_id=meeting.id)

    # Obliczanie wyników dla opcji
    options = meeting.options.all()
    for opt in options:
        opt.yes_count = opt.vote_set.filter(choice='yes').count()
        opt.no_count = opt.vote_set.filter(choice='no').count()

    context = {
        'meeting': meeting,
        'options': options,
        'participants': meeting.participants.all(),
        'current_participant': current_participant
    }
    return render(request, 'meeting_detail.html', context)

# Logika głosowania HTMX
def save_vote(request, option_id, choice):
    option = get_object_or_404(Option, id=option_id)
    meeting_id = option.meeting.id
    participant_id = request.session.get(f'participant_{meeting_id}')

    if not participant_id:
        return HttpResponse("Błąd: Brak uczestnika", status=403)

    participant = get_object_or_404(Participant, id=participant_id)

    # Update lub Create głosu
    vote, created = Vote.objects.update_or_create(
        participant=participant,
        option=option,
        defaults={'choice': choice}
    )

    # Zwracamy partial przycisków
    return render(request, 'partials/vote_buttons.html', {
        'option': option,
        'participant': participant
    })

def meeting_results(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Pobieramy wszystkie opcje
    options = list(meeting.options.all())

    # Dla każdej opcji ręcznie liczymy głosy i dodajemy je jako atrybuty
    for opt in options:
        opt.yes_count = opt.vote_set.filter(choice='yes').count()
        opt.maybe_count = opt.vote_set.filter(choice='maybe').count()
        opt.no_count = opt.vote_set.filter(choice='no').count()

        # Obliczamy prosty wynik (score) do sortowania: Tak=2 pkt, Może=1 pkt
        opt.score = (opt.yes_count * 2) + opt.maybe_count

    # Sortujemy opcje od najlepszej do najgorszej
    options.sort(key=lambda x: x.score, reverse=True)

    # Najlepsza opcja to ta pierwsza po posortowaniu
    best_option = options[0] if options else None

    context = {
        'meeting': meeting,
        'options': options,      # Przekazujemy listę z policzonymi głosami
        'best_option': best_option
    }
    return render(request, 'results.html', context)

# Dodaj tę funkcję na początku pliku (przed create_meeting)
def home(request):
    return render(request, 'home.html')

def meeting_success(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    # Generujemy pełny link do spotkania (z domeną)
    relative_path = reverse('meeting_detail', args=[meeting.id])
    full_link = request.build_absolute_uri(relative_path)

    return render(request, 'meeting_success.html', {
        'meeting': meeting,
        'full_link': full_link
    })

# W pliku planner/views.py

def add_option_input(request):
    input_type = request.GET.get('type', 'location')

    if input_type == 'date':
        # ZMIANA TUTAJ: type="datetime-local" zamiast "date"
        html = '''<div class="relative mt-3">
                    <i data-lucide="calendar" class="absolute left-3 top-3 w-5 h-5 text-gray-400"></i>
                    <input type="datetime-local" name="dates" class="w-full border border-gray-300 rounded-lg p-2.5 pl-10 focus:ring-blue-500 focus:border-blue-500">
                  </div>'''
    else:
        html = '''<div class="relative mt-3">
                    <i data-lucide="map-pin" class="absolute left-3 top-3 w-5 h-5 text-gray-400"></i>
                    <input type="text" name="locations" placeholder="Kolejna lokalizacja..." class="w-full border border-gray-300 rounded-lg p-2.5 pl-10 focus:ring-blue-500 focus:border-blue-500">
                  </div>'''

    html += '<script>lucide.createIcons();</script>'
    return HttpResponse(html)