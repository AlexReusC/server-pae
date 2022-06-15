from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Administrator

class IsTutor(BasePermission):
	def has_permission(self, request, view):
		return request.user.is_authenticated and request.user.is_tutor

class IsAdministratorOrStudent(BasePermission):
	def has_permission(self, request, view):
		if not request.user.is_authenticated:
			return False
		return request.user.is_administrator or request.user.is_student

class IsAdministrator(BasePermission):
	def has_permission(self, request, view):
		if not request.user.is_authenticated:
			return False
		return request.user.is_administrator

class IsAdministratorOrReadOnly(BasePermission):
	def has_permission(self, request, view):
		if request.method in SAFE_METHODS:
			return True
		if not request.user.is_authenticated:
			return False
		if request.user.is_administrator:
			return True
		return False

class TutoringViewsetPermission(BasePermission):
	def has_permission(self, request, view):
		if not request.user.is_authenticated:
			return False
		if request.method in SAFE_METHODS:
			return True
		return request.user.is_administrator or request.user.is_student

class AdministratorViewsetPermission(BasePermission):
	def has_permission(self, request, view):
		if not Administrator.objects.filter().exists():
			return True
		if not request.user.is_authenticated or not request.user.is_administrator:
			return False
		if request.method in SAFE_METHODS:
			return True
		return request.user.is_staff

class PollViewSetPermission(BasePermission):
	def has_permission(self, request, view):
		if not request.user.is_authenticated:
			return False
		if request.method == 'POST':
			if request.user.is_student:
				return True
			return False 
		if request.user.is_administrator:
			return True
		return False

class StudentTutorPermission(BasePermission):
	def has_permission(self, request, view):
		if request.method in SAFE_METHODS or request.method == 'POST':
			return True
		return request.user.is_authenticated and request.user.is_administrator