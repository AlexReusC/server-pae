from django.db import models
from .tutor import Tutor, Subject
from .student import Student

from api.utils import upload_to

class Tutoring(models.Model):

	class StatusTutoring(models.TextChoices):
		PENDING = 'PE', 'Pending'
		APPROVED = 'AP', 'Approved'
		COMPLETED = 'CO', 'Completed'
		CANCELED = 'CA', 'Canceled'
		

	tutor = models.ForeignKey(Tutor, null=True, on_delete=models.SET_NULL)
	student = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL)
	subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL)
	date = models.DateField()
	hour = models.PositiveIntegerField()
	status = models.CharField(max_length=2, choices=StatusTutoring.choices, default=StatusTutoring.PENDING)
	is_online = models.BooleanField()
	place = models.CharField(max_length=55)
	topic = models.CharField(max_length=255)
	doubt = models.TextField(null=True)
	file = models.ImageField('images', upload_to=upload_to, null=True)
	has_feeback = models.BooleanField(default=False)

class Period(models.Model):
    beginning_first_period = models.DateField()
    ending_first_period = models.DateField()
    beginning_second_period = models.DateField()
    ending_second_period = models.DateField()
    beginning_third_period = models.DateField()
    ending_third_period = models.DateField()