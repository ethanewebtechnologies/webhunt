from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template import loader
from django.core.files.storage import FileSystemStorage
from .models import ChContactTbl
import csv,os,sys
from checken.magic_mail import Crack_hunt
from .forms import SignUpForm, UploadFileForm

# Create your views here.
def index(request):
    template = loader.get_template('crackan/index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = SignUpForm()
    
    template = loader.get_template('crackan/signup.html')
    context = {'form': form}
    return HttpResponse(template.render(context, request))

def hunt(request):
    if request.method == 'POST' and request.POST.get('report_for_this_url'):
        webhunt_url = request.POST.get('report_for_this_url')
        ch = Crack_hunt(webhunt_url)
        ch.run()

        if ch:
            template = loader.get_template('crackan/seo_report.html')
            context = {
                'report': ch
            }
            return HttpResponse(template.render(context, request))

    raise Http404

def ajax_hunt(request):
    if request.method == 'POST' and request.POST.get('report_for_this_url'):
        webhunt_url = request.POST.get('report_for_this_url')
        ch = Crack_hunt(webhunt_url)
        ch.run()

        if ch:
            template = loader.get_template('crackan/seo_report.html')
            context = {
                'report': ch
            }
            return HttpResponse(template.render(context, request))

    raise Http404
    
@login_required
def upload_contact(request):
    request.session['error'] = False;
    form = UploadFileForm()
    template = loader.get_template('crackan/upload_contact.html')
    context = {'form': form}
    return HttpResponse(template.render(context, request))

def hunt_and_send(request):
    db_items = ChContactTbl.objects.filter(crawl_status=0)[0:1]
    
    if len(db_items) == 1:
        ch = Crack_hunt(db_items[0].contact_url, db_items[0].contact_email)
        ch.run()
        ChContactTbl.objects.filter(pk=db_items[0].contact_id).update(crawl_status='1')
    else:
        pass
    
    template = loader.get_template('crackan/success_crawled.html')
    context = {}
    return HttpResponse(template.render(context, request))

@login_required
def simple_upload(request):
    if request.method == 'POST' and request.FILES['contact_file']:
        myfile = request.FILES['contact_file']
        fs = FileSystemStorage()
        filename = fs.save('contacts.csv', myfile)
        uploaded_file_url = fs.url(filename)
        
        with open('media/contacts.csv', 'r+') as csv_file:
            reader = csv.reader(csv_file)
            i = 0
            for row in reader:
                if i == 0:
                    i=i+1
                    continue
                contact_items = ChContactTbl.objects.filter(contact_email=row[0], contact_url=row[1])
                if len(contact_items) == 0:
                    contact = ChContactTbl(contact_email=row[0], contact_url=row[1])
                    try:
                        contact.save()
                    except:
                        print ("there was a problem with line", i)
                    i = i+1

        if os.path.isfile('media/contacts.csv'):
            os.remove('media/contacts.csv')
        
        template = loader.get_template('crackan/success_upload.html')
        context = {}
        return HttpResponse(template.render(context, request))
    
    request.session['error'] = True;
    return HttpResponseRedirect('/uploads/')

@login_required
def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def handler404(request, exception, template_name="404.html"):
    response = render_to_response("404.html")
    response.status_code = 404
    return response

def handler500(request, exception, template_name="500.html"):
    response = render_to_response("500.html")
    response.status_code = 500
    return response
    
def handler403(request, exception, template_name="403.html"):
    response = render_to_response("403.html")
    response.status_code = 403
    return response

def handler400(request, exception, template_name="400.html"):
    response = render_to_response("400.html")
    response.status_code = 400
    return response