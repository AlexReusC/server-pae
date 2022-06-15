from django.forms import ValidationError
from rest_framework import serializers
from api.models import User, Administrator 
from . import UserSerializer
from django.core.validators import validate_email

from api.constants import NAME_RE

import re

class AdministratorSerializer(serializers.ModelSerializer):
	user = UserSerializer(required=True)

	class Meta:
		model = Administrator
		fields = ('user', 'registration_number', 'email', 'name')

	def create(self, validated_data):
		unique_identifier = 'administrator' + validated_data['registration_number']

		user = User.objects.create_user(unique_identifier, validated_data['user']['password'])
		user.is_administrator = True
		if not Administrator.objects.filter().exists():
			user.is_staff = True
		user.save()
		administrator = Administrator.objects.create(user=user, email=validated_data['email'], name=validated_data['name'], registration_number=validated_data['registration_number'])
		return administrator

	def validate_name(self, value):
		normalized_name = value.strip()
		if not re.search(NAME_RE, normalized_name):
			raise serializers.ValidationError("Name must be valid")
		return normalized_name

	def validate_email(self, value):
		normalized_email = value.lower()
		try:
			validate_email(normalized_email)
		except ValidationError as e:
			raise serializers.ValidationError({"email": list(e)})
		return normalized_email
