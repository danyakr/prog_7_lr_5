from django.urls import path
from .views import (
    QuestionListAPIView,
    QuestionStatsAPIView,
    QuestionFilterByDateAPIView,
    statistics_view,  # 👈 добавили
)

app_name = 'analytics'

urlpatterns = [
    path('questions/', QuestionListAPIView.as_view(), name='question-list'),
    path('questions/<int:pk>/stats/', QuestionStatsAPIView.as_view(), name='question-stats'),
    path('questions/filter/', QuestionFilterByDateAPIView.as_view(), name='question-filter'),
    path('statistics/', statistics_view, name='statistics'),
]
