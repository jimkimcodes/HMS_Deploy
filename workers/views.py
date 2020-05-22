from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse
from workers.models import Medical, Workers
from institute.models import Blocks
from complaints.models import Complaints, OfficialComplaints
from students.models import details
from django.contrib import messages

# Create your views here.
def staff_home(request):
    staff_id = request.COOKIES['username_staff']
    user_details = Workers.objects.get(staff_id=str(staff_id))
    

    complaints = list()
    if user_details.designation == 'General Servant':
        studs = details.objects.filter(block_id=Blocks.objects.get(block_id=str(user_details.block.block_id)))
        for stud in studs:
            complaints += list((Complaints.objects.filter(regd_no=str(stud.regd_no), type='Room Cleaning', status='Registered')))

    if user_details.designation == 'Scavenger':
        studs = details.objects.filter(block_id=Blocks.objects.get(block_id=str(user_details.block.block_id)))
        for stud in studs:
            complaints += list((Complaints.objects.filter(regd_no=str(stud.regd_no), type='Restroom Cleaning', status='Registered')))

    if user_details.designation == 'Electrician':
            complaints += list((Complaints.objects.filter(type='Electrical', status='Registered')))

    if user_details.designation == 'Mess Incharge':
            complaints += list((Complaints.objects.filter(type='Food Issues', status='Registered')))

    medical = list()
    if user_details.designation == 'Doctor':
        medical += list((Medical.objects.filter(status='Registered')))         


    if user_details.block: block_details = Blocks.objects.filter(block_id=user_details.block.block_id)
    else: block_details=""
    return render(request, 'workers/workers-profile.html', {'user_details': user_details, 'block_details':block_details, 'complaints':complaints, 'medical':medical})


def medical_issue(request):
    if request.method == 'POST':
        if request.COOKIES.get('username_std'):
                newComplaint = Medical(
                regd_no = request.COOKIES['username_std'],
                summary = request.POST['summary'],
                detailed = request.POST['detailed'],
                )
        elif request.COOKIES.get('username_off'):
                newComplaint = Medical(
                regd_no = request.COOKIES['username_off'],
                summary = request.POST['summary'],
                detailed = request.POST['detailed'],
                )
        elif request.COOKIES.get('username_staff'):
                newComplaint = Medical(
                regd_no = request.COOKIES['username_staff'],
                summary = request.POST['summary'],
                detailed = request.POST['detailed'],
                )

        else:
            raise Http404('Please Log In and then register medical issue!')
                
        newComplaint.save()
        messages.success(request, 'Medical Issue Registered Successfully!')
        return redirect('workers:medical_issue')



    return render(request, 'workers/medical.html')