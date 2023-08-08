from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date



TEAMS_AVAILABLE = [
    ('Not Available', 'Not Available'),
    ('IOT Test Automation', 'IOT Test Automation'),
    ('KCE Test Automation', 'KCE Test Automation'),]


UPDATE_COMP = [
    ('Enable', 'Enable'),
    ('Disable', 'Disable')]

class User(AbstractUser):
    # username will be kone_id
    """
        A class to represent a user.
    """

    first_name = models.CharField('First Name', max_length=25)
    last_name = models.CharField('Last Name', max_length=25)
    designation = models.CharField('Destination', max_length=100)
    team = models.CharField('Team Name', max_length=25, choices=TEAMS_AVAILABLE, default='Not Available')
    department = models.CharField('Department', max_length=50)
    date_of_birth = models.DateField(default=date(1990,1,1), auto_now_add=False, null=False)
    is_admin = models.BooleanField('Admin', default=False)
    is_user = models.BooleanField('User', default=True)
    is_manager = models.BooleanField('Manager', default=False)

    def __str__(self):
        return self.username

class module(models.Model):
    """
        A class to represent a module.
    """
    module_name = models.CharField('Module Name', max_length=50)

    def __str__(self):
        return str(self.module_name)

class product(models.Model):
    """
        A class to represent a product.
    """
    product_name = models.CharField('Product Name', max_length=50)
    module = models.ForeignKey(module, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.product_name)

class update_competency(models.Model):
    """
        A class to represent Update Competency status.
    """
    state = models.CharField('state', max_length=8, choices=UPDATE_COMP, default='Disable')

    def __str__(self):
        return str(self.state)

class training(models.Model):
    """
        Trainings model of competency
    """
    training_name = models.CharField('Training Name', max_length=50, blank=False, null=False)
    training_description = models.TextField('Training Description', max_length=500)
    training_date = models.DateTimeField('Training Date & Time', blank=False, null=False)
    training_duration = models.IntegerField('Training Duration', blank=False, null=False, help_text="Enter number in hours")
    training_location = models.CharField('Training Location', max_length=50, blank=True, null=True)
    training_link = models.URLField('Training Link')
    training_members = models.ManyToManyField(User)
    def __str__(self):
        return str(self.training_name)

class comments_field(models.Model):
    """
       model for comments field in test cases
    """
    case_id = models.CharField(max_length=20)
    comments = models.TextField('add comments', max_length=500)

    def __str__(self):
        return self.case_id


