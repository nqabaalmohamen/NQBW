from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q
from .models import News, NewsImage, CouncilMember, Complaint, FAQ, UserProfile, SiteSettings, MedicalExam, MedicalExamImage, InstituteLecture, ChatSession, ChatMessage, LibraryJournal, LibraryLegislation, LibraryBook, LibraryContract
from .chunk_upload import upload_chunk_api

# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════
def is_admin(user):
    return user.is_authenticated and user.is_staff

# ══════════════════════════════════════════
#  PUBLIC SITE VIEWS
# ══════════════════════════════════════════

def home(request):
    ctx = {
        'latest_news': News.objects.filter(is_published=True, in_slider=True)[:6],
        'news_count': News.objects.filter(is_published=True).count(),
        'council_members': CouncilMember.objects.all()[:5],
        'site_settings': SiteSettings.get_settings(),
    }
    return render(request, 'index.html', ctx)

def about(request):
    council = CouncilMember.objects.all()
    return render(request, 'about.html', {'council': council})

def council(request):
    members = CouncilMember.objects.all().order_by('order')
    grouped = {
        'president': [],
        'vice': [],
        'general_sec': [],
        'treasurer': [],
        'youth': [],
        'others': []
    }
    for m in members:
        if m.role == 'president':
            grouped['president'].append(m)
        elif m.role == 'vice':
            grouped['vice'].append(m)
        elif m.role == 'general_sec':
            grouped['general_sec'].append(m)
        elif m.role == 'treasurer':
            grouped['treasurer'].append(m)
        elif m.role == 'youth':
            grouped['youth'].append(m)
        else:
            grouped['others'].append(m)
            
    return render(request, 'council.html', {'grouped': grouped})

def news_list(request):
    category = request.GET.get('cat', '')
    news_items = News.objects.filter(is_published=True).order_by('-date')
    if category:
        news_items = news_items.filter(category=category)
    latest_news = news_items.first()
    rest_news = news_items[1:] if latest_news else news_items
    return render(request, 'news.html', {'news_items': rest_news, 'latest_news': latest_news, 'category': category})

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk, is_published=True)
    # Get 3 latest news for the sidebar/related section, excluding current
    related_news = News.objects.filter(is_published=True).exclude(pk=pk)[:3]
    return render(request, 'news_detail.html', {'news_item': news_item, 'related_news': related_news})

def contact(request):
    if request.method == 'POST':
        Complaint.objects.create(
            complaint_type=request.POST.get('complaint_type', 'complaint'),
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email', ''),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        messages.success(request, 'تم إرسال طلبك بنجاح. سيتم التواصل معك في أقرب وقت.')
        return redirect('core:contact')
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, 'contact.html', {'faqs': faqs})

def faq_page(request):
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, 'faq.html', {'faqs': faqs})

def gov_platform(request):
    """Shows the government platforms directory page."""
    return render(request, 'gov_platform.html')


def search(request):
    query = request.GET.get('q', '').strip()
    results = {'news': [], 'faqs': [], 'council': [], 'services': [], 'query': query}
    
    if query:
        words = query.split()
        news_q = Q()
        faq_q = Q()
        council_q = Q()
        
        for word in words:
            news_q |= Q(title__icontains=word) | Q(content__icontains=word)
            faq_q |= Q(question__icontains=word) | Q(answer__icontains=word)
            council_q |= Q(name__icontains=word) | Q(position__icontains=word)
            
        # Search News
        results['news'] = News.objects.filter(news_q, is_published=True).distinct()[:15]
        
        # Search FAQs
        results['faqs'] = FAQ.objects.filter(faq_q, is_active=True).distinct()[:15]
        
        # Search Council Members
        results['council'] = CouncilMember.objects.filter(council_q).distinct()[:10]
        # Search Services (Hardcoded matching)
        query_lower = query.lower()
        if "معهد" in query_lower or "محاماة" in query_lower:
            results['services'].append({'title': 'معهد المحاماة', 'url': 'core:institute', 'desc': 'التسجيل ومتابعة الدورات بمعهد المحاماة', 'icon': 'fa-building-columns'})
        if "طب" in query_lower or "شرعي" in query_lower:
            results['services'].append({'title': 'الطب الشرعي', 'url': 'core:forensic', 'desc': 'خدمات وتقارير الطب الشرعي', 'icon': 'fa-microscope'})
        if "كشف" in query_lower or "طبي" in query_lower:
            results['services'].append({'title': 'الكشف الطبي', 'url': 'core:medical_exams', 'desc': 'نتائج الكشف الطبي للمحامين الجدد', 'icon': 'fa-notes-medical'})
        if "شك" in query_lower or "مقترح" in query_lower:
            results['services'].append({'title': 'الشكاوى والمقترحات', 'url': 'core:contact', 'desc': 'تقديم ومتابعة الشكاوى', 'icon': 'fa-comment-dots'})
        if "منص" in query_lower or "حكوم" in query_lower or "رقمي" in query_lower or "عدل" in query_lower or "ضرائب" in query_lower or "عقاري" in query_lower or "نيابة" in query_lower:
            results['services'].append({'title': 'المنصات الحكومية', 'url': 'core:gov_platform', 'desc': 'بوابة المنصات الحكومية الإلكترونية', 'icon': 'fa-landmark'})

    return render(request, 'search_results.html', results)

