# Лабораторная работа 5. Django REST Framework: (микро)сервисы
## Улучшение (improvement) приложения для голосований
Для улучшения функциональности приложения для создания голосований (polls) из предыдущих лабораторных работ, создайте микросервис (или несколько микросервисов), написанный с использованием Django REST Framework
(DRF), который предоставляет возможность анализа результатов голосований и предоставления статистики по голосованиям.
Этот микросервис (poll analytics) будет вторым приложением в вашем Django-проекте.

---

## 1. Цель работы

Улучшение приложения для голосований (polls) с помощью микросервисов на Django REST Framework.  
Реализован микросервис для аналитики голосований, который позволяет:

- Просматривать список всех голосований
- Фильтровать голосования по дате
- Получать статистику по каждому голосованию
- Отображать диаграмму голосов в формате SVG

Все голосования являются анонимными, авторизация не требуется.

---

## 2. Структура проекта

Проект состоит из двух приложений:

1. **polls** — основное приложение для создания голосований  
2. **analytics** — микросервис для аналитики и статистики голосований

---

## 3. Реализованный функционал

### 3.1. Микросервис списка голосований

- Публикует список всех опросов через API:
  - URL: `/api/analytics/questions/`
  - Метод: GET
  - Результат: JSON-список вопросов с `id` и `question_text`

### 3.2. Микросервис статистики голосования

- Получает статистику для выбранного голосования:
  - URL: `/api/analytics/questions/<id>/stats/`
  - Метод: GET
  - Возвращает:
    - `question_text` — текст вопроса
    - `total_votes` — общее количество голосов
    - `choices` — список вариантов с количеством голосов (без процентов)
    - `histogram_svg` — диаграмма голосов в формате SVG

### 3.3. Микросервис фильтрации по дате

- Позволяет искать голосования по дате публикации:
  - URL: `/api/analytics/questions/filter/`
  - Метод: POST
  - Тело запроса:
    ```json
    {
      "publication-dates": { "from": "2025-10-01", "to": "2025-10-31" }
    }
    ```
  - Возвращает JSON-список вопросов за указанный период

### 3.4. Страница поиска и статистики

- Страница: `/analytics/statistics/`  
- Функционал:
  - Ввод диапазона дат
  - Кнопка **Search** для фильтрации голосований
  - Список найденных опросов слева
  - Динамическое отображение статистики и диаграммы справа по клику на опрос

---

## 4. Код микросервиса `analytics/views.py`

```python
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
            data.append({
                'choice_text': choice.choice_text,
                'votes': choice.votes
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

```
---

## 5. Код страницы analytics/templates/analytics/statistics.html

```
{% extends 'polls/base.html' %}
{% load static %}
{% block content %}

<style>
#stats-container svg {
  width: 100%;
  height: auto;
  max-width: 600px;
  display: block;
  margin: 0 auto;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
</style>

<div class="container mt-4">
  <div class="row">
    <div class="col-md-5 border-end">
      <h3>📅 Filter Polls</h3>
      <input type="date" id="from-date" class="form-control mb-2">
      <input type="date" id="to-date" class="form-control mb-2">
      <button class="btn btn-dark w-100" id="search-btn">Search</button>
      <hr>
      <div id="question-list"></div>
    </div>

    <div class="col-md-7">
      <h3>📊 Poll Statistics</h3>
      <div id="stats-container"></div>
    </div>
  </div>
</div>

<script>
async function fetchQuestions() {
  const response = await fetch('/api/analytics/questions/');
  const data = await response.json();
  const list = document.getElementById('question-list');
  list.innerHTML = '';
  data.forEach(q => {
    const el = document.createElement('a');
    el.href = '#';
    el.textContent = q.question_text;
    el.classList.add('d-block', 'p-2', 'border', 'rounded', 'mb-2');
    el.onclick = () => loadStats(q.id);
    list.appendChild(el);
  });
}

async function loadStats(id) {
  const res = await fetch(`/api/analytics/questions/${id}/stats/`);
  const data = await res.json();
  const stats = document.getElementById('stats-container');
  stats.innerHTML = `
    <h4>${data.question_text}</h4>
    <p>Total votes: ${data.total_votes}</p>
    <div>${data.histogram_svg}</div>
  `;
}

document.getElementById('search-btn').addEventListener('click', async () => {
  const fromDate = document.getElementById('from-date').value;
  const toDate = document.getElementById('to-date').value;

  if (!fromDate || !toDate) {
    alert('Please select both dates!');
    return;
  }

  const response = await fetch('/api/analytics/questions/filter/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      'publication-dates': { from: fromDate, to: toDate }
    })
  });

  const data = await response.json();
  const list = document.getElementById('question-list');
  list.innerHTML = '';

  if (data.questions) {
    data.questions.forEach(q => {
      const el = document.createElement('a');
      el.href = '#';
      el.textContent = q.question_text;
      el.classList.add('d-block', 'p-2', 'border', 'rounded', 'mb-2');
      el.onclick = () => loadStats(q.id);
      list.appendChild(el);
    });
  } else {
    list.innerHTML = '<p>No questions found for this period.</p>';
  }
});

document.addEventListener('DOMContentLoaded', fetchQuestions);
</script>

{% endblock %}

```
---

## 6. Используемые технологии

- Python 3.x  
- Django 4.x  
- Django REST Framework  
- Plotly (для генерации диаграмм в SVG)  
- HTML / CSS / JavaScript (Bootstrap для стилизации)  

---

## 7. Принцип работы

1. Пользователь открывает страницу статистики `/analytics/statistics/`  
2. Загружается список всех голосований через `QuestionListAPIView`  
3. Пользователь может:
   - Кликнуть на вопрос и увидеть диаграмму голосов
   - Выбрать диапазон дат и нажать **Search**, чтобы отфильтровать голосования
4. Диаграмма формируется на сервере с помощью Plotly и передается в формате SVG  
5. Страница динамически обновляет статистику без перезагрузки  

---

## 8. Пример JSON-ответа микросервиса статистики

```json
{
  "question_text": "What's your favorite color?",
  "total_votes": 10,
  "choices": [
    {"choice_text": "Red", "votes": 4},
    {"choice_text": "Blue", "votes": 3},
    {"choice_text": "Green", "votes": 3}
  ],
  "histogram_svg": "<svg ...>...</svg>"
}
```
---

## 9. Итоги работы

- Создано приложение `analytics` с микросервисами:
  - Список голосований
  - Статистика голосования с диаграммой
  - Фильтрация по дате
- Страница статистики позволяет удобно просматривать результаты голосований
- Все данные отображаются динамически с помощью JavaScript
- Диаграмма SVG адаптирована под ширину блока и имеет тени и скругления

---

## Скриншоты работы приложения

### Главная страница
![Главная страница](https://github.com/user-attachments/assets/1581c206-8d6d-4cf9-9a8e-72d4ea922f1f)

### Вкладка "Statistics"
![Вкладка Statistics](https://github.com/user-attachments/assets/f8825357-ee9f-4af8-927c-8012b323918c)

### Выбор дат
![Выбор дат](https://github.com/user-attachments/assets/989c3771-1d39-43cc-9d7c-aa94e0721dc7)

### Пример статистики
![Пример статистики](https://github.com/user-attachments/assets/cba78305-06f3-4193-84c6-07940c630edc)



