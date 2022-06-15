from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny 
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
import jwt
from api.permissions import IsAdministrator, IsAdministratorOrReadOnly, IsTutor, StudentTutorPermission

from api.serializers import TutorRegisterSerializer, SubjectSerializer, VerifyEmailSerializer, TutorIsAcceptedSerializer, SubjectTutorSerializer,ModifyScheduleSerializer
from api.models import  Tutor, Subject, User, SubjectTutor, Schedule
from server.settings import SECRET_KEY

class TutorViewSet(viewsets.ModelViewSet):
	permission_classes = (StudentTutorPermission,)
	serializer_class = TutorRegisterSerializer
	queryset = Tutor.objects.all()
	filter_fields = ('registration_number',)

class TutorIsAccepted(GenericAPIView, UpdateModelMixin):
	permission_classes = (IsAdministrator,)
	serializer_class = TutorIsAcceptedSerializer
	queryset = Tutor.objects.all()

	def put(self, request, *args, **kwargs):
		return self.partial_update(request, *args, **kwargs)

class SubjectViewSet(viewsets.ModelViewSet):
	permission_classes = (IsAdministratorOrReadOnly,)
	serializer_class = SubjectSerializer
	queryset = Subject.objects.all()

class SubjectByTutorDetail(APIView):
	permission_classes = (AllowAny,)
	def get(self, request, *args, **kwargs):
		tutor = self.kwargs['tutor']
		subject_tutor = SubjectTutor.objects.filter(tutor = tutor)
		subjects = []
		for subject_tutor_object in subject_tutor:
			subjects.append(subject_tutor_object.subject)
		return Response(SubjectSerializer(subjects, many=True).data, status=status.HTTP_200_OK)	

class SubjectByTutor(APIView):
	permission_classes = (IsTutor,)
	serializer_class = SubjectTutorSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			tutor = serializer.validated_data.get("tutor")
			subject = serializer.validated_data.get("subject")
			if SubjectTutor.objects.filter(tutor=tutor, subject=subject).exists():
				return Response({"tutor": "such object already exixsts"}, status=status.HTTP_400_BAD_REQUEST)
			user = self.request.user.role_account
			if user != tutor:
				return Response({"tutor": "does not have permissions for this endpoint"}, status=status.HTTP_401_UNAUTHORIZED)
			subject_tutor = SubjectTutor.objects.create(tutor=tutor, subject=subject)
			return Response(SubjectTutorSerializer(subject_tutor).data, status=status.HTTP_201_CREATED)
	def delete(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			tutor = serializer.validated_data.get("tutor")
			subject = serializer.validated_data.get("subject")
			if not SubjectTutor.objects.filter(tutor=tutor, subject=subject).exists():
				return Response({"tutor": "such object does not exixsts"}, status=status.HTTP_400_BAD_REQUEST)
			user = self.request.user.role_account
			if user != tutor:
				return Response({"tutor": "does not have permissions for this endpoint"}, status=status.HTTP_401_UNAUTHORIZED)
			subject_tutor = SubjectTutor.objects.filter(tutor=tutor, subject=subject).delete()
			return Response({"tutor": "deleted"}, status=status.HTTP_200_OK)

class ModifySchedule(APIView):
	permission_classes = (IsTutor,)
	serializer_class = ModifyScheduleSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			tutor = serializer.validated_data.get('tutor')
			schedules = serializer.validated_data.get('schedules')
			user = self.request.user.role_account
			if user != tutor:
				return Response({"tutor": "does not have permissions for this endpoint"}, status=status.HTTP_401_UNAUTHORIZED)
			Schedule.objects.filter(tutor=tutor).delete()
			for schedule in schedules:
				Schedule.objects.create(tutor=tutor, **schedule)
			return Response({"schedule": "schedule updated"}, status=status.HTTP_201_CREATED)
			

class VerifyEmail(APIView):
	permission_classes = (AllowAny,)
	serializer_class = VerifyEmailSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			token = serializer.validated_data.get("token")
			key = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
			if not User.objects.filter().exists():
				return Response({"user": "user does not exist"})
			user = User.objects.get(unique_identifier=key['user_id'])
			tutor_or_student = user.role_account
			if not tutor_or_student.is_active:
				tutor_or_student.is_active = True
				tutor_or_student.save()
				role = ""
				if user.is_student:
					role = "student"
				if user.is_tutor:
					role = "tutor"
				return Response({'message': "user is now active", "role": role}, status=status.HTTP_201_CREATED)
			return Response({"token": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)