from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone
from polls.models import Question, Choice
from .serializers import QuestionSerializer
import plotly.graph_objects as go
import plotly.io as pio


class QuestionListAPIView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionStatsAPIView(APIView):
    def get(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

        choices = question.choice_set.all()
        total_votes = choices.aggregate(Sum('votes'))['votes__sum'] or 0
        data = []

        for choice in choices:
            percentage = (choice.votes / total_votes * 100) if total_votes > 0 else 0
            data.append({
                'choice_text': choice.choice_text,
                'votes': choice.votes,
                'percentage': round(percentage, 2)
            })

        # диаграмма
        fig = go.Figure(data=[go.Bar(x=[c['choice_text'] for c in data], y=[c['votes'] for c in data])])
        fig.update_layout(
            title=f"{question.question_text}",
            xaxis_title="Choices",
            yaxis_title="Votes",
            template="plotly_white"
        )
        svg_image = pio.to_image(fig, format='svg').decode('utf-8')

        return Response({
            'question_text': question.question_text,
            'total_votes': total_votes,
            'choices': data,
            'histogram_svg': svg_image
        })


class QuestionFilterByDateAPIView(APIView):
    def post(self, request):
        data = request.data.get('publication-dates', {})
        from_date = data.get('from')
        to_date = data.get('to')

        if not from_date or not to_date:
            return Response({'error': 'Both from and to dates must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_parsed = timezone.datetime.strptime(from_date, '%Y-%m-%d')
            to_parsed = timezone.datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        questions = Question.objects.filter(pub_date__range=[from_parsed, to_parsed])
        if not questions.exists():
            return Response({'message': 'No questions found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuestionSerializer(questions, many=True)
        return Response({'questions': serializer.data})

def statistics_view(request):
    return render(request, 'analytics/statistics.html')