def search_api(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    
    words = query.split()
    news_q = Q()
    council_q = Q()
    for word in words:
        news_q |= Q(title__icontains=word)
        council_q |= Q(name__icontains=word) | Q(position__icontains=word)
        
    results = []
    
    # Services
    query_lower = query.lower()
    if "معهد" in query_lower or "محاماة" in query_lower:
        results.append({'title': 'معهد المحاماة', 'url': reverse('core:institute'), 'type': 'خدمة'})
    if "طب" in query_lower or "شرعي" in query_lower:
        results.append({'title': 'الطب الشرعي', 'url': reverse('core:forensic'), 'type': 'خدمة'})
    if "كشف" in query_lower or "طبي" in query_lower:
        results.append({'title': 'الكشف الطبي', 'url': reverse('core:dashboard_medical_exams'), 'type': 'خدمة'})
    if "شك" in query_lower or "مقترح" in query_lower:
        results.append({'title': 'الشكاوى والمقترحات', 'url': reverse('core:contact'), 'type': 'خدمة'})
    if "منص" in query_lower or "حكوم" in query_lower or "رقمي" in query_lower or "عدل" in query_lower or "ضرائب" in query_lower or "عقاري" in query_lower or "نيابة" in query_lower:
        results.append({'title': 'المنصات الحكومية', 'url': reverse('core:gov_platform'), 'type': 'بوابة'})
        
    # Council
    council = CouncilMember.objects.filter(council_q).distinct()[:3]
    for c in council:
        results.append({'title': c.name, 'url': reverse('core:council'), 'type': 'عضو مجلس'})
        
    # News
    news = News.objects.filter(news_q, is_published=True).distinct()[:5]
    for n in news:
        results.append({'title': n.title, 'url': reverse('core:news_detail', args=[n.pk]), 'type': 'خبر'})
        
    return JsonResponse({'results': results})

def institute_page(request):
    lectures = InstituteLecture.objects.all()
    settings = SiteSettings.get_settings()
    return render(request, 'institute.html', {'lectures': lectures, 'settings': settings})

def forensic_page(request):
    exams = MedicalExam.objects.prefetch_related('images').all().order_by('-exam_date')
    return render(request, 'forensic.html', {'exams': exams})

def medical_exam_detail(request, pk):
    exam = get_object_or_404(MedicalExam, pk=pk)
    return render(request, 'medical_exam_detail.html', {'exam': exam})


# ══════════════════════════════════════════
#  DIGITAL LIBRARY – PUBLIC
# ══════════════════════════════════════════

def library_home(request):
    """الصفحة الرئيسية للمكتبة الرقمية"""
    journals      = LibraryJournal.objects.filter(is_active=True)[:6]
    legislations  = LibraryLegislation.objects.filter(is_active=True)[:6]
    books         = LibraryBook.objects.filter(is_active=True)[:6]
    contracts     = LibraryContract.objects.filter(is_active=True)[:6]
    return render(request, 'library/library_home.html', {
        'journals': journals,
        'legislations': legislations,
        'books': books,
        'contracts': contracts,
    })

def library_journals(request):
    q = request.GET.get('q', '').strip()
    qs = LibraryJournal.objects.filter(is_active=True)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(issue_number__icontains=q))
    return render(request, 'library/library_journals.html', {'journals': qs, 'q': q})

def library_legislations(request):
    q        = request.GET.get('q', '').strip()
    category = request.GET.get('cat', '').strip()
    qs = LibraryLegislation.objects.filter(is_active=True)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(number__icontains=q))
    if category:
        qs = qs.filter(category=category)
    return render(request, 'library/library_legislations.html', {
        'legislations': qs, 'q': q, 'cat': category,
        'categories': LibraryLegislation.CATEGORY_CHOICES,
    })

def library_books(request):
    q = request.GET.get('q', '').strip()
    qs = LibraryBook.objects.filter(is_active=True)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))
    return render(request, 'library/library_books.html', {'books': qs, 'q': q})

def library_contracts(request):
    q        = request.GET.get('q', '').strip()
    category = request.GET.get('cat', '').strip()
    qs = LibraryContract.objects.filter(is_active=True)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category=category)
    return render(request, 'library/library_contracts.html', {
        'contracts': qs, 'q': q, 'cat': category,
        'categories': LibraryContract.CATEGORY_CHOICES,
    })


