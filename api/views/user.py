from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny 
from api.models import Student, Tutor, User, Administrator
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from api.serializers import LogoutSerializer, ResetPasswordEmailSerializer, ResetPasswordTokenSerializer, ChangePasswordSerializer

import environ

env = environ.Env()
environ.Env.read_env()

class Login(ObtainAuthToken):
	permission_classes = (AllowAny,)
	def post(self, request):
		login_serializer = self.serializer_class(data=request.data, context = {'request': request})
		if login_serializer.is_valid():
			user = login_serializer.validated_data['user']
			if user.is_tutor:
				if not user.role_account.is_active:
					return Response({"message": "you need to activate your account"}, status=status.HTTP_401_UNAUTHORIZED)
				if not user.role_account.is_accepted:
					return Response({"message": "your account has not been activated by the administratos"}, status=status.HTTP_401_UNAUTHORIZED)
			if user.is_student and not user.role_account.is_active:
				return Response({"message": "you need to activate your account"})
			token, _ = Token.objects.get_or_create(user = user)
			return Response({
				'token': token.key,
				'user': user.role_account.name,
				'message': "Successful login" 
			}, status=status.HTTP_201_CREATED)
		return Response({'message': 'Username or password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

class Logout(APIView):
	permission_classes = (AllowAny,)
	serializer_class = LogoutSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			token = serializer.validated_data.get('token')
			if not Token.objects.filter(key = token).exists():
				return Response({"token": "No such token"}, status=status.HTTP_400_BAD_REQUEST)
			token = Token.objects.get(key = token)
			token.delete()
			return Response({"token": "Token successfully deleted"}, status=status.HTTP_200_OK)

class ResetPasswordEmail(APIView):
	permission_classes = (AllowAny,)
	serializer_class = ResetPasswordEmailSerializer

	def post(self, request):
		def formatEmail(link):
			return f"<html style=''><html lang='es'><head><meta charset='UTF-8'><link rel='preconnect' href='https://fonts.googleapis.com'><link rel='preconnect' href='https://fonts.gstatic.com' crossorigin><link href='https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap' rel='stylesheet'></head><body style='margin: 0;padding: 0;font-family:Montserrat, sans-serif;box-sizing:border-box; justify-content:center;align-items:center; background:#8f91a2;'><div class='oxxo-pay' style='height: auto;max-width:550px;background: #fff;padding: 50px 50px 10px 50px;margin: 0 auto;'><div class='oxxo-header' style='background-image: url('logo.ico');background-repeat:no-repeat;height:60px;background-position:center;background-size:contain;'></div><h4 style='text-align:center;font-weight:300;font-size:20px; padding-bottom:20px;border-bottom: 2px solid rgba(74, 74, 74, 0.25);'>PAE</h4><h1 style='font-size:30px;text-align:center;padding:30px;color:#545b65;font-weight:600;'>Cambio de contraseña </h1><div class='box' style='background:rgba(211,192,179,.4);margin-top:30px;padding:35px;justify-content: space-between;flex-direction:column;align-items:center;font-size: 14px;color:#545b65;'><h3 style='color:#1f1f1f;margin-bottom:15px;text-transform:uppercase;'>Link para reestablecer tu contraseña</h3><p style='text-align:center;'>Hola, da click en el siguiente link para reestablecer tu contraseña.</p> </div><div class='summary' style='width:100%;margin-top:45px;margin-bottom:45px;justify-content:center;align-items:center;text-align:center;flex-direction:column;'><div class='summary_header' style='margin-bottom:20px;height:auto;flex-direction:column;justify-content:center;align-items:center;text-align:center;'><h3 style='font-size:16px;margin-bottom:8px;'><a href={link}>Haz click en este enlace</a></h3></div></div><footer><p style='margin-bottom:4px;font-size:14px;text-align:center'> © PAE 2021. Desarrollado por Hacket</p></footer></div></body></html>"
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			email = serializer.validated_data.get('email')
			user_type = serializer.validated_data.get('user_type')
			user = None
			if user_type == 0: #Student
				if not Student.objects.filter(email=email).exists():
					return Response({"email": 'There is no student with such email'}, status=status.HTTP_400_BAD_REQUEST)
				user = Student.objects.get(email=email).user
			elif user_type == 1: #Tutor
				if not Tutor.objects.filter(email=email).exists():
					return Response({"email": 'There is no tutor with such email'}, status=status.HTTP_400_BAD_REQUEST)
				user = Tutor.objects.get(email=email).user
			elif user_type == 2:
				if not Administrator.objects.filter(email=email).exists():
					return Response({"email": 'There is no administrator with such email'}, status=status.HTTP_400_BAD_REQUEST)
				user = Administrator.objects.get(email=email).user
			else:
				return Response({"user_type": "No such user type"}, status=status.HTTP_400_BAD_REQUEST)

			ui64 = urlsafe_base64_encode(smart_bytes(user.unique_identifier))
			token = PasswordResetTokenGenerator().make_token(user)
			relative_link = "reset-password/?" + "uid=" + ui64 + "&token=" + token
			url = env('FRONTEND_URL') + relative_link
			# print(token, ui64, url)
			send_mail('Reestablecer contraseña', "Cambio de contraseña", None, [email], html_message=formatEmail(url))
			return Response({"message": "An email has been sent"}, status=status.HTTP_201_CREATED)


class ResetPasswordToken(APIView):
	permission_classes = (AllowAny,)
	serializer_class = ResetPasswordTokenSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			token = serializer.validated_data.get('token')
			ui64 = serializer.validated_data.get('ui64')
			new_password = serializer.validated_data.get('new_password')
			ui = smart_str(urlsafe_base64_decode(ui64))
			if not User.objects.filter(unique_identifier=ui).exists():
				return Response({"user": "No such user"}, status=status.HTTP_400_BAD_REQUEST)
			user = User.objects.get(unique_identifier=ui)
			if not PasswordResetTokenGenerator().check_token(user, token):
				return Response({"token": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
			if user.check_password(new_password):
				return Response({"new_password": "You are using the same password"}, status=status.HTTP_400_BAD_REQUEST)
			user.set_password(new_password)
			user.save()
			return Response({"message": "Password was resetted successfully"}, status=status.HTTP_200_OK)

class ChangePassword(APIView):
	permission_classes = (IsAuthenticated,)
	serializer_class = ChangePasswordSerializer
	def patch(self, request):
		serializer = self.serializer_class(data=request.data, context = {'request': request})
		if serializer.is_valid(raise_exception=True):
			user = serializer.context['request'].user
			password = serializer.validated_data.get('password')
			new_password = serializer.validated_data.get('new_password')
			if user.check_password(new_password):
				return Response({"new_password": "the new password is the same as the old password"}, status=status.HTTP_400_BAD_REQUEST)
			if not user.check_password(password):
				return Response({"password": "the password provided is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
			user.set_password(new_password)
			user.save()
			return  Response({"message": "password changed successfully"}, status=status.HTTP_200_OK)

class IsUserAuthenticated(APIView):
	serializer_class = LogoutSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			token = serializer.validated_data.get('token')
			if Token.objects.filter(key = token).exists():
				return Response({"message": "user is authenticated"}, status=status.HTTP_200_OK)
			return Response({"message": "no such token"}, status=status.HTTP_200_OK)
	