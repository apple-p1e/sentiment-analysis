from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.views import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from website.models import Publication, Comment, RunningTask
from website.tasks import run_classifier
from website import forms


def home(request):
    if request.user.is_anonymous():
        return HttpResponseRedirect('/login')
    else:
        return HttpResponseRedirect('/feed')


def login_user(request):
    if request.user.is_anonymous():
        return login(
            request, template_name='login.html',
            authentication_form=forms.BootstrapAuthenticationForm)
    else:
        if request.GET.get('action', None) == 'logout':
            return logout(request, next_page='/login')
        return HttpResponseRedirect('/')


def signup(request):
    if request.user.is_anonymous():
        if request.method == "POST":
            form = forms.SignupForm(data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/login')
        else:
            form = forms.SignupForm()
        return render_to_response(
            'signup.html', {'form': form},
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')


@login_required
def feed(request):
    return render_to_response(
        'feed.html', context_instance=RequestContext(request))


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render_to_response(
        'profile.html', {'profile': user},
        context_instance=RequestContext(request))


@login_required
def publication(request, pk):
    pub = get_object_or_404(Publication, pk=pk)
    return render_to_response(
        'publication.html', {'publication': pub},
        context_instance=RequestContext(request))


@login_required
def upload(request):
    if request.method == "POST":
        form = forms.UploadForm(request.POST, request.FILES)
        if form.is_valid():
            pub = Publication(user=request.user, image_file=request.FILES['image'])
            pub.save()
    return HttpResponseRedirect('/')


@login_required
def classification(request):
    if request.user.is_superuser:
        values = {'not_finished': False}
        tasks = RunningTask.objects.all()
        if request.method == 'POST':
            if tasks:
                return HttpResponseForbidden()
            else:
                c = Comment.objects.filter(polarity=Comment.UNDEFINED)
                docs = [{'id': comment.id, 'text': comment.text} for comment in c]
                run_task = run_classifier.delay(docs)
                task = RunningTask(user=request.user, running_id=run_task.id)
                task.save()
                return HttpResponseRedirect('/classification')
        if tasks:
            task = tasks[0]
            run_task = run_classifier.AsyncResult(task.running_id)
            if run_task.status == "SUCCESS":
                task.delete()
            else:
                values['not_finished'] = True
                values['user_task'] = task.user.username
        publications = list(Publication.objects.all())
        publications.sort(
            key=lambda obj: len(obj.comments.filter(
                polarity=Comment.POSITIVE))-len(obj.comments.filter(polarity=Comment.NEGATIVE)))
        values['publications'] = publications
        return render_to_response(
            'classification.html', values,
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')