from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Category)


class AnswerAdmin(admin.StackedInline):
    model = Answer


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerAdmin]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
# admin.site.register(CourseSuggession)

@admin.register(QuizUserScore)
class QuizScore(admin.ModelAdmin):
    list_display = ['user','quiz_domain','created_at','score']


@admin.register(CourseSuggession)
class CourseSuggession(admin.ModelAdmin):
    list_filter = ['technology']
    list_display = ['technology','difficulty','course_name','course_duration']

    # list_display = ['technology']
    # search_fields = ['technology']
    