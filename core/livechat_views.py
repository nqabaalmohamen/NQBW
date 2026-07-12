import uuid
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from .models import ChatSession, ChatMessage


def is_admin(user):
    return user.is_authenticated and user.is_staff


# ══════════════════════════════════════════
#  LIVE CHAT – USER API
# ══════════════════════════════════════════

@require_POST
def chat_start(request):
    """Create new chat session, return session_key."""
    try:
        data      = json.loads(request.body)
        user_name = data.get('user_name', 'مستخدم').strip() or 'مستخدم'
        session_key = uuid.uuid4().hex
        session = ChatSession.objects.create(
            session_key=session_key,
            user_name=user_name,
            status='waiting',
        )
        return JsonResponse({'ok': True, 'session_key': session_key})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@require_POST
def chat_send(request):
    """User sends a message."""
    try:
        data        = json.loads(request.body)
        session_key = data.get('session_key')
        message     = data.get('message', '').strip()
        session     = get_object_or_404(ChatSession, session_key=session_key)
        if session.status == 'ended':
            return JsonResponse({'ok': False, 'error': 'ended'})
        if message:
            ChatMessage.objects.create(session=session, sender='user', message=message)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@require_GET
def chat_poll(request):
    """Polling: return new messages & session status."""
    session_key = request.GET.get('session_key')
    after_id    = int(request.GET.get('after_id', 0))
    session     = get_object_or_404(ChatSession, session_key=session_key)
    msgs = session.messages.filter(pk__gt=after_id).values(
        'id', 'sender', 'message', 'created_at'
    )
    msgs_list = [
        {
            'id':      m['id'],
            'sender':  m['sender'],
            'message': m['message'],
            'time':    timezone.localtime(m['created_at']).strftime('%I:%M %p'),
        }
        for m in msgs
    ]
    return JsonResponse({
        'status':   session.status,
        'messages': msgs_list,
    })


# ══════════════════════════════════════════
#  LIVE CHAT – ADMIN VIEWS
# ══════════════════════════════════════════

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_livechat(request):
    waiting = ChatSession.objects.filter(status='waiting').order_by('-created_at')
    active  = ChatSession.objects.filter(status='active').order_by('-created_at')
    ended   = ChatSession.objects.filter(status='ended').order_by('-created_at')[:20]
    return render(request, 'dashboard/livechat.html', {
        'waiting': waiting,
        'active':  active,
        'ended':   ended,
    })


@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_livechat_session(request, session_key):
    session = get_object_or_404(ChatSession, session_key=session_key)
    return render(request, 'dashboard/livechat_session.html', {'session': session})


@require_POST
@user_passes_test(is_admin, login_url='/dashboard/login/')
def chat_admin_join(request, session_key):
    session = get_object_or_404(ChatSession, session_key=session_key)
    if session.status == 'waiting':
        session.status = 'active'
        session.save()
        ChatMessage.objects.create(
            session=session,
            sender='system',
            message='✅ انضم إليك مسئول من نقابة المحامين بالفيوم. يمكنك الآن بدء المحادثة.'
        )
    return JsonResponse({'ok': True})


@require_POST
@user_passes_test(is_admin, login_url='/dashboard/login/')
def chat_admin_send(request, session_key):
    try:
        data    = json.loads(request.body)
        message = data.get('message', '').strip()
        session = get_object_or_404(ChatSession, session_key=session_key)
        if message:
            ChatMessage.objects.create(session=session, sender='admin', message=message)
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@require_POST
@user_passes_test(is_admin, login_url='/dashboard/login/')
def chat_admin_end(request, session_key):
    session = get_object_or_404(ChatSession, session_key=session_key)
    session.status = 'ended'
    session.save()
    ChatMessage.objects.create(
        session=session,
        sender='system',
        message='⛔ تم إنهاء المحادثة من قِبَل المسئول. شكراً لتواصلك مع نقابة المحامين بالفيوم.'
    )
    return JsonResponse({'ok': True})


@require_POST
@user_passes_test(is_admin, login_url='/dashboard/login/')
def chat_admin_reject(request, session_key):
    session = get_object_or_404(ChatSession, session_key=session_key)
    if session.status == 'waiting':
        session.status = 'ended'
        session.save()
        ChatMessage.objects.create(
            session=session,
            sender='system',
            message='نعتذر، جميع ممثلي خدمة العملاء مشغولون حالياً. يرجى ترك استفسارك أو المحاولة لاحقاً.'
        )
    return JsonResponse({'ok': True})


@require_GET
@user_passes_test(is_admin, login_url='/dashboard/login/')
def chat_admin_poll(request, session_key):
    after_id = int(request.GET.get('after_id', 0))
    session  = get_object_or_404(ChatSession, session_key=session_key)
    msgs = session.messages.filter(pk__gt=after_id).values(
        'id', 'sender', 'message', 'created_at'
    )
    msgs_list = [
        {
            'id':      m['id'],
            'sender':  m['sender'],
            'message': m['message'],
            'time':    timezone.localtime(m['created_at']).strftime('%I:%M %p'),
        }
        for m in msgs
    ]
    return JsonResponse({
        'status':        session.status,
        'messages':      msgs_list,
        'waiting_count': ChatSession.objects.filter(status='waiting').count(),
    })


@require_GET
@user_passes_test(is_admin, login_url='/dashboard/login/')
def chat_admin_waiting_count(request):
    return JsonResponse({
        'waiting': ChatSession.objects.filter(status='waiting').count(),
        'active':  ChatSession.objects.filter(status='active').count(),
    })
