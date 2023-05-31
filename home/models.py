import random
import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, User


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_domain = models.CharField(max_length=100)


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateField(auto_now=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    category_name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.category_name


class Question(BaseModel):
    category = models.ForeignKey(Category, related_name='category', on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    marks = models.IntegerField(default=10)

    def __str__(self) -> str:
        return self.question

    def get_answers(self):
        answer_objs = list(Answer.objects.filter(question=self))
        random.shuffle(answer_objs)
        data = []
        for answer_obj in answer_objs:
            data.append({
                'answer': answer_obj.answer,
                'is_correct': answer_obj.is_correct
            })
        return data


class Answer(BaseModel):
    question = models.ForeignKey(Question, related_name='question_answer', on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.answer


class CourseSuggestion(models.Model):
    DIFFICULTY_LEVEL = (
        ("BG", "Beginner"),
        ("IN", "Intermediate"),
        ("AD", "Advanced"),
    )
    technology = models.ForeignKey(Category, related_name='suggestion', on_delete=models.CASCADE)
    course_url = models.URLField(max_length=1000,default=None)
    difficulty = models.CharField(max_length=2, choices=DIFFICULTY_LEVEL, default='BG')
    course_name = models.CharField(max_length=100, default=' ')
    course_instructor = models.CharField(max_length=50, default=' ')
    ratings = models.FloatField(default=4.0)
    course_duration = models.FloatField(null=True)

    class Meta:
        db_table = 'course_suggestion'

    def __str__(self) -> str:
        return self.course_url


class Otp(models.Model):
    mail = models.CharField(max_length=50)
    otp = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    count = models.IntegerField(default=0)


class QuizAttempt(models.Model):
    timer = models.IntegerField(default=0)
    domain = models.CharField(max_length=50, default='')


class QuizUserScore(models.Model):
    user = models.CharField(User, max_length=50)
    quiz_domain = models.CharField(max_length=50, null=True)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)


class UserTracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.action}"


class QuizProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_answered = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.quiz.question}"


class ProgressUserQuiz(models.Model):
    STATUS_CHOICES = (
        ('answered', "Answered"),
        ('passed', "Passed"),
        ('closed', "Closed"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=50)
