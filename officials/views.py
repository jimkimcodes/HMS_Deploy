from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from institute.models import Blocks, Institutestd, Officials
from students.models import attendance as ATT
from students.models import details
from students.models import attendance
from students.models import outing as OUTINGDB
from django.contrib import messages
from datetime import date as datePy
from django.http.response import Http404
from complaints.models import Complaints, OfficialComplaints
from workers.models import Medical, Workers
from workers.models import attendance as ATTWORKER
from django.db.models import QuerySet
from officials.models import WaterCan


# Create your views here.
@csrf_exempt
def official_home(request):
    name = request.COOKIES['username_off']
    user_details = Officials.objects.get(emp_id=str(name))
    if(user_details.designation == 'Caretaker' or user_details.designation == 'Warden'):
        try:
            block_details = Blocks.objects.get(emp_id_id=str(name))
        except Blocks.DoesNotExist:
            raise Http404("You are currently not appointed any block! Please contact Admin")

        students = details.objects.filter(block_id=block_details.block_id)
    
        present_list = list()
        absent_list = list()
        for student in students:
            if ATT.objects.get(regd_no_id=student.regd_no_id).status == 'Present':
                present_list.append(
                    {
                        'block':student,
                        'info':Institutestd.objects.get(regd_no=str(student.regd_no))
                    }
                )
            elif ATT.objects.get(regd_no_id=student.regd_no_id).status == 'Absent':
                absent_list.append(
                    {
                        'block':student,
                        'info':Institutestd.objects.get(regd_no=str(student.regd_no))
                    }
                )

        complaints = list(Complaints.objects.filter(status='Registered'))

        if request.method == 'POST':
            for item in complaints:
                newComplaint = Complaints.objects.get(id=item.id)
                newComplaint.status = request.POST[str(item.id)]
                newComplaint.save()
            else:
                messages.success(request, 'Successfully Complaints updated!')
                return redirect('officials:official_home') 

        return render(request, 'officials/caretaker-home.html', {'user_details': user_details, 'block_details':block_details,'present_list':present_list,'absent_list':absent_list, 'complaints':complaints})

    else:
        name = request.COOKIES['username_off']
        user_details = Officials.objects.get(emp_id=str(name))
        pres = attendance.objects.filter(status='Present')
        present=list()
        for item in pres:
            present.append({
                'info':Institutestd.objects.get(regd_no=str(item.regd_no)),
                'block':details.objects.get(regd_no = Institutestd.objects.get(regd_no=str(item.regd_no))),
                'block_name': Blocks.objects.get(block_id=details.objects.get(regd_no = Institutestd.objects.get(regd_no=str(item.regd_no))).block_id_id).block_name
            })

        abse = attendance.objects.filter(status='Absent')
        absent=list()
        for item in abse:
            absent.append({
                'info':Institutestd.objects.get(regd_no=str(item.regd_no)),
                'block':details.objects.get(regd_no = Institutestd.objects.get(regd_no=str(item.regd_no))),
                'block_name': Blocks.objects.get(block_id=details.objects.get(regd_no = Institutestd.objects.get(regd_no=str(item.regd_no))).block_id_id).block_name

            })
        complaints = list(Complaints.objects.all())
        offComplaints = list(OfficialComplaints.objects.all())
        complaints+=offComplaints

        if request.method == 'POST':
            for item in complaints:
                newComplaint = Complaints.objects.get(id=item.id)
                newComplaint.status = request.POST[str(item.id)]
                newComplaint.save()
            else:
                messages.success(request, 'Successfully Complaints updated!')
                return redirect('officials:official_home')

        return render(request, 'officials/chiefs-home.html', {'user_details': user_details, 'present':present, 'absent':absent, 'complaints':complaints})



def profile(request):
    name = request.COOKIES['username_off']
    user_details = Officials.objects.get(emp_id=str(name))
    block_details = Blocks.objects.filter(emp_id_id=str(name))
    complaints=user_details.offComplaints.all()

    return render(request, 'officials/profile.html', {'user_details': user_details,'block_details':block_details, 'complaints':complaints})

def chiefsProfile(request):
    name = request.COOKIES['username_off']
    user_details = Officials.objects.get(emp_id=str(name))
    block_details = Blocks.objects.filter(emp_id_id=str(name))
    complaints=user_details.offComplaints.all()

    return render(request, 'officials/chiefs-profile.html', {'user_details': user_details, 'complaints':complaints})

