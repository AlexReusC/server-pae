from rest_framework import serializers
from api.models import Question, QuestionPoll, Poll, Tutor
from api.models.tutoring import Tutoring

class TutorPollSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutor
		fields = ('name', 'registration_number')

class QuestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Question
		fields = ('__all__')

class QuestionPollSerializer(serializers.ModelSerializer):
	question = QuestionSerializer(read_only=True)
	question_id = serializers.PrimaryKeyRelatedField(write_only=True, source='question', queryset=Question.objects.all())

	class Meta:
		model = QuestionPoll
		fields = ('question_id', 'question', 'result',)
		depth = 1

class ResultSerializer(serializers.Serializer):
	result = serializers.IntegerField()
	total = serializers.IntegerField()


class PollResultsSerializer(serializers.Serializer):
	question = QuestionSerializer()
	results = ResultSerializer(many=True)

class PollSerializer(serializers.ModelSerializer):
	question_polls = QuestionPollSerializer(many=True)
	tutor = TutorPollSerializer(read_only=True)

	class Meta:
		model = Poll
		fields = ('tutoring', 'comment', 'question_polls', 'tutor')

	def create(self, validated_data):
		question_poll_data = validated_data.pop('question_polls')
		poll = Poll.objects.create(tutoring=validated_data['tutoring'], comment=validated_data['comment'])
		for question_poll in question_poll_data:
			QuestionPoll.objects.create(poll=poll, **question_poll)
		print(validated_data['tutoring'])
		tutoring = validated_data['tutoring']
		tutoring.status = "CO"
		tutoring.has_feeback = True
		tutoring.save()
		return poll

	def validate_question_polls(self, value):
		num_questions = Question.objects.count()
		if num_questions != len(value):
			raise serializers.ValidationError("Received incorrect number of questions")
		visited_questions = set()
		for x in value:
			pk_question = x['question'].pk
			if pk_question in visited_questions:
				raise serializers.ValidationError("Repeated question")
			visited_questions.add(pk_question)	
		return value

	def validate(self, data):
		user = self.context['request'].user
		if not user.is_student:
			raise serializers.ValidationError({"user": "User must be a student"})
		if not data.get('tutoring').student or not data.get('tutoring').student.user == self.context['request'].user:
			raise serializers.ValidationError({"user": "This student cannot post this poll"})
		return data


