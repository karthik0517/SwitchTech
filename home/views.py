import json
import logging
import pytz
import random
import math
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout
from .models import Question, QuizAttempt, QuizUserScore, Otp
from .models import PlayerActivity, CourseSuggession, Category, Video
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseBadRequest


logger = logging.getLogger(__name__)


def generate_otp():
    '''
    It is will generate an 6 digit random number
    '''
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    logger.info(f'OTP is generated {OTP}')
    return OTP


count = 0


def loginPage(request):
    '''
    In this method it will check user session is still active or not if active
    it will redirect to Dashboard page, if not it will redirect to login page
    '''
    remember_me = request.session.get('remember_me', False)
    if remember_me:
        logger.info('User session exists (remember me enabled), '
                    'redirecting to the Dashboard page')
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        overall_progress = PlayerActivity.objects.filter(user=user).order_by(
            '-id').values_list('percentage', 'category')[:3]

        if overall_progress:
            percentages, categories = zip(*overall_progress)
            list_overall_progress = list(percentages)
            list_overall_categories = list(categories)
            rounded_progress = [round(value, 2)
                                for value in list_overall_progress]
            print(rounded_progress)
            sum_overall_progress = sum(rounded_progress)
            logger.info(f'Employee overall Progress: {sum_overall_progress} %')
            context = {
                'categories': Category.objects.all(),
                'list_overall_progress': rounded_progress,
                'list_categories': list_overall_categories,
                'overall_progress': sum_overall_progress
            }
            logger.info('Dashboard page is accessed')
            print(context)
            return render(request, 'dashboard.html', context)
        else:
            # Handle the case when no progress data is available
            logger.info('No progress data found')
            context = {
                'categories': Category.objects.all(),
                'list_overall_progress': [],
                'list_categories': [],
                'overall_progress': 0
            }
            return render(request, 'dashboard.html', context)

    elif request.method == "POST":
        logger.info('Login page accessed!')
        if request.POST.get('mail'):
            Employee_Mail = request.POST.get('mail')
            username = request.POST.get('username')
            latest_user = User.objects.latest('date_joined')
            last_user_id = int(latest_user.id) if latest_user else 1
            try:
                user = User.objects.get(username=username)
                if user.email != Employee_Mail:
                    error_message = 'Invalid username or email-id.'
                    logger.info('Employee entered invalid username or email')
                    return render(request, 'login.html',
                                  {'error_message': error_message})
            except User.DoesNotExist:
                logger.info('New employee details are entered '
                            'and saving into database')
                user = User.objects.create(id=last_user_id + 1,
                                           username=username,
                                           email=Employee_Mail)
                user.save()
            user_otp = User.objects.get(username=username)
            logger.info(f'Entered employee mail: {Employee_Mail}')
            otp = generate_otp()
            database = Otp()
            update_count = count + 1
            database.mail = Employee_Mail
            database.otp = otp
            database.user = user_otp
            database.count = update_count
            check = Otp.objects.filter(mail=database.mail)
            if check.count() > 0:
                cc_count = Otp.objects.filter(mail=database.mail).\
                    values_list('count', flat=True)
                new_count = list(cc_count)
                new_count1 = new_count[0]
                new_count2 = new_count1 + 1
                logger.warning(f'Previously employee attempted '
                               f'quiz for {new_count1} time')
                Otp.objects.filter(mail=database.mail).update(
                    otp=database.otp, user=database.user, count=new_count2)
                # check_count = Otp.objects.filter(mail=database.mail)\
                #     .values_list('count', flat=True)
                # time_entred = list(check_count)
                # time_count = time_entred[0]
                # if time_count > 3:
                #     logger.warning(
                #         f'Employee trying to login for '
                #         f'{time_count} times, so employee is restricted!')
                #     return render(request, 'restrict.html')
                # else:
                logger.info(f'Otp is sent to employee '
                            f'mail-id: {Employee_Mail}')

                send_mail(subject="OTP", message=f"Your otp {otp}",
                          from_email="switchingtechsystem@gmail.com",
                          recipient_list=[Employee_Mail],
                          fail_silently=False)
            else:
                logger.info(f'Otp is sent to employee '
                            f'mail-id: {Employee_Mail}')
                send_mail(subject="OTP", message=f"Your otp {otp}",
                          from_email="switchingtechsystem@gmail.com",
                          recipient_list=[Employee_Mail],
                          fail_silently=False)
                database.save()
            logger.info('Employee details are saved into database')
            logger.info('Employee is redirected to otp validation page!')
            return render(request, 'validate.html')
    else:
        # logger.error('Employee is not entered valid username or email-id')
        return render(request, 'login.html')


global mail


def validate(request):
    '''
    This method will validate the employee entered otp with their email.
    Once it is validated it will redirect to dashboard page
    '''
    logger.info('OTP validation is accessed!')
    if request.method == 'POST':
        mail = request.POST.get('mail')
        otp = request.POST.get('otp')
        request.session['mail'] = mail
        verified = Otp.objects.filter(mail=mail, otp=otp)
        if verified:
            logger.info('OTP is verified successfully')
            keep_signed_in = request.POST.get('remember_me', False) == 'on'
            logger.info(f'Employee checked keep me signed: {keep_signed_in}')
            user = User.objects.get(email=mail)
            if user is not None:
                login(request, user)
                logger.info('Employee logged-in successfully')
                request.session['username'] = user.username

                if keep_signed_in:
                    # Set session expiration to None
                    request.session.set_expiry(None)
                    request.session['remember_me'] = True
                return redirect('dashboard/')
        else:
            logger.info('Otp is invalid and redirect to login page')
            error_message = 'Invalid OTP. Please try again.'
            return render(request, 'validate.html',
                          {'error_message': error_message})


