from rest_framework import viewsets, status
from rest_framework.views import APIView
from api.models import Tutoring
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from api.models import Schedule, Tutor, Period, Tutoring
from api.permissions import IsAdministrator, IsAdministratorOrStudent, TutoringViewsetPermission
from api.serializers import TutoringSerializer, ParamsAvailableTutoringSerializer, AvailableTutoringSerializerList, AvailableTutoring
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin

from api.serializers.tutoring import ChangeTutorSerializer, ChangeTutoringLocationSerializer, ParamsAlternateTutorSerializer, AlternateTutorSerializer
from api.constants import START_DATE_FIELDS, END_DATE_FIELDS
from django.core.mail import send_mail

import datetime

class AvailableTutorings(APIView):
    serializer_class = ParamsAvailableTutoringSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            subject = serializer.validated_data.get("subject")
            initial_date_serializer = serializer.validated_data.get("initial_date_serializer")
            final_date_serializer = serializer.validated_data.get("final_date_serializer")

            # find tutors with that subject
            tutors_with_subject = Tutor.objects.filter(subjecttutor__subject=subject)
            # retrieve schedules
            schedules_tutors = Schedule.objects.filter(tutor__in=tutors_with_subject)
            #it gets the start and end dates of the period
            period = Period.objects.filter().first()
            list_available_tutorings = []

            #it goes for the 3 periods
            for current_period in range(3):
                #it gets the initial and end date for that period
                start_date, end_date = START_DATE_FIELDS[current_period], END_DATE_FIELDS[current_period]
                initial_date, final_date = period.__dict__[start_date], period.__dict__[end_date]
                #checks if period is inside asked dates
                if not (initial_date_serializer > final_date or final_date_serializer < initial_date):
                    #checks if it has to use dates of period or dates asked
                    initial_date = max(initial_date_serializer, initial_date)
                    final_date = min(final_date_serializer, final_date)
                    delta = final_date - initial_date
                    #gets dates in that period
                    current_period_dates = [initial_date + datetime.timedelta(days=current_period) for current_period in range(delta.days + 1)]
                    #split dates by day of the week
                    days_by_week = {}
                    available_tutorings = {}
                    for i in range(0, 6):
                        days_by_week[i] = []
                    for date_in_period in current_period_dates:
                        if date_in_period.weekday() >= 0 and date_in_period.weekday() <= 4:
                            available_tutorings[date_in_period] = []
                            days_by_week[date_in_period.weekday()+1].append(date_in_period)

                    #creates possible tutorings with the schedules and the dates in this period
                    for schedule in schedules_tutors:
                        if schedule.period == current_period:
                            for date_in_period in days_by_week[schedule.day_week]:
                                available_tutorings[date_in_period].append(AvailableTutoring(hour=schedule.hour, period=schedule.period, tutor=schedule.tutor, isOnline=True))
                                # TODO: validate tutor and student are not the same person

                    #eliminates if there is already a tutoring at that time and with the same tutor
                    tutorings_with_same_tutors = Tutoring.objects.filter(tutor__in=tutors_with_subject)
                    for tutoring in tutorings_with_same_tutors:
                        if tutoring.date in available_tutorings:
                            available_tutorings[tutoring.date] = list(filter(
                                lambda x: x.hour != tutoring.hour or x.tutor != tutoring.tutor.registration_number, available_tutorings[tutoring.date]))

                    #gives format for returning
                    for available_tutoring in available_tutorings.items():
                        list_available_tutorings.append({"date": available_tutoring[0], "tutorings": available_tutoring[1]})

            return Response(AvailableTutoringSerializerList(list_available_tutorings, many=True).data)

