import json
import logging
import random
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Question, QuizAttempt, QuizUserScore
from .models import PlayerActivity, CourseSuggession, Video
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseBadRequest


logger = logging.getLogger(__name__)


def index(request):
    '''
    Instructions page
    '''
    logger.info('Instruction page is accessed')
    return render(request, 'index.html')


def url(score, category):
    '''
    Based on the employee quiz attempt score and difficulty level
    This will suggest a course from Udemy and youtube course.
    '''
    YouTube_id = ''
    Title = ''
    suggesstion_url = None
    course_name = None
    ratings = None
    instructor = None
    duration = None
    difficulty = None
    YouTube_id = None
    Title = None

    if score <= 50:
        logger.info('Based on employee score we '
                    'are suggesting Beginner course')
        suggesstion = CourseSuggession.objects.filter(
            technology__category_name__icontains=category, difficulty='BG')
        suggestion_vdo = Video.objects.filter(
            technology_v__category_name__icontains=category, difficulty='BG')
        for val in suggesstion:
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            # logger.info(f'Suggested udemy course: {course_name}')
            break
        for v_id in suggestion_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            # logger.info(f'Suggested youtube course: {Title}')
            # logger.info(f'Youtube ID: {YouTube_id}')
            break

    elif 50 < score <= 70:
        logger.info('Based on employee score we are '
                    'suggesting Intermediate course')
        suggesstion = CourseSuggession.objects.filter(
            technology__category_name__icontains=category, difficulty='IN')
        suggestion_vdo = Video.objects.filter(
            technology_v__category_name__icontains=category, difficulty='IN')
        for val in suggesstion:
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            logger.info(f'Suggested udemy course: {course_name}')
            break
        for v_id in suggestion_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            logger.info(f'Suggested youtube course: {Title}')
            logger.info(f'Youtube ID: {YouTube_id}')
            break

    elif score > 70 <= 100:
        logger.info('Based on employee score we '
                    'are suggesting Advanced course')
        suggesstion = CourseSuggession.objects.filter(
            technology__category_name__icontains=category, difficulty='AD')
        suggesst_vdo = Video.objects.filter(
            technology_v__category_name__icontains=category, difficulty='AD')
        for val in suggesstion:
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            logger.info(f'Suggested udemy course: {course_name}')
            break
        for v_id in suggesst_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            logger.info(f'Suggested youtube course: {Title}')
            logger.info(f'Youtube ID: {YouTube_id}')
            break

    return suggesstion_url, course_name, ratings, \
        instructor, duration, difficulty, YouTube_id, Title


@login_required(login_url='login')
def quiz(request):
    '''
    Based on the selected category it will redirect to quiz page
    '''
    mail = request.session.get('mail')
    user = User.objects.get(email=mail)
    time_remaining = QuizAttempt.objects.filter(
        user=user).values_list('timer', 'domain')
    if time_remaining:
        rem_time = list(time_remaining)
        update_timer = rem_time[0][0]
        logger.info(f'Employee still having '
                    f'the previous quiz timer with {update_timer} sec')
        if request.GET.get('category') == \
                rem_time[0][1] and rem_time[0][0] > 5:
            new_timer = update_timer
        else:
            new_timer = 300
    else:
        new_timer = 300
    context = {'category': request.GET.get('category'), 'new_timer': new_timer}
    logger.info('Employee agreed to terms and conditions with selected '
                'domain {}, redirecting to quiz page'
                .format(request.GET.get('category')))
    return render(request, 'quiz.html', context)


@login_required(login_url='login')
def get_quiz(request):
    '''
    Based on selected category it will generate
    ten random questions along with options
    '''
    try:
        logger.info('Quiz question loaded successfully')
        questions_objs = Question.objects.all()
        if request.GET.get('category'):
            request.session['category'] = request.GET.get('category')
            questions_objs = questions_objs.filter(
                category__category_name__icontains=request.GET.get('category'))
        questions_objs = list(questions_objs)
        data = []
        random.shuffle(questions_objs)
        counter = int()
        for question_obj in questions_objs:
            counter += 1
            if counter < 11:
                data.append({
                    "uid": question_obj.uid,
                    "category": question_obj.category.category_name,
                    "question": question_obj.question,
                    "marks": question_obj.marks,
                    "time": request.POST.get('timer'),
                    "answers": question_obj.get_answers()
                })
        return JsonResponse({'data': data, 'status': True})
    except Exception as e:
        logger.error(e)
    return HttpResponse("Something went worng")


