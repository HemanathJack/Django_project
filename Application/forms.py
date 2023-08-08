from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import NumberInput
from django.forms import ModelForm
from .models import *

class change_password(PasswordChangeForm):
	old_password = forms.CharField(label='Old Password',widget=forms.PasswordInput(
		attrs={'class':'form-control mb-3','placeholder':'Old Password', 'id':'form-oldpass'}))
	new_password1 = forms.CharField(label='New password',widget=forms.PasswordInput(
		attrs={'class':'form-control mb-3','placeholder':'New Password', 'id':'form-newpass'}))
	new_password2 = forms.CharField(label='Confirm new Password',widget=forms.PasswordInput(
		attrs={'class':'form-control mb-3','placeholder':'Confirm new Password', 'id':'form-new-pass2'}))

	class Meta:
		model = User
		fields = ('old_password', 'new_password1', 'new_password2')

class update_user_profile(ModelForm):
    """
    A form that lets a user change their user details.
    """
    TEAMS_AVAILABLE = [
        ('IOT Test Automation', 'IOT Test Automation'),
        ('KCE Test Automation', 'KCE Test Automation'), ]

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Username"}))
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "First Name"}))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Last Name"}))
    email = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'email', 'id': 'input-email',
               "placeholder": "Email ID"}))
    date_of_birth = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'date'}))
    department = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Department"}))
    team = forms.ChoiceField(label='', choices=TEAMS_AVAILABLE, widget=forms.Select(
        attrs={'class': 'form-control form-control-alternative', 'id': 'teams_dropdown'}))
    designation = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Designation"}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'date_of_birth', 'department', 'team', 'designation')


class comp_update_auth(ModelForm):
    """
        A class to represent Update Competency status.
    """
    UPDATE_COMP = [
        ('Enable', 'Enable'),
        ('Disable', 'Disable')]

    state = forms.ChoiceField(widget=forms.Select(
        attrs={'class': 'form-control form-control-alternative', 'id': 'competency_update_dropdown'}), label='',
                              choices=UPDATE_COMP)

    class Meta:
        model = update_competency
        fields = ('state',)


class ModulesForm(ModelForm):
    """
       A class to represent a module form.
    """

    class Meta:
        model = module
        fields = ('module_name',)

    module_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Add Module"}))


class ProductsForm(ModelForm):
    """
        A class to represent a product form.
    """

    class Meta:
        model = product
        fields = ('product_name', 'module',)

    product_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Add Product"}))
    module = forms.ModelChoiceField(widget=forms.Select(
        attrs={'class': 'form-control form-control-alternative', 'id': 'id_module'}), label='Select module',
        queryset=module.objects.all())

class TrainingForm(ModelForm):
    """
        A class to represent a training form.

    """
    user = User.objects.exclude(username='admin')
    class Meta:
        model = training
        fields = ('training_name', 'training_description', 'training_date', 'training_duration', 'training_location',
                  'training_link', 'training_members',)
    training_name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Training Name"}))
    training_description = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Training Description"}))
    training_date = forms.DateTimeField(widget=NumberInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'datetime-local'}))
    training_duration = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'number', "placeholder": "Training Duration"}))
    training_location = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'text', "placeholder": "Training Location"}))
    training_link = forms.URLField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'url', "placeholder": "Training link"}))
    training_members = forms.ModelMultipleChoiceField(
        widget=forms.SelectMultiple(choices=user,
                                    attrs={'class': 'form-control form-control-alternative', 'type': 'url',
                                           "placeholder": "Training members"}), label='Training Members', queryset=user)

class CommentForm(forms.ModelForm):
    """
         A class to represent a comment form.

     """
    comments = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-alternative',
            'type': 'text',
            'placeholder': 'comment',
        }),
        required=False,
    )
    case_id = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-alternative', 'type': 'number', "placeholder": " case_id"}))

    class Meta:
        model = comments_field
        fields = ('comments', 'case_id')