@csrf_exempt
def takeAttendance(request):
    name = request.COOKIES['username_off']
    off_details = Officials.objects.get(emp_id=str(name))
    block_details = Blocks.objects.get(emp_id_id=str(name))
    students = details.objects.filter(block_id=block_details.block_id)
    
    stud_list = list()
    for student in students:
        stud_list.append(
            {
                'student':student,
                'name':Institutestd.objects.get(regd_no=str(student.regd_no)).name,
            }
        )

    if request.method == 'POST':
        date=request.POST["datefield"]
        attendance_list=list()
        for stud in stud_list:
            attendance_list.append(request.POST[str(stud['student'].regd_no)]) # Storing attendance for verification
            if (request.POST[str(stud['student'].regd_no)] == 'Present'):
                current = ATT.objects.get(regd_no_id=str(stud['student'].regd_no))
                currAtt = current.dates
                if currAtt == '':
                    currAtt += date
                else:
                    currAtt += (','+date)

                if current.status == '':
                    current.status = 'Present'
                else:
                    today = datePy.today()
                    if(date == str(today)):
                        current.status = 'Present'

                current.dates = currAtt
                current.save()
            else:
                current = ATT.objects.get(regd_no_id=str(stud['student'].regd_no))
                currAtt = current.dates
                if currAtt == '':
                    currAtt += ('X'+date)
                else:
                    currAtt += (',X'+date)

                if current.status == '':
                    current.status = 'Absent'
                else:
                    today = datePy.today()
                    if(date == str(today)):
                        current.status = 'Absent'
                
                current.dates = currAtt
                current.save()

        else:
            messages.success(request, f'Attendance marked for the date: {date}')
            return redirect('officials:attendance') 


    return render(request, 'officials/attendance.html', {'off_details':off_details, 'block_details':block_details, 'stud_list':stud_list})


@csrf_exempt
def attendance_workers(request):
    name = request.COOKIES['username_off']
    off_details = Officials.objects.get(emp_id=str(name))
    block_details = Blocks.objects.get(emp_id_id=str(name))
    students = Workers.objects.filter(block=block_details.block_id)
    
    stud_list = list()
    for student in students:
        stud_list.append(
            {
                'student':student,
            }
        )

    if request.method == 'POST':
        date=request.POST["datefield"]
        attendance_list=list()
        for stud in stud_list:
            attendance_list.append(request.POST[str(stud['student'].staff_id)]) # Storing attendance for verification
            if (request.POST[str(stud['student'].staff_id)] == 'Present'):
                current = ATTWORKER.objects.get(staff_id=str(stud['student'].staff_id))
                currAtt = current.dates
                if currAtt == '':
                    currAtt += date
                else:
                    currAtt += (','+date)

                if current.status == '':
                    current.status = 'Present'
                else:
                    today = datePy.today()
                    if(date == str(today)):
                        current.status = 'Present'

                current.dates = currAtt
                current.save()
            elif (request.POST[str(stud['student'].staff_id)] == 'Absent'):
                current = ATTWORKER.objects.get(staff_id=str(stud['student'].staff_id))
                currAtt = current.dates
                if currAtt == '':
                    currAtt += ('X'+date)
                else:
                    currAtt += (',X'+date)

                if current.status == '':
                    current.status = 'Absent'
                else:
                    today = datePy.today()
                    if(date == str(today)):
                        current.status = 'Absent'
                
                current.dates = currAtt
                current.save()

        else:
            messages.success(request, f'Attendance marked for the date: {date}')
            return redirect('officials:attendance_workers') 


    return render(request, 'officials/attendance-workers.html', {'off_details':off_details, 'block_details':block_details, 'stud_list':stud_list})