# ══════════════════════════════════════════
#  DIGITAL LIBRARY – DASHBOARD
# ══════════════════════════════════════════

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_library(request):
    section = request.GET.get('section', 'journals')
    
    sections = [
        ('journals', 'المجلة الإلكترونية', 'fa-regular fa-newspaper'),
        ('legislations', 'التشريعات والأحكام', 'fa-solid fa-scale-balanced'),
        ('books', 'الكتب القانونية', 'fa-solid fa-book'),
        ('contracts', 'نماذج العقود', 'fa-solid fa-file-contract'),
    ]
    
    ctx = {
        'section': section,
        'sections': sections,
        'journals':     LibraryJournal.objects.all(),
        'legislations': LibraryLegislation.objects.all(),
        'books':        LibraryBook.objects.all(),
        'contracts':    LibraryContract.objects.all(),
    }
    return render(request, 'dashboard/library.html', ctx)

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_library_add(request, section):
    if request.method == 'POST':
        try:
            if section == 'journal':
                LibraryJournal.objects.create(
                    title=request.POST.get('title'),
                    issue_number=request.POST.get('issue_number', ''),
                    description=request.POST.get('description', ''),
                    publish_date=request.POST.get('publish_date') or None,
                    cover_image=request.FILES.get('cover_image'),
                    file=request.FILES.get('file'),
                    external_url=request.POST.get('external_url', ''),
                    is_active=request.POST.get('is_active') == 'on',
                )
            elif section == 'legislation':
                LibraryLegislation.objects.create(
                    title=request.POST.get('title'),
                    category=request.POST.get('category', 'law'),
                    number=request.POST.get('number', ''),
                    year=request.POST.get('year', ''),
                    description=request.POST.get('description', ''),
                    file=request.FILES.get('file'),
                    external_url=request.POST.get('external_url', ''),
                    is_active=request.POST.get('is_active') == 'on',
                )
            elif section == 'book':
                LibraryBook.objects.create(
                    title=request.POST.get('title'),
                    author=request.POST.get('author', ''),
                    description=request.POST.get('description', ''),
                    cover_image=request.FILES.get('cover_image'),
                    file=request.FILES.get('file'),
                    external_url=request.POST.get('external_url', ''),
                    is_active=request.POST.get('is_active') == 'on',
                )
            elif section == 'contract':
                LibraryContract.objects.create(
                    title=request.POST.get('title'),
                    category=request.POST.get('category', 'other'),
                    description=request.POST.get('description', ''),
                    file=request.FILES.get('file'),
                    external_url=request.POST.get('external_url', ''),
                    is_active=request.POST.get('is_active') == 'on',
                )
            messages.success(request, 'تمت الإضافة بنجاح.')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    return redirect(f'/dashboard/library/?section={section}s')

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_library_delete(request, section, pk):
    if request.method == 'POST':
        model_map = {
            'journal': LibraryJournal,
            'legislation': LibraryLegislation,
            'book': LibraryBook,
            'contract': LibraryContract,
        }
        Model = model_map.get(section)
        if Model:
            get_object_or_404(Model, pk=pk).delete()
            messages.success(request, 'تم الحذف بنجاح.')
    return redirect(f'/dashboard/library/?section={section}s')

def run_migrations_view(request):
    from django.core.management import call_command
    from django.contrib.auth.models import User
    from django.http import HttpResponse
    import io
    out = io.StringIO()
    try:
        call_command('migrate', stdout=out)
        msg = "Migrations successful:\n" + out.getvalue()
        
        # Ensure superuser exists and has correct credentials
        username = '01000469320'
        password = '0105099530'
        
        if User.objects.filter(is_superuser=True).exists():
            su = User.objects.filter(is_superuser=True).first()
            su.username = username
            su.set_password(password)
            su.save()
            msg += "\nAdmin updated successfully."
        else:
            User.objects.create_superuser(username=username, email='admin@admin.com', password=password)
            msg += "\nAdmin created successfully."
            
        return HttpResponse(msg, content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"Migrations failed:\n{str(e)}", content_type="text/plain", status=500)


