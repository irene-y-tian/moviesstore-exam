# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

class SecurityQuestion(models.Model):
    question = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question

class UserSecurityAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    answer_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'question')
    
    def set_answer(self, raw_answer):
        """Hash and store the security answer"""
        self.answer_hash = make_password(raw_answer.lower().strip())
    
    def check_answer(self, raw_answer):
        """Check if the provided answer matches the stored hash"""
        return check_password(raw_answer.lower().strip(), self.answer_hash)


