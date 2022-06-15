from rest_framework import serializers
from api.models import Tutoring, Schedule, Tutor, Subject, Period

from api.constants import HOUR_CHOICES, END_DATE_FIELDS, START_DATE_FIELDS 

from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode


class TutorTutoringSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutor
		fields = ('name', 'registration_number')

class SubjectTutoringSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subject
		fields = ('__all__')

class ParamsAvailableTutoringSerializer(serializers.Serializer):
	subject = serializers.CharField()
	initial_date_serializer = serializers.DateField()
	final_date_serializer = serializers.DateField()

class AvailableTutoring(object):
	def __init__(self, hour, period, tutor, isOnline):
		self.hour = hour
		self.period = period
		#encode registration number of tutor to avoid identification
		# self.tutor = urlsafe_base64_encode(smart_bytes(tutor.registration_number))
		self.tutor = tutor.registration_number
		self.isOnline = isOnline

class AvailableTutoringSerializer(serializers.Serializer):
		hour = serializers.IntegerField()
		period = serializers.IntegerField()
		tutor = serializers.CharField()
		isOnline = serializers.BooleanField()

class AvailableTutoringSerializerList(serializers.Serializer):
	date = serializers.DateField()
	tutorings = AvailableTutoringSerializer(many=True)

class TutoringSerializer(serializers.ModelSerializer):
	tutor = TutorTutoringSerializer(read_only=True)
	tutor_id = serializers.PrimaryKeyRelatedField(write_only=True, source='tutor', queryset=Tutor.objects.all())
	subject = SubjectTutoringSerializer(read_only=True)
	subject_id = serializers.PrimaryKeyRelatedField(write_only=True, source='subject', queryset=Subject.objects.all())
	class Meta:
		model = Tutoring
		exclude = ()
		read_only_fields = ('student', 'status')
		depth = 1

	def create(self, validated_data):
		student = self.context['request'].user.role_account
		return Tutoring.objects.create(student = student, **validated_data)

	def validate_tutor_id(self, value):
		if value is None:
			raise serializers.ValidationError({"tutor": "tutor cannot be null"})
		return value

	def validate_subject(self, value):
		if value is None:
			raise serializers.ValidationError({"subject": "subjct cannot be null"})
		return value
	
	def validate_hour(self, value):	
		if value not in HOUR_CHOICES:
			raise serializers.ValidationError({"hour": "hour must be between 7 and 17"})
		return value

	def validate(self, data):
		if data["doubt"] is None and data["file"] is None:
			raise serializers.ValidationError({"doubt": "there must a doubt or a file"})
		return data

class ChangeTutoringLocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutoring
		fields = ('is_online', 'place',)

class ParamsAlternateTutorSerializer(serializers.Serializer):
	hour = serializers.IntegerField()
	date = serializers.DateField()
	subject = serializers.CharField()

class AlternateTutorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutor
		fields = ('registration_number', 'name', 'completed_hours', 'major',)

class ChangeTutorSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutoring
		fields = ('tutor',)
	
	def validate_tutor(self, value):
		tutoring = self.instance
		tutor = value

		hour = tutoring.hour
		date = tutoring.date
		day_week = date.weekday()

		period = Period.objects.filter().first()
		current_period = -1
		for i in range(3):
				start_date, end_date = START_DATE_FIELDS[i], END_DATE_FIELDS[i]
				initial_date, final_date = period.__dict__[start_date], period.__dict__[end_date]
				if date >= initial_date and date <= final_date:
					current_period = i
					break
		if current_period == -1:
				raise serializers.ValidationError({"period": "period does not exist"}) 

		if not Schedule.objects.filter(tutor=tutor.registration_number, hour=hour, period=current_period, day_week=day_week).exists():
				raise serializers.ValidationError({"schedule": "tutor does not have that schedule"})

		#TODO: check that is not cancelled
		if Tutoring.objects.filter(tutor=tutor.registration_number, hour=hour, date=date).exists():
			raise serializers.ValidationError({"tutorign": "tutor already has a tutoring at that time"})

		return tutor 