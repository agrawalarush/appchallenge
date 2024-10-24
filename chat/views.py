from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatRoom, Message
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned


class RoomRedirectForm(forms.Form):
    room_id = forms.IntegerField(label="Room ID", required=True)

    def clean_room_id(self):
        room_id = self.cleaned_data.get('room_id')
        # Ensure the room exists
        if not ChatRoom.objects.filter(id=room_id).exists():
            raise forms.ValidationError("Room with this ID does not exist.")
        return room_id


# View to render the chat room
def chat_room(request, room_name):
    if request.user.is_authenticated:
        room = get_object_or_404(ChatRoom, name=room_name)

        # Check if the user is approved for the room
        try:
            ChatRoomUser.objects.get(room=room, user=request.user, is_approved=True)
        except ChatRoomUser.DoesNotExist:
            messages.warning(request, "You do not have access to this chat.")
            return redirect('/products')  # Redirect if the chat room does not exist
        except MultipleObjectsReturned:
            messages.warning(request, "You cannnot chat with yourself and checkout your own product!")
            room_to_delete = ChatRoom.objects.filter(name=room_name)
            room_to_delete.delete()
            return redirect("/products")

        # Fetch messages for the room
        content = Message.objects.filter(room=room).order_by('timestamp')
        user = ChatRoomUser.objects.filter(room=room, is_approved=True, role="Buyer")
        # Render the chat room template
        return render(request, 'chat/chat.html', {'room': room, 'text': content, 'buying_user': user})
    else:
        messages.warning(request, "Please log in to view chat rooms!")
        return redirect("/user/sign_in/")



# View to handle sending messages in the chat room
@login_required
@csrf_exempt
def send_message(request, room_name):
    if request.method == 'POST':
        content = request.POST.get('content')
        room = ChatRoom.objects.get(name=room_name)
        Message.objects.create(room=room, sender=request.user, content=content)
    return redirect(f'/chat/room/{room_name}/')


# View to handle redirection to a chat room based on the form input
def what_room(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = RoomRedirectForm(request.POST)  # Bind form to POST data
            if form.is_valid():
                room_id = form.cleaned_data['room_id']  # Get the room id
                try:
                    room = ChatRoom.objects.get(id=room_id)
                except ChatRoom.DoesNotExist:
                    messages.warning(request, "This chat room does not exist!")
                    return redirect("/chat/room/")
                return redirect(f'/chat/room/{room.name}/')  # Redirect using room name
        else:
            form = RoomRedirectForm()  # Unbound form for GET requests

        approved_rooms_for_user = ChatRoom.objects.filter(chatroomuser__user=request.user, chatroomuser__is_approved=True)
        return render(request, 'chat/redirect.html', {"form": form, "allowed_rooms": approved_rooms_for_user})
    else:
        messages.warning(request, "Please log in to view chat rooms!")
        return redirect("/user/sign_in/")


def approve_user(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    user = get_object_or_404(User, username= request.user.username)
    
    # Approve the user for the room
    chat_room_user, created = ChatRoomUser.objects.get_or_create(room=room, user=user)
    chat_room_user.is_approved = True
    chat_room_user.save()
    
    return redirect('/chat/room/')  # Redirect after approval

def remove_user(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    user = get_object_or_404(User, username= request.user.username)
    
    # Approve the user for the room
    chat_room_user, created = ChatRoomUser.objects.get_or_404(room=room, user=user)
    chat_room_user.is_approved = False
    chat_room_user.save()
    
    return redirect('/chat/room/')  # Redirect after removal

def what(request):
    rooms = ChatRoom.objects.all()
    for room in rooms:
        approved_users = ChatRoomUser.objects.filter(room= room, is_approved=True)
        print(f"{room.name} Allowed users: {approved_users} ID: {room.id}\n")

def delete_rooms(request):
    room = ChatRoom.objects.all()
    room.delete()
    user_instance = ChatRoomUser.objects.all()
    user_instance.delete()
    messages = Message.objects.all()
    messages.delete()