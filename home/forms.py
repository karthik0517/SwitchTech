from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.shortcuts import render,redirect
from django.http import request, HttpResponse,JsonResponse,response



class createuserform(UserCreationForm):
    # iterable
    DOMAIN_CHOICES = (
        ("Python", "Python"),
        ("Hadoop/Bigdata", "Hadoop/Bigdata"),
        ("Oracle", "Oracle"),
        (".Net", ".Net"),
        ("Java", "Java")
    )
    current_domain = forms.ChoiceField(choices=DOMAIN_CHOICES,required=True)
    class Meta:
        model = User
        fields = ['first_name','last_name','email','username', 'password','current_domain']

    # def save(self, commit=True):
    #     user = super(createuserform, self).save(commit=False)
    #     user.email = self.cleaned_data['email']
    #     if commit:
    #         user.save()
    #     return user


# class QuizForm(forms.Form):
#     def __init__(self, data, questions, *args, **kwargs):
#         self.questions = questions
#         for question in questions:
#             field_name = "question_%d" % question.pk
#             choices = []
#             for answer in question.answer_set().all():
#                 choices.append((answer.pk, answer.answer,))
#             ## May need to pass some initial data, etc:
#             field = forms.ChoiceField(label=question.question, required=True,
#                                       choices=choices, widget=forms.RadioSelect)
#         return super(QuizForm, self).__init__(data, *args, **kwargs)
#
#     def save(self):
#         pass
#         ## Loop back through the question/answer fields and manually
#         ## update the Attempt instance before returning it.

# class addQuestionform(ModelForm):
#     class Meta:
#         model = QuesModel
#         fields = "__all__"