def attendance_log(request):
    name = request.COOKIES['username_off']
    off_details = Officials.objects.get(emp_id=str(name))
    try:
        block_details = Blocks.objects.get(emp_id_id=str(name))
        stud_set = block_details.details_set.all()
    except:
        block_details = None

    if request.method == 'POST':
        if(request.POST["date"]):
            date=request.POST["date"]
            if block_details:
                studs = list()
                for item in stud_set:
                    studs += ATT.objects.filter(regd_no_id=item.regd_no_id)

            else:   studs = ATT.objects.all()

            pres_stud = list()
            abse_stud = list()
            for stud in studs:
                att = str(stud.dates)
                try:
                    pos = att.index(date)
                    if att[pos-1] == 'X':
                        abse_stud.append(Institutestd.objects.get(regd_no=stud.regd_no_id))
                    else: 
                        pres_stud.append(Institutestd.objects.get(regd_no=stud.regd_no_id))
                except ValueError:
                    pos = -1
            if off_details.designation == 'Deputy Chief-Warden' or off_details.designation == 'Chief-Warden':
                return render(request, 'officials/attendance-log-chief.html', {'off_details':off_details, 'block_details':block_details, 'pres_stud':pres_stud, 'abse_stud':abse_stud})
            else:
                return render(request, 'officials/attendance-log.html', {'off_details':off_details, 'block_details':block_details, 'pres_stud':pres_stud, 'abse_stud':abse_stud})


        elif(request.POST["regno"]):
            regno = request.POST["regno"]
            user_details = Institutestd.objects.get(regd_no=str(regno))
            current = attendance.objects.get(regd_no_id=regno).dates
            dates = current.split(',')
            abse = list(filter(lambda x: (x.startswith('X')), dates))
            pres = list(filter(lambda x: not (x.startswith('X')), dates))
            abse = list(map(lambda x: x.replace('X',''), abse))

            if off_details.designation == 'Deputy Chief-Warden' or off_details.designation == 'Chief-Warden':
                return render(request, 'officials/attendance-log-chief.html', {'off_details':off_details, 'block_details':block_details, 'pres_dates':pres, 'abse_dates':abse})
            else:
                return render(request, 'officials/attendance-log.html', {'off_details':off_details, 'block_details':block_details, 'pres_dates':pres, 'abse_dates':abse})

            
    if off_details.designation == 'Deputy Chief-Warden' or off_details.designation == 'Chief-Warden':
        return render(request, 'officials/attendance-log-chief.html', {'off_details':off_details, 'block_details':block_details,})
    else:
        return render(request, 'officials/attendance-log.html', {'off_details':off_details, 'block_details':block_details,})


def grantOuting(request):
    name = request.COOKIES['username_off']
    off_details = Officials.objects.get(emp_id=str(name))
    block_details = Blocks.objects.get(emp_id_id=str(name))
    students = details.objects.filter(block_id=block_details.block_id)

    stud_list = list()
    for student in students:
        outings = OUTINGDB.objects.filter(regd_no_id=str(student.regd_no), permission='Pending')
        for outing in outings:
            stud_list.append(
                {
                    'outing': outing,
                    'info':Institutestd.objects.get(regd_no=str(student.regd_no)),
                }
            )


    if request.method == 'POST':
        for stud in stud_list:
            if request.POST[str(stud['outing'].id)] !='':
                updateOuting = OUTINGDB.objects.get(id=stud['outing'].id)
                updateOuting.permission = request.POST[str(stud['outing'].id)]
                updateOuting.save()
        else:
            messages.success(request, 'Selected Outing requests updated!')
            return redirect('officials:grantOuting') 

    return render(request, 'officials/outingPending.html', {'off_details':off_details, 'stud_list':stud_list})


@csrf_exempt
def search(request):
    send_blocks = Blocks.objects.all()
    if request.method == 'POST':
        if request.POST.get('regno'):
            stud = Institutestd.objects.get(regd_no=str(request.POST.get('regno')))
            block_details = details.objects.get(regd_no=stud)
            block = Blocks.objects.get(block_id=block_details.block_id_id)
            if attendance.objects.get(regd_no=stud).status=='':isPresent = 'Absent'
            else: isPresent = attendance.objects.get(regd_no=stud).status
            items={
                'stud':stud,
                'block_details':block_details,
                'block_name':block.block_name,
                'isPresent':isPresent
            }
            items_list = list()
            items_list.append(items)

            return render(request, 'officials/search.html', {'items_list':(items_list), 'send_blocks':send_blocks})

        else:
            block_name = Blocks.objects.get(block_id=request.POST['block']).block_name
            studs = details.objects.filter(block_id=request.POST['block'])
            items_list = list()
            for stud in studs:
                info = Institutestd.objects.get(regd_no=str(stud.regd_no_id))
                block_details = details.objects.get(regd_no=info)
                if attendance.objects.get(regd_no=info).status=='':isPresent = 'Absent'
                else: isPresent = attendance.objects.get(regd_no=info).status
                items={
                    'stud':info,
                    'block_details':block_details,
                    'block_name':block_name,
                    'isPresent':isPresent
                }
                items_list.append(items)
            return render(request, 'officials/search.html', {'items_list':(items_list), 'send_blocks':send_blocks})

    return render(request, 'officials/search.html',{'send_blocks':send_blocks})

