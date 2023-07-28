from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class createuserform(UserCreationForm):
    # iterable
    DOMAIN_CHOICES = (
        ("Python", "Python"),
        ("Hadoop/Bigdata", "Hadoop/Bigdata"),
        ("Oracle", "Oracle"),
        (".Net", ".Net"),
        ("Java", "Java")
    )
    current_domain = forms.ChoiceField(choices=DOMAIN_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['first_name',
                  'last_name',
                  'email',
                  'username',
                  'password',
                  'current_domain']
