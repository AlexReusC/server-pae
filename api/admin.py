from django.contrib import admin

from . import models
# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Tutor)
admin.site.register(models.Student)
admin.site.register(models.Schedule)
admin.site.register(models.Subject)
admin.site.register(models.Period)
admin.site.register(models.Tutoring)
admin.site.register(models.Administrator)
admin.site.register(models.Question)
admin.site.register(models.QuestionPoll)
admin.site.register(models.Poll)

