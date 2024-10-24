from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):

    name = models.CharField(max_length=100)  # Name of the chat room

    def __str__(self):
        return f"Chat Room: {self.name}"

class ChatRoomUser(models.Model):
    role_options = [
        ('buyer', "Buyer"),
        ('seller', "Seller")
    ]
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)  # Field to check if the user is approved
    role = models.CharField(max_length=25, choices=role_options, default="Buyer")

    def __str__(self):
        return f"{self.user.username} in {self.room.name} - Approved: {self.is_approved}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    machine_sender = models.CharField(max_length=255, null=False, blank=True)  # New field for machine messages
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content} at {self.timestamp}"
