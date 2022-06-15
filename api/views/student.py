from rest_framework import viewsets
from api.models import Student 
from api.permissions import StudentTutorPermission
from api.serializers import StudentRegisterSerializer

class StudentViewSet(viewsets.ModelViewSet):
	permission_classes = (StudentTutorPermission,)
	http_method_names = ['get', 'post', 'options', 'head', 'delete']
	serializer_class = StudentRegisterSerializer
	queryset = Student.objects.all()