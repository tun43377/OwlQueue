import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import QueueEntry


class QueueConsumer(WebsocketConsumer):
    group_name = "queue"

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()
        self.send_queue()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "join":
            QueueEntry.objects.create(name=data["name"], question=data["question"])
        elif data.get("action") == "next":
            entry = QueueEntry.objects.filter(helped=False).first()
            if entry:
                entry.helped = True
                entry.save()
        async_to_sync(self.channel_layer.group_send)(self.group_name, {"type": "queue.update"})

    def queue_update(self, event):
        self.send_queue()

    def send_queue(self):
        queue = [
            {"name": e.name, "question": e.question}
            for e in QueueEntry.objects.filter(helped=False)
        ]
        self.send(text_data=json.dumps({"queue": queue}))