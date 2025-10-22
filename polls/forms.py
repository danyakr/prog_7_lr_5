from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .models import Question, Choice


class QuestionForm(forms.ModelForm):
    """Форма для создания/редактирования вопроса"""
    choices = forms.CharField(
        label='Question Choices',
        widget=forms.Textarea(attrs={'rows': 7}),
        help_text='Enter the answer options, separating each option with a new line.'
    )

    class Meta:
        model = Question
        fields = ['question_text', 'choices']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            choices = '\n'.join(
                self.instance.choice_set.values_list('choice_text', flat=True)
            )
            self.initial['choices'] = choices

    def clean_choices(self):
        choices = self.cleaned_data.get('choices')
        if choices:
            choices_list = [
                choice.strip()
                for choice in choices.split('\n')
                if choice.strip()
            ]

            if len(choices_list) < 2:
                raise forms.ValidationError('Enter at least two answer options.')

            return choices_list
        return []

    def save(self, commit=True):
        question_instance = super().save(commit=False)
        if not question_instance.pub_date:
            question_instance.pub_date = timezone.now()
        question_instance.save()

        # Удалить старые варианты
        Choice.objects.filter(question=question_instance).delete()

        # Создать новые варианты
        choices = self.cleaned_data.get('choices')
        if choices:
            for choice_text in choices:
                Choice.objects.create(
                    question=question_instance,
                    choice_text=choice_text
                )

        return question_instance


class NewUserForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, request, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False  # Неактивен до подтверждения email
        user.is_superuser = False
        user.is_staff = False
        if commit:
            user.save()
            self.send_verification_email(user, request)
        return user

    def send_verification_email(self, user, request):
        """Отправка email для активации аккаунта"""
        current_site = get_current_site(request)
        mail_subject = 'Activate your Polls account'
        message = render_to_string(
            'polls/verification_email.html',
            {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
        )
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.content_subtype = "html"
        email.send()