@csrf_exempt
def blockSearch(request):
    send_blocks = Blocks.objects.all()
    if request.POST.get('submit'):
        block_name = Blocks.objects.get(block_id=request.POST['block']).block_name
        block_gender = Blocks.objects.get(block_id=request.POST['block']).gender
        block_care = Blocks.objects.get(block_id=request.POST['block']).emp_id_id
        cap_room = (Blocks.objects.get(block_id=request.POST['block']).capacity)*3
        room_type = Blocks.objects.get(block_id=request.POST['block']).room_type
        
        if room_type == '4S':   cap_stud = cap_room*3
        elif room_type == '2S': cap_stud = cap_room*2
        elif room_type == '1S': cap_stud = cap_room
        
        studs = details.objects.filter(block_id=request.POST['block'])
        pres_stud = studs.count()
        items_list = list()
        for stud in studs:
            info = Institutestd.objects.get(regd_no=str(stud.regd_no_id))
            block_details = details.objects.get(regd_no=info)
            if attendance.objects.get(regd_no=info).status=='':isPresent = 'Absent'
            else: isPresent = attendance.objects.get(regd_no=info).status
            items={
                'stud':info,
                'block_details':block_details,
                'isPresent':isPresent
            }
            items_list.append(items)

        return render(request, 'officials/roomLayout.html', {
            'items_list':(items_list), 
            'send_blocks':send_blocks, 
            'block_name':block_name,
            'cap_room': cap_room,
            'room_type' : room_type,
            'cap_stud' : cap_stud,
            'block_gender':block_gender,
            'block_care':block_care,
            'pres_stud':pres_stud,
            'pres_room': (int(pres_stud))//(int(room_type[0])),
            'vacant_room':cap_room - (int(pres_stud))//(int(room_type[0])) - (int(pres_stud))%(int(room_type[0])),
            'partial_room':(int(pres_stud))%(int(room_type[0])),
            })

    if request.POST.get('Add'):
        roll = (request.POST.get('roll'))
        location = (request.POST.get('room')).split('-')
        placing_block = location[0]
        placing_floor = location[1]
        placing_room = location[2]

        if details.objects.filter(regd_no=roll).exists():
            student = details.objects.get(regd_no=roll)
            if student.block_id_id != None and student.room_no != None and student.floor != None:
                messages.error(request, 'Student : '+str(roll)+' already alloted room!')
                return redirect('officials:blockSearch')
            else:
                block_req = Blocks.objects.get(block_name=placing_block)
                stud_req = Institutestd.objects.get(regd_no=roll)
                if (stud_req.gender == block_req.gender) and ((stud_req.year == 1 and block_req.room_type == '4S') or (stud_req.year == 2 and block_req.room_type == '2S') or (stud_req.year == 3 and block_req.room_type == '2S') or (stud_req.year == 4 and block_req.room_type == '1S')):
                    student.block_id = Blocks.objects.get(block_name=placing_block)
                    student.room_no = int(placing_room)
                    student.floor = placing_floor

                    student.save()
                    messages.success(request,'Student : '+str(roll)+' alloted room '+student.floor+'-'+str(student.room_no)+' in block '+str(student.block_id)+' : '+placing_block+'!')
                    return redirect('officials:blockSearch')
                else:
                    messages.error(request, 'Incompatible Block for Student with roll no. : '+str(roll)+'!')
                    return redirect('officials:blockSearch')


        else:
            messages.error(request, 'No Student with roll no. : '+str(roll)+' found!')
            return redirect('officials:blockSearch')

    if request.POST.get('change'):
        block_name = request.POST.get('block')
        block_req = Blocks.objects.get(block_name=block_name)
        studs = details.objects.filter(block_id=block_req)
        for stud in studs:
            if request.POST.get(str(stud.regd_no)):
                if request.POST.get(str(stud.regd_no)) == 'None':
                    stud.block_id = None
                    stud.room_no = None
                    stud.floor = None
                    stud.save()

                    messages.success(request, 'Student : '+str(stud.regd_no)+' removed from block : '+block_name+'!')
                    return redirect('officials:blockSearch')


                else:
                    roll = request.POST.get(str(stud.regd_no))
                    stud_req = Institutestd.objects.get(regd_no=roll)
                    student = details.objects.get(regd_no=roll)
                    if (stud_req.gender == block_req.gender) and ((stud_req.year == 1 and block_req.room_type == '4S') or (stud_req.year == 2 and block_req.room_type == '2S') or (stud_req.year == 3 and block_req.room_type == '2S') or (stud_req.year == 4 and block_req.room_type == '1S')):
                        student.block_id = stud.block_id
                        student.room_no = stud.room_no
                        student.floor = stud.floor
                        student.save()

                        stud.block_id = None
                        stud.room_no = None
                        stud.floor = None
                        stud.save()

                        messages.success(request,'Student : '+str(roll)+' alloted room '+student.floor+'-'+str(student.room_no)+' in block '+str(student.block_id)+' : '+block_name+'!')
                        messages.success(request, 'Student : '+str(stud.regd_no)+' removed from block : '+block_name+'!')
                        return redirect('officials:blockSearch')
                    else:
                        messages.error(request, 'Incompatible Block for Student with roll no. : '+str(roll)+'!')
                        return redirect('officials:blockSearch')



    return render(request, 'officials/roomLayout.html',{'send_blocks':send_blocks})




    

