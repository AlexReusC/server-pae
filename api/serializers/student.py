from rest_framework import serializers
from django.core import exceptions
from api.models import User, Student
from django.core.mail import send_mail
import django.contrib.auth.password_validation as password_validators 
from . import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from api.constants import NAME_RE, EMAIL_RE, MAJOR_RE

import re
import datetime
import environ

env = environ.Env()
environ.Env.read_env()

class StudentRegisterSerializer(serializers.ModelSerializer):
	user = UserSerializer(required=True)

	class Meta:
		model = Student 
		fields = ('user', 'registration_number', 'email', 'name', 'major', 'is_active')
		read_only_fields = ('registration_number', 'is_active')



	def create(self, validated_data):
		def formatEmail(url):
			return f"<html style=''><html lang='es'><head><meta charset='UTF-8'><link rel='preconnect' href='https://fonts.googleapis.com'><link rel='preconnect' href='https://fonts.gstatic.com' crossorigin><link href='https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap' rel='stylesheet'></head><body style='margin: 0;padding: 0;font-family:Montserrat, sans-serif;box-sizing:border-box; justify-content:center;align-items:center; background:#8f91a2;'><div class='oxxo-pay' style='height: auto;max-width:550px;background: #fff;padding: 50px 50px 10px 50px;margin: 0 auto;'><div class='oxxo-header' style='background-image: url('logo.ico');background-repeat:no-repeat;height:60px;background-position:center;background-size:contain;'></div><h4 style='text-align:center;font-weight:300;font-size:20px; padding-bottom:20px;border-bottom: 2px solid rgba(74, 74, 74, 0.25);'>PAE</h4><h1 style='font-size:30px;text-align:center;padding:30px;color:#545b65;font-weight:600;'>Activación de cuenta </h1><div class='box' style='background:rgba(211,192,179,.4);margin-top:30px;padding:35px;justify-content: space-between;flex-direction:column;align-items:center;font-size: 14px;color:#545b65;'><p style='text-align:center;'>Su cuenta acaba de ser registrada como Estudiante de PAE (Programa Asesor Estudiante). Da click en el siguiente enlace para activar tu cuenta.</p> </div><div class='summary' style='width:100%;margin-top:45px;margin-bottom:45px;justify-content:center;align-items:center;text-align:center;flex-direction:column;'><div class='summary_header' style='margin-bottom:20px;height:auto;flex-direction:column;justify-content:center;align-items:center;text-align:center;'><h3 style='font-size:16px;margin-bottom:8px;'><a href='{url}'>Haz click en este enlace</a></h3></div></div><footer><p style='margin-bottom:4px;font-size:14px;text-align:center'> © PAE 2021. Desarrollado por Hacket</p></footer></div></body></html>"
		registration_number = validated_data['email'][:9]
		unique_identifier = 'student' + registration_number

		user = User.objects.create_user(unique_identifier, validated_data['user']['password'])
		user.is_student = True
		user.save()
		student = Student.objects.create(user=user, registration_number = registration_number, email=validated_data['email'], major=validated_data['major'], name=validated_data['name'])

		#create a token for activating the account
		token = RefreshToken.for_user(user)
		token.set_exp(lifetime=datetime.timedelta(days=10))
		access_token = token.access_token
		print("token", access_token)
		relative_link = "activate-account/?" + "token=" + str(access_token)
		url = env('FRONTEND_URL') + relative_link
		send_mail("Activa tu cuenta", "Activar cuenta", None, [validated_data["email"]], html_message=formatEmail(url))

		return student 

	def validate_name(self, value):
		normalized_name = value.strip()
		if not re.search(NAME_RE, normalized_name):
			raise serializers.ValidationError("Name must be valid")
		return normalized_name

	def validate_email(self, value):
		normalized_email = value.lower()
		if not re.search(EMAIL_RE, normalized_email):
			raise serializers.ValidationError("Must be a valid tec email")
		return normalized_email

	def validate_major(self, value):
		normalized_major = value.upper()
		if not re.search(MAJOR_RE, normalized_major):
			raise serializers.ValidationError("Must contain only letters")
		if len(normalized_major) < 2:
			raise serializers.ValidationError("Must be longer than 2 letters")
		return normalized_major
		
	def validate(self, data):
		password = data.get('user').get('password')
		if password != data.get('user').get('confirm_password'):
			raise serializers.ValidationError({"password": "passwords do not match"})
		try:
			password_validators.validate_password(password=password)
		except exceptions.ValidationError as e:
			raise serializers.ValidationError({"password": list(e)})
		return data 