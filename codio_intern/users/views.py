from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse   
from django.contrib.auth import login, authenticate,logout   
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .token import account_activation_token  
from django.core.mail import EmailMessage 
from django.contrib.auth import get_user_model
from .models import Room, Topic, Message,User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.db.models import Q
import json
import csv

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('codio-home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('codio-home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'users/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('codio-home')



def register(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
           # form.save()
           # username = form.cleaned_data.get('username')
            #messages.success(request, f'Your account is created you can login Now!')
            #return redirect('login')
            # save form in the memory not in database  
            user = form.save(commit=False)  
            user.is_active = False  
            user.save()  
            # to get the domain of the current site  
            current_site = get_current_site(request)  
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('acc_active_email.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),  
            })  
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                        mail_subject, message, to=[to_email]  
            )  
            email.send()  
            return HttpResponse('Please confirm your email address to complete the registration')  
        else:
            messages.error(request, 'Please enter all the details correctly')
    form = MyUserCreationForm()
    return render(request, 'users/register.html',{'form':form})

def activate(request, uidb64, token):  
    User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        #return render(request, 'users/login.html')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')  
    else:  
        return HttpResponse('Activation link is invalid!')  

@login_required
def profile(request):
    return render(request, 'users/profile.html')




def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3]

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'users/home.html', context)



def about(request):
    return render(request,'users/about.html')

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'users/profile.html', context)




def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    current_user = request.user
    
    # checking whether the current user is registered or not
    is_registered = room.participants.filter(id = current_user.id).exists()
   
    recipient_emails = ','.join([user2.email for user2 in participants])

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants,'is_registered': is_registered,
               'recipient_emails': recipient_emails}
    
    return render(request, 'users/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('codio-home')

    context = {'form': form, 'topics': topics}
    return render(request, 'users/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'users/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('codio-home')
    return render(request, 'users/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('codio-home')
    return render(request, 'users/delete.html', {'obj': message})



def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'users/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'users/activity.html', {'room_messages': room_messages})

# to add the student into the event if he/she registers
def update_room_follow(request):
    if request.method == 'PUT':
        # Extract the data from the request
        data = json.loads(request.body)
        action = data.get('action')
        user_id = data.get('user_id')
        roomid = data.get('roomid')

        # Perform the necessary actions based on the data
        # For example, update the room's follow status for the user
        instance = Room.objects.get(id=roomid)
            # Add the user as a participant to the course
        instance.participants.add(user_id)
        instance.save()
        # Return a JSON response indicating the success or failure of the update
        return JsonResponse({'success': True})

    # If the request method is not PUT, return an error response
    return JsonResponse({'error': 'Invalid request method'})


# downloading the student data

def download_users(request,pk):
    room = Room.objects.get(id=pk)
    participants = room.participants.all()

    # Create the HttpResponse object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_data.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write the CSV headers
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name'])

    # Write each user's data to the CSV file
    for user in participants:
        writer.writerow([user.username, user.email, user.first_name, user.last_name])

    return response