class AlternateTutor(APIView):
    serializer_class = ParamsAlternateTutorSerializer
    permission_classes = (IsAdministrator,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            subject = serializer.validated_data.get("subject")
            date = serializer.validated_data.get("date")
            hour = serializer.validated_data.get("hour")

            day_week = date.weekday()

            #check to which period the date belongs
            period = Period.objects.filter().first()
            current_period = -1
            for i in range(3):
                start_date, end_date = START_DATE_FIELDS[i], END_DATE_FIELDS[i]
                initial_date, final_date = period.__dict__[start_date], period.__dict__[end_date]
                if date >= initial_date and date <= final_date:
                    current_period = i
                    break
            if current_period == -1:
                return Response({"date": "date not inside any period"}, status=status.HTTP_400_BAD_REQUEST)


            #find tutors with such subject
            tutors_with_subject = Tutor.objects.filter(subjecttutor__subject=subject)
            #get schedule for such tutors
            schedules_tutors = Schedule.objects.filter(tutor__in=tutors_with_subject, period=current_period, hour=hour, day_week=day_week)

            tutors_with_schedule = Tutor.objects.filter(schedule__in=schedules_tutors)

            #removes tutors with a tutoring in such date and hour
            tutoring_same_time = Tutoring.objects.filter(date=date, hour=hour)
            tutors_with_tutoring = set()
            for tutoring in tutoring_same_time:
                tutors_with_tutoring.add(tutoring.tutor.registration_number)
            # print(tutors_with_tutoring)

            available_tutors = []
            for tutor in tutors_with_schedule:
                if tutor.registration_number not in tutors_with_tutoring:
                    available_tutors.append(tutor)

            return Response(AlternateTutorSerializer(available_tutors, many=True).data)

class ChangeTutor(GenericAPIView, UpdateModelMixin):
    serializer_class = ChangeTutorSerializer
    queryset = Tutoring.objects.all()
    permission_classes = (IsAdministrator,)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class TutoringViewSet(viewsets.ModelViewSet):
    serializer_class = TutoringSerializer
    queryset = Tutoring.objects.all()
    permission_classes = (TutoringViewsetPermission,)
    http_method_names = ["get", "post", "delete", "head", "options"]
    filter_fields = ('status','student', 'tutor')

class ChangeTutoringLocation(GenericAPIView, UpdateModelMixin):
    serializer_class = ChangeTutoringLocationSerializer
    queryset = Tutoring.objects.all()
    permission_classes = (IsAdministrator,)
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class UpdateTutoring(APIView):
    def put(self, request, *args, **kwargs):
        def formatEmail():
            return f"<html style=''><html lang='es'><head><meta charset='UTF-8'><link rel='preconnect' href='https://fonts.googleapis.com'><link rel='preconnect' href='https://fonts.gstatic.com' crossorigin><link href='https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap' rel='stylesheet'></head><body style='margin: 0;padding: 0;font-family:Montserrat, sans-serif;box-sizing:border-box; justify-content:center;align-items:center; background:#8f91a2;'><div class='oxxo-pay' style='height: auto;max-width:550px;background: #fff;padding: 50px 50px 10px 50px;margin: 0 auto;'><div class='oxxo-header' style='background-image: url('logo.ico');background-repeat:no-repeat;height:60px;background-position:center;background-size:contain;'></div><h4 style='text-align:center;font-weight:300;font-size:20px; padding-bottom:20px;border-bottom: 2px solid rgba(74, 74, 74, 0.25);'>PAE</h4><h1 style='font-size:30px;text-align:center;padding:30px;color:#545b65;font-weight:600;'>Notificación de asesoría solicitada</h1><div class='box' style='background:rgba(211,192,179,.4);margin-top:30px;padding:35px;justify-content: space-between;flex-direction:column;align-items:center;font-size: 14px;color:#545b65;'><p style='text-align:center;'>Accede a tu cuenta y revisa el estado de la asesoría.</p> </div><div class='summary' style='width:100%;margin-top:45px;margin-bottom:45px;justify-content:center;align-items:center;text-align:center;flex-direction:column;'><div class='summary_header' style='margin-bottom:20px;height:auto;flex-direction:column;justify-content:center;align-items:center;text-align:center;'></div></div><footer><p style='margin-bottom:4px;font-size:14px;text-align:center'> © PAE 2021. Desarrollado por Hacket</p></footer></div></body></html>"
        permission_classes = (IsAdministrator,)
        pk = self.kwargs['pk']
        stat = self.kwargs['status']
        if not Tutoring.objects.filter(pk = pk).exists():
            return Response({"pk": "does not exist"}, status=status.HTTP_404_NOT_FOUND)
        tutoring = Tutoring.objects.filter(pk = pk).first()
        send_mail("Notifiación de cambios en asesorías", "Accede a tu cuenta de PAE", None, [tutoring.student.email], html_message=formatEmail())
        send_mail("Notifiación de cambios en asesorías", "Accede a tu cuenta de PAE", None, [tutoring.tutor.email], html_message=formatEmail())
        tutoring.status = stat
        tutoring.save()
        return Response(TutoringSerializer(tutoring).data, status=status.HTTP_200_OK)