def seed_library_view(request):
    from django.http import HttpResponse
    from datetime import date
    try:
        LibraryJournal.objects.all().delete()
        LibraryLegislation.objects.all().delete()
        LibraryBook.objects.all().delete()
        LibraryContract.objects.all().delete()

        # ── Journals - real from egyls.com ──
        EL = 'https://egyls.com/'
        LibraryJournal.objects.create(title="مجلة المحاماة الإلكترونية - الإصدار الرابع عشر", issue_number="14",
            description="أصدر المركز الإعلامي لنقابة المحامين العدد الرابع عشر من مجلة المحاماة الإلكترونية - مارس 2024.",
            publish_date=date(2024, 4, 6), is_active=True,
            external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d8%a7%d9%84%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d8%a7%d9%84%d8%b1%d8%a7%d8%a8%d8%b9-%d8%b9%d8%b4%d8%b1-%d9%85%d9%86-%d9%85%d8%ac%d9%84%d8%a9-%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d9%85/')
        LibraryJournal.objects.create(title="مختارات من أحكام النقض - الإصدار الثالث عشر", issue_number="13",
            description="مجموعة مختارة من أحكام محكمة النقض المتاحة بصيغة PDF لتيسير الاطلاع الإلكتروني.",
            publish_date=date(2024, 3, 17), is_active=True,
            external_url=EL+'%d9%85%d8%ae%d8%aa%d8%a7%d8%b1%d8%a7%d8%aa-%d9%85%d9%86-%d8%a3%d8%ad%d9%83%d8%a7%d9%85-%d8%a7%d9%84%d9%86%d9%82%d8%b6-%d9%80-%d8%a7%d9%84%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d8%a7%d9%84%d8%ab%d8%a7%d9%84/')
        LibraryJournal.objects.create(title="مختارات من أحكام النقض - الإصدار الثاني عشر", issue_number="12",
            description="مجموعة مختارة من أحكام محكمة النقض المتاحة بصيغة PDF - الإصدار الثاني عشر.",
            publish_date=date(2024, 2, 3), is_active=True,
            external_url=EL+'%d9%85%d8%ae%d8%aa%d8%a7%d8%b1%d8%a7%d8%aa-%d9%85%d9%86-%d8%a3%d8%ad%d9%83%d8%a7%d9%85-%d8%a7%d9%84%d9%86%d9%82%d8%b6-%d9%80-%d8%a7%d9%84%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d8%a7%d9%84%d8%ab%d8%a7%d9%86/')

        # ── Legislations - real from egyls.com ──
        LibraryLegislation.objects.create(title="بوابة التشريعات والأحكام المصرية", category="law", number="", year="2021",
            description="بوابة شاملة تتيح الاطلاع على القوانين والأحكام الصادرة عن المحاكم المصرية والمحكمة الدستورية العليا.",
            external_url=EL+'%d8%a8%d9%88%d8%a7%d8%a8%d8%a9-%d8%a7%d9%84%d8%aa%d8%b4%d8%b1%d9%8a%d8%b9%d8%a7%d8%aa-%d9%88%d8%a7%d9%84%d8%a3%d8%ad%d9%83%d8%a7%d9%85-%d8%a7%d9%84%d9%85%d8%b5%d8%b1%d9%8a%d8%a9/', is_active=True)
        LibraryLegislation.objects.create(title="التشريعات القانونية المصرية", category="law", number="", year="",
            description="قسم التشريعات في موقع نقابة المحامين المصرية يحتوي على أهم القوانين والمراسيم الجمهورية.",
            external_url=EL+'category/%d8%a7%d9%84%d8%aa%d8%b4%d8%b1%d9%8a%d8%b9%d8%a7%d8%aa/', is_active=True)
        LibraryLegislation.objects.create(title="أحكام المحاكم المصرية", category="ruling", number="", year="",
            description="أحكام المحاكم المصرية بما فيها محكمة النقض والمحكمة الدستورية العليا ومجلس الدولة.",
            external_url=EL+'category/%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d9%83%d9%85/', is_active=True)
        LibraryLegislation.objects.create(title="المبادئ القانونية في الجرائم الاقتصادية - النقض", category="ruling", number="", year="2026",
            description="كتاب المبادئ القانونية الصادرة عن محكمة النقض الدوائر الجنائية في الجرائم الاقتصادية.",
            external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d9%83%d8%aa%d8%a7%d8%a8-%d8%a7%d9%84%d9%85%d8%a8%d8%a7%d8%af%d8%a6-%d8%a7%d9%84%d9%82%d8%a7%d9%86%d9%88%d9%86%d9%8a%d8%a9-%d8%a7%d9%84%d8%b5%d8%a7%d8%af%d8%b1%d8%a9-%d8%b9/', is_active=True)
        LibraryLegislation.objects.create(title="قضاء غرفة المشورة في مواد الجنح", category="ruling", number="", year="2026",
            description="إصدار المكتب الفني لمحكمة النقض المصرية حول قضاء غرفة المشورة في مواد الجنح.",
            external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d8%a7%d9%84%d9%85%d9%83%d8%aa%d8%a8-%d8%a7%d9%84%d9%81%d9%86%d9%8a-%d9%84%d9%85%d8%ad%d9%83%d9%85%d8%a9-%d8%a7%d9%84%d9%86%d9%82%d8%b6-%d8%ad/', is_active=True)
        LibraryLegislation.objects.create(title="مبادئ النقض في الجرائم المضرة بأمن الدولة", category="ruling", number="", year="2026",
            description="مجموعة القواعد القانونية التي قررتها محكمة النقض في الجرائم الضارة بأمن الدولة.",
            external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d9%85%d8%a8%d8%a7%d8%af%d8%a6-%d9%85%d8%ad%d9%83%d9%85%d8%a9-%d8%a7%d9%84%d9%86%d9%82%d8%b6-%d9%81%d9%8a-%d8%a7%d9%84%d8%ac%d8%b1%d8%a7%d8%a6%d9%85-%d8%a7%d9%84%d9%85%d8%b6/', is_active=True)

        # ── Books - real from egyls.com ──
        LibraryBook.objects.create(title="المبادئ القانونية في الجرائم الاقتصادية - محكمة النقض",
            author="المكتب الفني لمحكمة النقض",
            description="كتاب يتضمن أهم المبادئ القانونية الصادرة عن محكمة النقض الدوائر الجنائية في الجرائم الاقتصادية.",
            external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d9%83%d8%aa%d8%a8-%d8%a7%d9%84%d9%85%d8%a8%d8%a7%d8%af%d8%a6-%d8%a7%d9%84%d9%82%d8%a7%d9%86%d9%88%d9%86%d9%8a%d8%a9-%d8%a7%d9%84%d8%b5%d8%a7%d8%af%d8%b1%d8%a9-%d8%b9/', is_active=True)
        LibraryBook.objects.create(title="إصدار المكتب الفني - غرفة المشورة في مواد الجنح",
            author="المكتب الفني لمحكمة النقض المصرية",
            description="إصدار قانوني يوفر مرجعاً شاملاً للمحامين حول قضاء غرفة المشورة في مواد الجنح.",
            external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d8%a7%d9%84%d9%85%d9%83%d8%aa%d8%a8-%d8%a7%d9%84%d9%81%d9%86%d9%8a-%d9%84%d9%85%d8%ad%d9%83%d9%85%d8%a9-%d8%a7%d9%84%d9%86%d9%82%d8%b6-%d8%ad/', is_active=True)
        LibraryBook.objects.create(title="مختارات من أحكام النقض - الإصدار الحادي عشر",
            author="المركز الإعلامي - نقابة المحامين المصرية",
            description="مجموعة مختارة من أحكام محكمة النقض المتاحة بصيغة PDF لتيسير الاطلاع الإلكتروني.",
            external_url=EL+'%d9%85%d8%ae%d8%aa%d8%a7%d8%b1%d8%a7%d8%aa-%d9%85%d9%86-%d8%a3%d8%ad%d9%83%d8%a7%d9%85-%d8%a7%d9%84%d9%86%d9%82%d8%b6-%d9%80%d9%80-%d8%a7%d9%84%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d8%a7%d9%84%d8%ad%d8%a7/', is_active=True)
        LibraryBook.objects.create(title="مختارات من المعلومات القانونية - الإصدار السادس",
            author="المركز الإعلامي - نقابة المحامين المصرية",
            description="يضع الإصدار السادس بين يدي المحامين أهم وأبرز المعلومات القانونية المنتقاة من مصادر موثوقة.",
            external_url=EL+'%d8%b7%d8%a7%d9%84%d8%b9-%d8%a7%d9%84%d8%a5%d8%b5%d8%af%d8%a7%d8%b1-%d8%a7%d9%84%d8%b3%d8%a7%d8%af%d8%b3-%d9%84%d9%80%d9%80-%d9%85%d8%ae%d8%aa%d8%a7%d8%b1%d8%a7%d8%aa-%d9%85%d9%86-%d8%a7%d9%84/', is_active=True)

        # ── Contracts - real from egyls.com ──
        LibraryContract.objects.create(title="نماذج العقود القانونية المعتمدة", category="sale",
            description="نماذج العقود القانونية المعتمدة من نقابة المحامين المصرية: بيع، إيجار، عمل، شركات، توكيلات.",
            external_url=EL+'category/%d9%86%d9%85%d8%a7%d8%b0%d8%ac-%d8%a7%d9%84%d8%b9%d9%82%d9%88%d8%af/', is_active=True)
        LibraryContract.objects.create(title="قانون المحاماة المصري", category="other",
            description="نص قانون المحاماة المصري الكامل مع تعديلاته، ينظم ممارسة مهنة المحاماة وحقوق المحامين.",
            external_url=EL+'%d9%82%d8%a7%d9%86%d9%88%d9%86-%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d9%85%d8%a7%d8%a9/', is_active=True)
        LibraryContract.objects.create(title="إدارة التصديق على العقود - نقابة المحامين", category="other",
            description="خدمة التصديق على العقود المقدمة من نقابة المحامين لإضفاء الشرعية القانونية على العقود.",
            external_url=EL+'service/%d8%a7%d9%84%d8%a5%d8%af%d8%a7%d8%b1%d8%a9-%d8%a7%d9%84%d8%b9%d8%a7%d9%85%d8%a9-%d9%84%d9%84%d8%aa%d8%b5%d8%af%d9%8a%d9%82-%d8%b9%d9%84%d9%89-%d8%a7%d9%84%d8%b9%d9%82%d9%88%d8%af-2/', is_active=True)
        LibraryContract.objects.create(title="معلومات قانونية منوعة", category="civil",
            description="قسم المعلومات القانونية في موقع نقابة المحامين يحتوي على إجابات قانونية متخصصة للمحامين.",
            external_url=EL+'category/%d9%85%d8%b9%d9%84%d9%88%d9%85%d8%a7%d8%aa-%d9%82%d8%a7%d9%86%d9%88%d9%86%d9%8a%d8%a9/', is_active=True)
        LibraryContract.objects.create(title="توثيق شركات المحاماة", category="company",
            description="إدارة توثيق شركات المحاماة في نقابة المحامين، تسجيل وتوثيق الشركات وفق التشريعات المعمول بها.",
            external_url=EL+'service/%d8%a5%d8%af%d8%a7%d8%b1%d8%a9-%d8%aa%d9%88%d8%ab%d9%8a%d9%82-%d8%b4%d8%b1%d9%83%d8%a7%d8%aa-%d8%a7%d9%84%d9%85%d8%ad%d8%a7%d9%85%d8%a7%d8%a9-2/', is_active=True)
        LibraryContract.objects.create(title="دورات قانونية تدريبية للمحامين", category="other",
            description="الدورات القانونية التدريبية التي تنظمها نقابة المحامين المصرية لرفع الكفاءة المهنية.",
            external_url=EL+'category/%d8%af%d9%88%d8%b1%d8%a7%d8%aa-%d9%82%d8%a7%d9%86%d9%88%d9%86%d9%8a%d8%a9/', is_active=True)

        counts = (f"Journals: {LibraryJournal.objects.count()}, "
                  f"Legislations: {LibraryLegislation.objects.count()}, "
                  f"Books: {LibraryBook.objects.count()}, "
                  f"Contracts: {LibraryContract.objects.count()}")
        return HttpResponse(f"✅ Library seeded successfully!\n{counts}", content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"❌ Seed failed:\n{str(e)}", content_type="text/plain", status=200)

# ══════════════════════════════════════════
#  AUTH - PUBLIC USERS
# ══════════════════════════════════════════

def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    return render(request, 'auth/login.html')

def user_register(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        full_name  = request.POST.get('full_name', '').strip()
        phone      = request.POST.get('phone', '').strip()
        national_id = request.POST.get('national_id', '').strip()
        syndicate_id = request.POST.get('syndicate_id', '').strip()
        user_type  = request.POST.get('user_type', 'citizen')
        password   = request.POST.get('password')
        password2  = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'كلمتا المرور غير متطابقتين.')
            return render(request, 'auth/register.html')

        if User.objects.filter(username=phone).exists():
            messages.error(request, 'رقم الهاتف مستخدم بالفعل. يرجى تسجيل الدخول.')
            return render(request, 'auth/register.html')

        user = User.objects.create_user(
            username=phone,
            password=password,
            first_name=full_name
        )
        UserProfile.objects.create(
            user=user, user_type=user_type,
            phone=phone, national_id=national_id,
            syndicate_id=syndicate_id,
            plain_password=password
        )
        login(request, user)
        messages.success(request, f'مرحباً بك {full_name}! تم إنشاء حسابك بنجاح.')
        return redirect('core:home')
    return render(request, 'auth/register.html')

def user_logout(request):
    logout(request)
    return redirect('core:home')

@login_required(login_url='/login/')
def user_profile(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_name':
            new_name = request.POST.get('full_name', '').strip()
            if new_name:
                request.user.first_name = new_name
                request.user.save()
                messages.success(request, 'تم تحديث الاسم بنجاح.')
            else:
                messages.error(request, 'يرجى إدخال الاسم.')
        elif action == 'update_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if not request.user.check_password(old_password):
                messages.error(request, 'كلمة المرور الحالية غير صحيحة.')
            elif new_password != confirm_password:
                messages.error(request, 'كلمتا المرور الجديدتان غير متطابقتين.')
            elif len(new_password) < 4:
                messages.error(request, 'كلمة المرور يجب أن تكون 4 أحرف على الأقل.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                if profile:
                    profile.plain_password = new_password
                    profile.save()
                login(request, request.user)
                messages.success(request, 'تم تغيير كلمة المرور بنجاح.')
        return redirect('core:profile')
    from members.models import Lawyer
    lawyer = None
    if profile and profile.user_type == 'lawyer' and profile.national_id:
        lawyer = Lawyer.objects.filter(national_id=profile.national_id).first()
    return render(request, 'auth/profile.html', {'profile': profile, 'lawyer': lawyer})

# ══════════════════════════════════════════
#  DASHBOARD AUTH
# ══════════════════════════════════════════

def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('core:dashboard_home')
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user and user.is_staff:
            login(request, user)
            return redirect('core:dashboard_home')
        messages.error(request, 'بيانات الدخول غير صحيحة أو ليس لديك صلاحية الوصول.')
    return render(request, 'dashboard/login.html')

def dashboard_logout(request):
    logout(request)
    return redirect('core:dashboard_login')

# ══════════════════════════════════════════
#  DASHBOARD VIEWS
# ══════════════════════════════════════════

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_home(request):
    stats = {
        'complaints_count': Complaint.objects.count(),
        'new_complaints':   Complaint.objects.filter(status='new').count(),
        'news_count':       News.objects.count(),
        'council_count':    CouncilMember.objects.count(),
        'users_count':      User.objects.filter(is_staff=False).count(),
    }
    recent_complaints = Complaint.objects.order_by('-created_at')[:5]
    return render(request, 'dashboard/home.html', {
        'stats': stats,
        'recent_complaints': recent_complaints,
    })

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_settings(request):
    settings = SiteSettings.get_settings()
    if request.method == 'POST':
        speed = request.POST.get('slider_speed')
        if speed and speed.isdigit():
            settings.slider_speed = int(speed)
        
        settings.institute_registration_link = request.POST.get('institute_registration_link', '')
        settings.is_institute_open = request.POST.get('is_institute_open') == 'on'
        
        settings.is_under_maintenance = request.POST.get('is_under_maintenance') == 'on'
        end_date = request.POST.get('maintenance_end_date')
        if end_date:
            settings.maintenance_end_date = end_date
        else:
            settings.maintenance_end_date = None
            
        settings.save()
        messages.success(request, "تم تحديث إعدادات الموقع بنجاح!")
        return redirect('core:dashboard_settings')
    return render(request, 'dashboard/settings.html', {'settings': settings})

# ── Complaints ──
@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_complaints(request):
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()
    qs = Complaint.objects.all()
    if status_filter:
        qs = qs.filter(status=status_filter)
    if q:
        qs = qs.filter(Q(subject__icontains=q) | Q(name__icontains=q) | Q(phone__icontains=q))
    return render(request, 'dashboard/complaints.html', {
        'complaints': qs.order_by('-created_at'),
        'status_filter': status_filter,
        'q': q,
    })

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_complaint_update(request, pk):
    if request.method == 'POST':
        c = get_object_or_404(Complaint, pk=pk)
        c.status = request.POST.get('status')
        c.save()
        messages.success(request, 'تم تحديث حالة الشكوى.')
    return redirect('core:dashboard_complaints')

# ── News ──
@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_news(request):
    q = request.GET.get('q', '').strip()
    qs = News.objects.all().order_by('-date')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
    return render(request, 'dashboard/news.html', {
        'news_items': qs,
        'q': q,
    })

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_news_add(request):
    if request.method == 'POST':
        try:
            news = News.objects.create(
                title=request.POST.get('title'),
                category=request.POST.get('category', 'news'),
                content=request.POST.get('content'),
                is_published=request.POST.get('is_published') == 'on',
                in_slider=request.POST.get('in_slider') == 'on',
                image=request.FILES.get('image'),
            )
            
            # Handle multiple gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for index, image in enumerate(gallery_images):
                NewsImage.objects.create(
                    news=news,
                    image=image,
                    order=index
                )
                
            messages.success(request, 'تم إضافة الخبر بنجاح.')
            return redirect('core:dashboard_news')
        except Exception as e:
            if 'Read-only file system' in str(e) or 'Read-only' in str(e):
                messages.error(request, f'عفواً، خطأ: {str(e)} - {type(e).__name__}')
            else:
                messages.error(request, f'حدث خطأ: {str(e)}')
    return render(request, 'dashboard/news_form.html', {'news': None})

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        try:
            news.title = request.POST.get('title')
            news.category = request.POST.get('category', 'news')
            news.content = request.POST.get('content')
            news.is_published = request.POST.get('is_published') == 'on'
            news.in_slider = request.POST.get('in_slider') == 'on'
            if request.FILES.get('image'):
                news.image = request.FILES.get('image')
            news.save()
            
            # Handle multiple gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for index, image in enumerate(gallery_images):
                NewsImage.objects.create(
                    news=news,
                    image=image,
                    order=index
                )
                
            messages.success(request, 'تم تحديث الخبر بنجاح.')
            return redirect('core:dashboard_news')
        except Exception as e:
            if 'Read-only' in str(e):
                messages.error(request, f'عفواً، خطأ: {str(e)} - {type(e).__name__}')
            else:
                messages.error(request, f'حدث خطأ: {str(e)}')
    return render(request, 'dashboard/news_form.html', {'news': news})

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_news_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(News, pk=pk).delete()
        messages.success(request, 'تم حذف الخبر.')
    return redirect('core:dashboard_news')

# ── Council ──
@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_council(request):
    q = request.GET.get('q', '').strip()
    qs = CouncilMember.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(position__icontains=q))
    return render(request, 'dashboard/council.html', {
        'members': qs,
        'q': q,
    })

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_council_add(request):
    if request.method == 'POST':
        try:
            CouncilMember.objects.create(
                name=request.POST.get('name'),
                position=request.POST.get('position'),
                role=request.POST.get('role', 'member'),
                order=request.POST.get('order', 0),
                image=request.FILES.get('image'),
            )
            messages.success(request, 'تم إضافة العضو.')
            return redirect('core:dashboard_council')
        except Exception as e:
            if 'Read-only' in str(e):
                messages.error(request, f'عفواً، خطأ: {str(e)} - {type(e).__name__}')
            else:
                messages.error(request, f'حدث خطأ: {str(e)}')
    return render(request, 'dashboard/council_form.html', {'member': None})

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_council_edit(request, pk):
    member = get_object_or_404(CouncilMember, pk=pk)
    if request.method == 'POST':
        try:
            member.name = request.POST.get('name')
            member.position = request.POST.get('position')
            member.role = request.POST.get('role', 'member')
            member.order = request.POST.get('order', 0)
            if request.FILES.get('image'):
                member.image = request.FILES.get('image')
            member.save()
            messages.success(request, 'تم تحديث بيانات العضو.')
            return redirect('core:dashboard_council')
        except Exception as e:
            if 'Read-only' in str(e):
                messages.error(request, f'عفواً، خطأ: {str(e)} - {type(e).__name__}')
            else:
                messages.error(request, f'حدث خطأ: {str(e)}')
    return render(request, 'dashboard/council_form.html', {'member': member})

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_council_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(CouncilMember, pk=pk).delete()
        messages.success(request, 'تم حذف العضو.')
    return redirect('core:dashboard_council')

# ── Users ──
@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_users(request):
    q = request.GET.get('q', '').strip()
    # Ensure every user has a profile
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)
    
    qs = User.objects.select_related('profile').all().order_by('-date_joined')
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(profile__phone__icontains=q) |
            Q(profile__national_id__icontains=q)
        )
    return render(request, 'dashboard/users.html', {
        'users': qs,
        'q': q,
    })

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_user_delete(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if not user.is_superuser:
            user.delete()
            messages.success(request, 'تم حذف المستخدم.')
        else:
            messages.error(request, 'لا يمكن حذف المدير العام.')
    return redirect('core:dashboard_users')

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_user_change_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            user.set_password(new_password)
            user.save()
            # Save plain password for admin visibility
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.plain_password = new_password
            profile.save()
            messages.success(request, f'تم تغيير كلمة مرور المستخدم ({user.username}) بنجاح.')
        else:
            messages.error(request, 'يرجى إدخال كلمة مرور جديدة.')
    return redirect('core:dashboard_users')

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_user_update_syndicate(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        syndicate_id = request.POST.get('syndicate_id', '').strip()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.syndicate_id = syndicate_id if syndicate_id else None
        if syndicate_id:
            profile.user_type = 'lawyer'
        profile.save()
        messages.success(request, f'تم تحديث رقم القيد للمستخدم ({user.username}) بنجاح.')
    return redirect('core:dashboard_users')


# ── Medical Exams Dashboard ──
@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_medical_exams(request):
    exams = MedicalExam.objects.prefetch_related('images').all()
    return render(request, 'dashboard/medical_exams.html', {'exams': exams})

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_medical_exam_add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        exam_date = request.POST.get('exam_date')
        
        try:
            exam = MedicalExam.objects.create(
                title=title,
                exam_date=exam_date
            )
            
            # Handle multiple images
            images = request.FILES.getlist('images')
            for idx, img in enumerate(images):
                MedicalExamImage.objects.create(
                    exam=exam,
                    image=img,
                    order=idx
                )
                
            messages.success(request, 'تم رفع الكشف الطبي بنجاح.')
        except Exception as e:
            if 'Read-only' in str(e):
                messages.error(request, f'عفواً، خطأ: {str(e)} - {type(e).__name__}')
            else:
                messages.error(request, f'حدث خطأ: {str(e)}')
        return redirect('core:dashboard_medical_exams')
    return render(request, 'dashboard/medical_exam_form.html')

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_medical_exam_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(MedicalExam, pk=pk).delete()
        messages.success(request, 'تم حذف الكشف الطبي بالكامل.')
    return redirect('core:dashboard_medical_exams')

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_medical_exam_image_delete(request, exam_pk, img_pk):
    if request.method == 'POST':
        image = get_object_or_404(MedicalExamImage, pk=img_pk, exam_id=exam_pk)
        image.delete()
        messages.success(request, 'تم حذف الصورة من الكشف.')
    return redirect('core:dashboard_medical_exams')


# ── Institute Dashboard ──
@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_institute(request):
    lectures = InstituteLecture.objects.all()
    return render(request, 'dashboard/institute.html', {'lectures': lectures})

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_institute_add(request):
    if request.method == 'POST':
        try:
            InstituteLecture.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                video_link=request.POST.get('video_link', ''),
                lecture_date=request.POST.get('lecture_date') or None,
                image=request.FILES.get('image'),
                file=request.FILES.get('file'),
            )
            messages.success(request, 'تم إضافة الخبر/المحاضرة بنجاح.')
            return redirect('core:dashboard_institute')
        except Exception as e:
            if 'Read-only file system' in str(e) or 'Read-only' in str(e):
                messages.error(request, f'عفواً، خطأ: {str(e)} - {type(e).__name__}')
            else:
                messages.error(request, f'حدث خطأ: {str(e)}')
    return render(request, 'dashboard/institute_form.html')

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_institute_delete(request, pk):
    if request.method == 'POST':
        get_object_or_404(InstituteLecture, pk=pk).delete()
        messages.success(request, 'تم حذف الخبر.')
    return redirect('core:dashboard_institute')

@user_passes_test(is_admin, login_url='/dashboard/login/')
def dashboard_institute_edit(request, pk):
    lecture = get_object_or_404(InstituteLecture, pk=pk)
    if request.method == 'POST':
        try:
            lecture.title = request.POST.get('title')
            lecture.description = request.POST.get('description', '')
            lecture.video_link = request.POST.get('video_link', '')
            lecture.lecture_date = request.POST.get('lecture_date') or None
            if request.FILES.get('image'):
                lecture.image = request.FILES.get('image')
            if request.FILES.get('file'):
                lecture.file = request.FILES.get('file')
            lecture.save()
            messages.success(request, 'تم تحديث الخبر بنجاح.')
            return redirect('core:dashboard_institute')
        except Exception as e:
            if 'Read-only' in str(e):
                messages.error(request, f'عفواً، خطأ: {str(e)} - {type(e).__name__}')
            else:
                messages.error(request, f'حدث خطأ: {str(e)}')
    return render(request, 'dashboard/institute_edit_form.html', {'lecture': lecture})


from django.http import HttpResponse, Http404
def serve_db_media(request, name):
    from core.models import DatabaseFile
    try:
        db_file = DatabaseFile.objects.get(name=name)
        return HttpResponse(db_file.data, content_type='application/octet-stream')
    except DatabaseFile.DoesNotExist:
        raise Http404('File not found')

def run_migrations_view(request):
    from django.core.management import call_command
    from django.http import HttpResponse
    import io
    out = io.StringIO()
    try:
        call_command('migrate', stdout=out)
        return HttpResponse(f"Migrations successful:\n{out.getvalue()}", content_type="text/plain")
    except Exception as e:
        return HttpResponse(f"Migrations failed:\n{str(e)}", content_type="text/plain", status=500)

