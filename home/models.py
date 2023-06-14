import random
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User




class QuizUserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # user = models.CharField(User, max_length=50)
    quiz_domain = models.CharField(max_length=50, null=True)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)

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
    category =  models.ForeignKey(Category,related_name='category', on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    marks = models.IntegerField(default=10)

    def __str__(self) -> str:
        return self.question

    def get_answers(self):
        answer_objs = list(Answer.objects.filter(question = self))
        random.shuffle(answer_objs)
        data = []
        for answer_obj in answer_objs:
            data.append({
                'answer':answer_obj.answer,
                'is_correct' : answer_obj.is_correct
            })
        return data

class Answer(BaseModel):
    question = models.ForeignKey(Question,related_name='question_answer', on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.answer
 

# class CourseSuggession(models.Model):
#     DIFFICULTY_LEVEL = (
#         ("BG", "Begginer"),
#         ("IN", "Intermediate"),
#         ("AD", "Advanced"),
#     )
#     technology = models.ForeignKey(Category, on_delete=models.CASCADE)
#     course_url = models.URLField(max_length=1000)
#     difficulty = models.CharField(max_length=2, choices=DIFFICULTY_LEVEL, default='BG')
#     class Meta:
#         db_table = 'course_suggestion'



class CourseSuggession(models.Model):
    DIFFICULTY_LEVEL = (
        ("BG", "Beginner"),
        ("IN", "Intermediate"),
        ("AD", "Advanced"),
    )
    technology = models.ForeignKey(Category,related_name='suggesstion', on_delete=models.CASCADE)
    course_url = models.URLField(max_length=1000)
    # difficulty = models.CharField(max_length=2, choices=DIFFICULTY_LEVEL)
    difficulty = models.CharField(max_length=2, choices=DIFFICULTY_LEVEL, default='BG')
    course_name = models.CharField(max_length=100, default= ' ')
    course_instructor = models.CharField(max_length=50,default=' ')
    ratings = models.FloatField(default=4.0)
    course_duration = models.FloatField(null=True)


    
    class Meta:
        db_table = 'course_suggestion'

    def __str__(self) -> str:
        return self.course_url        

#  testing_otp_code
class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mail = models.CharField(max_length=50)
    otp = models.CharField(max_length=50)
    # username = models.CharField(max_length=50)
    count = models.IntegerField(default=0)


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # username = models.CharField(max_length=50,default='')
    timer = models.IntegerField(default=0)
    domain = models.CharField(max_length=50, default='')
