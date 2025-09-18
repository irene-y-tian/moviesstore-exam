# accounts/views.py (updated)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from .forms import (
    CustomUserCreationForm, CustomErrorList, SecurityQuestionsForm,
    ForgotPasswordUsernameForm, SecurityAnswerForm, CustomSetPasswordForm
)
from .models import SecurityQuestion, UserSecurityAnswer

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

@login_required
def settings(request):
    template_data = {}
    template_data['title'] = 'Account Settings'
    template_data['has_security_questions'] = UserSecurityAnswer.objects.filter(user=request.user).exists()
    return render(request, 'accounts/settings.html', {'template_data': template_data})

@login_required
def setup_security_questions(request):
    # Check if user already has security questions set up
    existing_answers = UserSecurityAnswer.objects.filter(user=request.user)
    
    template_data = {}
    template_data['title'] = 'Security Questions'
    template_data['has_existing'] = existing_answers.exists()
    
    if request.method == 'GET':
        template_data['form'] = SecurityQuestionsForm()
        return render(request, 'accounts/setup_security.html', {'template_data': template_data})
    
    elif request.method == 'POST':
        form = SecurityQuestionsForm(request.POST)
        if form.is_valid():
            # Delete existing answers if updating
            existing_answers.delete()
            
            # Save new security answers
            for field_name, answer in form.cleaned_data.items():
                if field_name.startswith('question_'):
                    question_id = field_name.split('_')[1]
                    question = SecurityQuestion.objects.get(id=question_id)
                    
                    user_answer = UserSecurityAnswer(user=request.user, question=question)
                    user_answer.set_answer(answer)
                    user_answer.save()
            
            messages.success(request, 'Security questions updated successfully!')
            return redirect('accounts.settings')
        else:
            template_data['form'] = form
            return render(request, 'accounts/setup_security.html', {'template_data': template_data})

def forgot_password(request):
    template_data = {}
    template_data['title'] = 'Forgot Password'
    
    if request.method == 'GET':
        template_data['form'] = ForgotPasswordUsernameForm()
        return render(request, 'accounts/forgot_password.html', {'template_data': template_data})
    
    elif request.method == 'POST':
        form = ForgotPasswordUsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                # Check if user has security questions set up
                if UserSecurityAnswer.objects.filter(user=user).exists():
                    return redirect('accounts.verify_security', user_id=user.id)
                else:
                    messages.error(request, 'This user has not set up security questions.')
                    return render(request, 'accounts/forgot_password.html', {'template_data': template_data})
            except User.DoesNotExist:
                messages.error(request, 'Username not found.')
                return render(request, 'accounts/forgot_password.html', {'template_data': template_data})
        else:
            template_data['form'] = form
            return render(request, 'accounts/forgot_password.html', {'template_data': template_data})

def verify_security_answers(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Check if user has security questions
    if not UserSecurityAnswer.objects.filter(user=user).exists():
        raise Http404("Security questions not found")
    
    template_data = {}
    template_data['title'] = 'Answer Security Questions'
    template_data['username'] = user.username
    
    if request.method == 'GET':
        template_data['form'] = SecurityAnswerForm(user=user)
        return render(request, 'accounts/verify_security.html', {'template_data': template_data})
    
    elif request.method == 'POST':
        form = SecurityAnswerForm(user=user, data=request.POST)
        if form.is_valid():
            # Store user ID in session for password reset
            request.session['reset_user_id'] = user.id
            return redirect('accounts.reset_password')
        else:
            template_data['form'] = form
            return render(request, 'accounts/verify_security.html', {'template_data': template_data})

def reset_password(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please start the password recovery process again.')
        return redirect('accounts.forgot_password')
    
    user = get_object_or_404(User, id=user_id)
    
    template_data = {}
    template_data['title'] = 'Reset Password'
    template_data['username'] = user.username
    
    if request.method == 'GET':
        template_data['form'] = CustomSetPasswordForm(user=user)
        return render(request, 'accounts/reset_password.html', {'template_data': template_data})
    
    elif request.method == 'POST':
        form = CustomSetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            # Clear session
            del request.session['reset_user_id']
            messages.success(request, 'Password reset successfully! You can now log in with your new password.')
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/reset_password.html', {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html', {'template_data': template_data})
