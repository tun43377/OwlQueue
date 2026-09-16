from django.db import models


class QueueEntry(models.Model):
    name = models.CharField(max_length=100)
    question = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    helped = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name}: {self.question}"