@login_required(login_url='login')
def save_remaining_time(request):
    '''
    This method is used to save the remaining quiz timer in database
    '''
    if request.method == 'POST':
        remaining_time = request.POST.get('remainingTime')
        category = request.POST.get('category')
        quiz_timer = QuizAttempt()
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        quiz_timer.timer = remaining_time
        quiz_timer.user = user
        quiz_timer.domain = category
        quiz_timer.save()
        logger.info(f'saving remaining time in database: {remaining_time}')
        return JsonResponse({'message': 'Remaining time saved successfully'})
    return JsonResponse({'message': 'Invalid request method'}, status=400)


score = 0
suggesstion_url = str()
course_name = str()
ratings = 0
instructor = str()
duration = float()
difficulty = str()
YouTube_id = str()
Title = str()


@login_required(login_url='login')
def result(request):
    '''
    This method will generate employee score
    '''
    if request.method == 'POST':
        logger.info('Results page accessed!')
        quiz_add = QuizUserScore()
        global score, suggesstion_url, course_name, ratings, \
            duration, instructor, difficulty, YouTube_id, Title
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        score_data = json.loads(request.body)
        score = score_data.get('score')
        category = score_data.get('category')
        quiz_add.quiz_domain = category
        quiz_add.score = score * 10
        quiz_add.user = user
        kolkata_tz = timezone.get_current_timezone()
        current_time = timezone.localtime(timezone.now(), kolkata_tz)
        quiz_add.created_at = current_time.astimezone(timezone.utc)
        quiz_add.save()
        suggesstion_url, course_name, ratings, \
            instructor, duration, difficulty, \
            YouTube_id, Title = url(score=quiz_add.score, category=category)
        logger.info(f'Based on quiz attempt employee got '
                    f'{score * 10} score & selected domain {category}')
        return HttpResponse(status=200)


@login_required(login_url='login')
def skip_quiz(request):
    '''
    This method will skip the quiz and redirect to overall
    recomendations page based on selected catergory
    '''
    selected_category = request.GET.get('category')
    context = {}
    if selected_category:
        suggestions = CourseSuggession.objects.filter(
            technology__category_name__icontains=selected_category)
        context['suggestions'] = suggestions
    logger.info('Employee skipped the quiz and select domain '
                '{} and redirected to all recomendations page '
                'with all the avaliable courses'.
                format(request.GET.get('category')))
    return render(request, 'skipquiz.html', context)


@login_required(login_url='login')
def final(request):
    '''
    Based on will redirect to results page
    along with the udemy and youtube course data
    '''
    context = {
        "score": score * 10, 'suggested': suggesstion_url,
        'course_name': course_name, 'ratings': ratings,
        'duration': duration, 'instructor': instructor,
        'difficulty': difficulty, 'YouTube_id': YouTube_id,
        'title': Title}
    logger.info('Employee redirect to results page with course suggestion')
    return render(request, 'results.html', context=context)


@csrf_exempt
def save_time(request):
    '''
    This method is used to record the duration
    of completed time for a YouTube video
    '''
    if request.method == 'POST':
        data = json.loads(request.body)
        current_time = data.get('current_time')
        youtube_id = data.get('youtube_id')
        percentage = data.get('percentage')
        selectedcategory = data.get('selectedcategory')

        # print(current_time)
        # print(youtube_id)
        # print(percentage)
        # print(selectedcategory)

        if current_time is None:
            current_time = 0  # Assign a numeric default value

        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        check = PlayerActivity.objects.filter(youtube_id=youtube_id, user=user)
        # print(check)
        if check:
            PlayerActivity.objects.filter(
                user=user, youtube_id=youtube_id).update(
                current_time=current_time, percentage=percentage)
            # print('inside check')
        # player_activity.current_time = current_time
        # player_activity.percentage = percentage
        # player_activity.save()
        else:
            # print('its else')
            PlayerActivity.objects.create(current_time=current_time,
                                          percentage=percentage,
                                          youtube_id=youtube_id,
                                          category=selectedcategory,
                                          user=user)
        logger.info(f'Watched timer for youtube id: '
                    f'{youtube_id} with percentage : {percentage}')
        return JsonResponse({'message': 'Time saved successfully'})
    else:
        return HttpResponseBadRequest('Invalid request method')