def dashboard(request):
    '''
    This is the dashboard method where it will
    calculate employee overall progress and generate categories
    '''
    logger.info('Dashboard page is accessed!')
    mail = request.session.get('mail')
    user = User.objects.get(email=mail)
    overall_progress = PlayerActivity.objects.filter(user=user).order_by(
        '-id').values_list('percentage', 'category')[:3]

    if overall_progress:
        percentages, categories = zip(*overall_progress)
        list_overall_progress = list(percentages)
        list_overall_categories = list(categories)
        rounded_progress = [round(value, 2) for value in list_overall_progress]
        sum_overall_progress = sum(rounded_progress)
        logger.info(f'Employee overall Progress: {sum_overall_progress} %')
        context = {
            'categories': Category.objects.all(),
            'list_overall_progress': rounded_progress,
            'list_categories': list_overall_categories,
            'overall_progress': sum_overall_progress
        }
        logger.info('Dashboard page is accessed')
        print(context)
        return render(request, 'dashboard.html', context)
    else:
        # Handle the case when no progress data is available
        logger.info('No progress data found')
        context = {
            'categories': Category.objects.all(),
            'list_overall_progress': [],
            'list_categories': [],
            'overall_progress': 0
        }
        return render(request, 'dashboard.html', context)


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
            logger.info(f'Suggested udemy course: {course_name}')
            break
        for v_id in suggestion_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            logger.info(f'Suggested youtube course: {Title}')
            logger.info(f'Youtube ID: {YouTube_id}')
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
def history(request):
    '''
    This method will display the employee previous quiz attempt history
    '''
    logger.info('History page is accessed!')
    mail = request.session.get('mail')
    user = User.objects.get(email=mail)
    score_details = QuizUserScore.objects.filter(
        user=user).order_by('-created_at').values_list(
        'score', 'created_at', 'quiz_domain')[:3]
    user_history = list(score_details)
    if user_history:
        logger.info('Employee previous quiz history present')
        attempts_data = []

        for score, user_time, user_domain in user_history:
            logger.info(f'Employee previous quiz score: {score}')
            user_time = timezone.localtime(
                user_time, timezone=pytz.timezone('Asia/Kolkata'))
            logger.info(f'Employee previous quiz attempt date: {user_time}')
            logger.info(f'Employee previous attempted '
                        f'quiz domain: {user_domain}')

            suggesstion_url, course_name, ratings, \
                instructor, duration, difficulty, \
                YouTube_id, Title = url(score, category=user_domain)

            attempt_data = {
                'user_score': score,
                'user_time': user_time,
                'previous_domain': user_domain,
                'suggestion_url': suggesstion_url,
                'course_name': course_name,
                'ratings': ratings,
                'instructor': instructor,
                'duration': duration,
                'difficulty': difficulty,
                'title': Title
            }
            attempts_data.append(attempt_data)

        return render(request, 'history.html',
                      context={'attempts_data': attempts_data})
    else:
        logger.info('Employee previous quiz history is not present')
        data = {
            'no_data': True  # Add a flag to indicate no data
        }
        return render(request, 'history.html', context=data)


def user_logout(request):
    '''
    In this method user will be logout and clear all employee sessions
    '''
    logout(request)
    logger.info('Employee is logged-out successfully!')
    request.session.flush()
    return redirect('/')


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
            new_timer = 60
    else:
        new_timer = 60
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

        print(current_time)
        print(youtube_id)
        print(percentage)
        print(selectedcategory)

        if current_time is None:
            current_time = 0  # Assign a numeric default value

        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        check = PlayerActivity.objects.filter(youtube_id=youtube_id, user=user)
        print(check)
        if check:
            PlayerActivity.objects.filter(
                user=user, youtube_id=youtube_id).update(
                current_time=current_time, percentage=percentage)
            print('inside check')
        # player_activity.current_time = current_time
        # player_activity.percentage = percentage
        # player_activity.save()
        else:
            print('its else')
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


def my_learning(request):
    '''
    This method redirects to my learning page,
    here we can see employee suggested courses.
    '''
    logger.info('My Learning page accessed!')
    mail = request.session.get('mail')
    user = User.objects.get(email=mail)
    retrieve_time = PlayerActivity.objects.filter(
        user=user).order_by('-id').values_list('current_time', 'youtube_id')[0:3]
    resume = list(retrieve_time)
    if resume:
        logger.info('Learning modules are present')
        data = {
            'videos': [{'youtube_id': item[1],
                        'resume_time': item[0]} for item in resume]
        }

        return render(request, 'mylearning.html', context=data)
    else:
        logger.info('Employee doesnt have any learning as of now')
        data = {
            'no_data': True  # Add a flag to indicate no data
        }
        return render(request, 'mylearning.html', context=data)
