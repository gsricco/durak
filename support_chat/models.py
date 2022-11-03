from django.contrib.auth.models import User
from django.db import models


class Message(models.Model):
    """Модель сообщений чата поддержки"""
    user_posted = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_send')
    user_received = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_received')
    message = models.TextField(blank=True, null=True)
    file_message = models.ImageField(upload_to='support_chat/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-date',)
