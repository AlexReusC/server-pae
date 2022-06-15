from django.db import models
from .tutoring import Tutoring

CHOICES = [(i,i) for i in range(1, 5)]

class Poll(models.Model):
	tutoring = models.OneToOneField(Tutoring, on_delete=models.CASCADE)
	comment = models.TextField()

	@property
	def question_polls(self):
		return self.questionpoll_set.all()

	@property
	def tutor(self):
		return self.tutoring.tutor

class Question(models.Model):
	body = models.TextField()

class QuestionPoll(models.Model):
	poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, null=True, on_delete=models.CASCADE)
	result = models.IntegerField(choices=CHOICES)


