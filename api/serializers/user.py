from rest_framework import serializers
from django.core import exceptions
from api.models import User
import django.contrib.auth.password_validation as password_validators 

HOUR_CHOICES = [x for x in range(7, 18)]  #[7, 17]
PERIOD_CHOICES = [0, 1, 2]

class UserSerializer(serializers.ModelSerializer):
	confirm_password = serializers.CharField(write_only=True,  style={'input_type': 'password'})
	class Meta:
		model = User
		fields = ('unique_identifier', 'is_staff', 'is_tutor', 'is_student', 'is_administrator','password', 'confirm_password',)
		read_only_fields = ('unique_identifier', 'is_staff', 'is_tutor', 'is_student', 'is_administrator',)
		extra_kwargs = {
			'password': {
				'write_only': True,
				'style': {'input_type': 'password'}
			},
		}

class ResetPasswordEmailSerializer(serializers.Serializer):
	email = serializers.EmailField()
	user_type = serializers.IntegerField()

class ResetPasswordTokenSerializer(serializers.Serializer):
	token = serializers.CharField()
	new_password = serializers.CharField()
	ui64 = serializers.CharField()

	def validate_new_password(self, value):
		try:
			password_validators.validate_password(password=value)
		except exceptions.ValidationError as e:
			raise serializers.ValidationError({"password": list(e)})
		return value

class ChangePasswordSerializer(serializers.Serializer):
	password = serializers.CharField()
	new_password = serializers.CharField()
	confirm_new_password = serializers.CharField()

	def validate_new_password(self, value):
		try:
			password_validators.validate_password(password=value)
		except exceptions.ValidationError as e:
			raise serializers.ValidationError({"password": list(e)})
		return value

	def validate(self, data):
		if data['new_password'] != data['confirm_new_password']:
			raise serializers.ValidationError({"confirm_new_password": "new password and confirm new password do not match"})
		return data

class LogoutSerializer(serializers.Serializer):
	token = serializers.CharField() 
