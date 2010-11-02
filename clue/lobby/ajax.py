from datetime import datetime, timedelta
from django.contrib import auth
from django.http import *
from django.shortcuts import render_to_response,  get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import *
from lobby import *
from lobby.models import *
from lb.util import *

@login_required
def send_message(request):
    to = User.objects.get(id=request.REQUEST['to'])
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    sender = request.user
    content = request.REQUEST['content']
    
    new_message = Message(
        sender=sender,
        to=to,
        content=content,
        lobby=lobby
    )
    new_message.save()
    return HttpResponse()

@login_required
def get_messages(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    messages = Message.objects.filter(to=request.user).filter(lobby=lobby).select_related('user').all()

    out = serialize_qs(messages, related=['sender'])
    return HttpResponse(json.dumps(out))
    
@login_required
def get_members(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    members = lobby.members.all()
    out = serialize_qs(members, related=['user'])

    return HttpResponse(json.dumps(out))
    
def get_lobby(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    
    resp = expand(lobby)
    resp['members'] = serialize_qs(lobby.members.all(), related=['user'])
    
    return HttpResponse(json.dumps(resp))
    
@login_required
def add_cpu_user(request):
    lobby = Lobby.objects.get(id=request.REQUEST['lobby'])
    members = lobby.members.all()
    user_ids = []
    
    for member in members:
        user_ids.append(member.user.id)
    
    user = User.objects.filter(is_active=False).exclude(id__in=user_ids)[0]
    
    cpu_member = Member(
        user = user,
        lobby = lobby
    )
    cpu_member.save()
    
    return HttpResponse("")