def register (request):
     if request.method == 'POST':
          if request.POST["submit"]:
               regdno=request.POST["regno"]
               rollno=request.POST["rollno"]
               name=request.POST["name"]
               year=request.POST["year"]
               branch=request.POST["branch"]
               gender=request.POST["type"]
               pwd=request.POST["pwd"]
               cast=request.POST["cast"]
               dob=request.POST["dob"]
               bgp=request.POST["blood"]
               email=request.POST["email"]
               ph_std=request.POST["ph_std"]
               ph_p=request.POST["ph_p"]
               ph_emr=request.POST["ph_emr"]
               address=request.POST["address"]
               photo=request.POST["photo"]
               hosteller=request.POST["hosteller"]
               amount=request.POST["amount"]
               bank=request.POST["bank"]
               ch_no=request.POST["ch_no"]
               dop=request.POST['dop']
               appli=request.POST["application"]
               undertake=request.POST["undertake"]
               recipt=request.POST["reipt"]
               afd=request.POST["afd"]
               
               if Institutestd.objects.filter(regd_no=regdno).exists():
                    messages.error(request, 'Already Registered!')
               else :
                    temp="No"
                    if amount !=None:
                         temp="Yes"
                    if bank == None and ch_no == None and dop==None and appli ==None and undertake ==None and recipt == None:
                         bank="null"
                         ch_no="null"
                         dop="null"
                         appli="null"
                         undertake="null"
                         recipt="null"
                    elif bank != None and ch_no != None and dop!=None and appli !=None and undertake !=None and recipt != None and afd==None:
                         afd="null"
                    else :
                         messages.error(request, 'Invalid Registration!')
                         return redirect('officials:register')
                    acc=Institutestd(regdno,rollno,name,year,branch,gender,pwd,cast,dob,bgp,email,ph_std,ph_p,ph_emr,address,photo,hosteller,amount,bank,ch_no,dop,appli,undertake,recipt,afd,temp)
                    acc.save()
                    messages.success(request, ' Registration Successful!')
                    return redirect('officials:register')
     return render(request,'officials/register.html',{})

def registeremp (request):
     if request.method == 'POST':
          if request.POST["submit"]:
               empid=request.POST["regno"]
               name=request.POST["name"]
               desig=request.POST['desig']
               gender=request.POST["type"]
               email=request.POST["email"]
               address=request.POST["address"]
               ph=request.POST['ph']
              
               
               if Officials.objects.filter(emp_id=empid).exists():
                    messages.error(request, 'Aldready Registered!')
               else :
                    acc=Officials(empid,name,desig,address,ph,email)
                    acc.save()
                    messages.success(request, ' Registration Successful!')
                    return redirect('officials:registeremp')
     return render(request,'officials/register-emp.html',{})


@csrf_exempt
def watercan(request):
    name = request.COOKIES['username_off']
    off_details = Officials.objects.get(emp_id=str(name))
    block_details = Blocks.objects.get(emp_id_id=str(name))

    if request.method == 'POST':
        if request.POST.get('submit_btn'):
            date = request.POST.get('date')
            count = request.POST.get('count')

            if WaterCan.objects.filter(block=block_details, date=date).exists():
                current = WaterCan.objects.get(block=block_details, date=date)
                current.count = count
                current.save()
            else:
                newCan = WaterCan(block=block_details, date=date, count=count)
                newCan.save()
            return redirect('officials:watercan')

        elif request.POST.get('count_btn'):
            date_hist = request.POST.get('date_hist')
            if WaterCan.objects.filter(block=block_details, date=date_hist).exists():
                dateCount = WaterCan.objects.get(block=block_details, date=date_hist).count
            else:
                dateCount = -10
            return render(request, 'officials/water-can.html', {'dateCount':dateCount})

    return render(request, 'officials/water-can.html')