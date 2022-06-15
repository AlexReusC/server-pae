from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('student', views.StudentViewSet)
router.register('tutor', views.TutorViewSet)
router.register('subject', views.SubjectViewSet)
router.register('tutoring', views.TutoringViewSet)
router.register('administrator', views.AdministratorViewSet)
router.register('question', views.QuestionViewSet)
router.register('poll', views.PollViewSet)

urlpatterns = [
	path('', include(router.urls)),
	path('login/', views.Login.as_view()),
	path('logout/', views.Logout.as_view()),
	path('resetpassword/', views.ResetPasswordEmail.as_view()),
	path('changepasswordtoken/', views.ResetPasswordToken.as_view()),
	path('changepassword/', views.ChangePassword.as_view()),
	path('availabletutoring/', views.AvailableTutorings.as_view()),
	path('verifyemail/', views.VerifyEmail.as_view()),
	path('tutorisaccepted/<pk>', views.TutorIsAccepted.as_view()),
	path('pollresult/', views.PollResults.as_view()),
	path('changetutoringlocation/<pk>', views.ChangeTutoringLocation.as_view()),
	path('updatetutoring/<pk>/<status>', views.UpdateTutoring.as_view()),
	path('alternatetutor/', views.AlternateTutor.as_view()),
	path('subjectbytutor/<tutor>', views.SubjectByTutorDetail.as_view()),
	path('subjectbytutor/', views.SubjectByTutor.as_view()),
	path('changetutor/<pk>', views.ChangeTutor.as_view()),
	path('modifyschedule/', views.ModifySchedule.as_view()),
	path('isauthenticated/', views.IsUserAuthenticated.as_view())
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)