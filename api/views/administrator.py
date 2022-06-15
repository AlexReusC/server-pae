from rest_framework import viewsets
from api.models import Administrator
from api.permissions import AdministratorViewsetPermission

from api.serializers import AdministratorSerializer

class AdministratorViewSet(viewsets.ModelViewSet):
	permission_classes = (AdministratorViewsetPermission,)
	serializer_class = AdministratorSerializer
	queryset = Administrator.objects.all()