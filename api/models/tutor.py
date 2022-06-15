from django.db import models
from .user import User
import datetime

class Tutor(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	email = models.EmailField(max_length=255, unique=True)
	name = models.CharField(max_length=255)
	registration_number = models.TextField(max_length=9, primary_key=True)
	# completed_hours = models.IntegerField(default=0)
	major = models.CharField(max_length=4)
	is_active = models.BooleanField(default=False)
	is_accepted = models.BooleanField(default=False)

	@property
	def completed_hours(self):
		return self.tutoring_set.filter(status='CO').count()

	@property
	def weekly_completed_hours(self):
		completed_hours = self.tutoring_set.filter(status='CO')
		weekly_completed_hours = 0
		today = datetime.date.today()
		last_monday = today - datetime.timedelta(days=today.weekday())
		for tutoring in completed_hours:
			if tutoring.date >= last_monday:
				weekly_completed_hours += 1
		return weekly_completed_hours 

	@property
	def schedules(self):
		return self.schedule_set.all()

	@property
	def subjects(self):
		return self.subjecttutor_set.all()

	@property
	def tutoring(self):
		return self.tutoring_set.all()

	def delete(self, *args, **kwargs):
		super().delete(*args, **kwargs)
		if self.user:
			self.user.delete()

class Subject(models.Model):
	code = models.TextField(max_length=9, primary_key=True)
	name = models.CharField(max_length=255, null=False)
	semester = models.PositiveSmallIntegerField(null=False)

class SubjectTutor(models.Model):
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)

class Schedule(models.Model):
	tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
	period = models.PositiveSmallIntegerField(null=False)
	day_week = models.PositiveSmallIntegerField(null=False)
	hour = models.PositiveSmallIntegerField(null=False)