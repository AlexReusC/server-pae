from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
	def create_user(self, unique_identifier, password):
		user = self.model(unique_identifier=unique_identifier)
		user.set_password(password)
		user.save(using=self.db)
		return user 
	
	def create_superuser(self, unique_identifier, password):
		user = self.create_user(unique_identifier, password)
		user.is_superuser = True
		user.is_staff = True
		user.save(using=self.db)
		return user

class User(AbstractBaseUser, PermissionsMixin):
	unique_identifier = models.CharField(max_length=22, primary_key=True)
	is_validated = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)
	is_tutor = models.BooleanField(default=False)
	is_student = models.BooleanField(default=False)
	is_administrator = models.BooleanField(default=False)

	objects = UserManager()

	USERNAME_FIELD = 'unique_identifier'

	@property
	def role_account(self):
		if self.is_tutor:
			return self.tutor
		if self.is_student:
			return self.student
		if self.is_administrator:
			return self.administrator