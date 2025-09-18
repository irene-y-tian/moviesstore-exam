# accounts/forms.py (updated)
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.models import User
from .models import SecurityQuestion, UserSecurityAnswer

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )

class SecurityQuestionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = SecurityQuestion.objects.filter(is_active=True)
        
        for i, question in enumerate(questions[:3], 1):
            self.fields[f'question_{question.id}'] = forms.CharField(
                label=question.question,
                max_length=200,
                required=True,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Your answer'
                })
            )

class ForgotPasswordUsernameForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )

class SecurityAnswerForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        user_answers = UserSecurityAnswer.objects.filter(user=user).select_related('question')
        
        for answer in user_answers:
            self.fields[f'answer_{answer.question.id}'] = forms.CharField(
                label=answer.question.question,
                max_length=200,
                required=True,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'placeholder': 'Your answer'
                })
            )
    
    def clean(self):
        cleaned_data = super().clean()
        user_answers = UserSecurityAnswer.objects.filter(user=self.user)
        
        correct_answers = 0
        for answer in user_answers:
            field_name = f'answer_{answer.question.id}'
            user_input = cleaned_data.get(field_name, '').strip()
            if user_input and answer.check_answer(user_input):
                correct_answers += 1
        
        if correct_answers < len(user_answers):
            raise forms.ValidationError("One or more security answers are incorrect.")
        
        return cleaned_data

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['new_password1', 'new_password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )

