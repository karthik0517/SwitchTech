import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import request, HttpResponse, JsonResponse, response
from django.contrib.auth import login, logout, authenticate
from .forms import *
from .models import *
import random
import math
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import logging
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings
from django.db import IntegrityError
import pytz
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_otp():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    logger.info(f'OTP is generated {OTP}')
    return OTP


count = 0
def loginPage(request):
    remember_me = request.session.get('remember_me', False)
    print('------->', remember_me)
    if remember_me:
        # logger.info('User session exists (remember me enabled), redirecting to the Instructions page')
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        overall_progress = PlayerActivity.objects.filter(user=user).values_list('percentage', flat=True)
        list_overall_progress = list(overall_progress)
        sum_overall_progress = sum(list_overall_progress)
        print('sum_overall', sum_overall_progress)
        formatted_progress = round(sum_overall_progress, 2)
        print('overall_progress',formatted_progress)
        context = {'categories': Category.objects.all(), 'overall_progress':formatted_progress}
        return render(request, 'dashboard.html',context)

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
                    return render(request, 'login.html', {'error_message': error_message})
            except User.DoesNotExist:
                user = User.objects.create(id=last_user_id + 1, username=username, email=Employee_Mail)
                user.save()
                # Additional logic for newly created user if needed
            user_otp = User.objects.get(username=username)
            print(Employee_Mail)
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
                cc_count = Otp.objects.filter(mail=database.mail).values_list('count', flat=True)
                new_count = list(cc_count)
                new_count1 = new_count[0]
                new_count2 = new_count1 + 1
                print('--------->', new_count2)
                logger.warning(f'Previously employee attempted quiz for {new_count1} time')
                Otp.objects.filter(mail=database.mail).update(otp=database.otp, user=database.user,
                                                              count=new_count2)
                # check_count = Otp.objects.filter(mail=database.mail).values_list('count', flat=True)
                # time_entred = list(check_count)
                # time_hours = time_entred[0]
                # print(time_hours)
                # if time_hours > 30:
                #     logger.warning(f'Employee trying to login for {time_hours} times, so employee is restricted!')
                #     return render(request, 'restrict.html')
                # else:
                logger.info(f'Employee having login attempts and otp is sent to employee mail-id: {Employee_Mail}')
                print("otp:", otp)
                send_mail(subject="OTP", message=f"Your otp {otp}", from_email="switchingtechsystem@gmail.com",
                          recipient_list=[Employee_Mail], fail_silently=False)
            else:
                logger.info(f'Employee having login attempts and otp is sent to employee mail-id: {Employee_Mail}')
                print("otp:", otp)
                send_mail(subject="OTP", message=f"Your otp {otp}", from_email="switchingtechsystem@gmail.com",
                          recipient_list=[Employee_Mail], fail_silently=False)
                database.save()
            logger.info('Employee details are saved into database')
            logger.info('Employee is redirected to otp validation page!')
            return render(request, 'validate.html')
    else:
        # logger.error('Employee is not entered valid username or email-id')
        return render(request, 'login.html')


global mail
def validate(request):
    if request.method == 'POST':
        mail = request.POST.get('mail')
        otp = request.POST.get('otp')
        print('validate:', mail)
        print('validate:', otp)
        request.session['mail'] = mail
        verified = Otp.objects.filter(mail=mail, otp=otp)
        if verified:
            keep_signed_in = request.POST.get('remember_me', False) == 'on'
            # keep_signed_in = request.POST.get('remember_me', False) = 'True'
            print('---------', keep_signed_in)
            print('mail', mail)
            user = User.objects.get(email=mail)
            print(user)
            # user = KeepMeSignedInBackend().authenticate(request, otp=otp)
            if user is not None:
                login(request, user)
                request.session['username'] = user.username

                # set persistent session or cookie if "Keep me signed in" is checked
                if keep_signed_in:
                    # request.session.set_expiry(86400 * 30)  # set session expiration time (e.g., 30 days)
                    request.session.set_expiry(None)  # Set session expiration to None
                    request.session['remember_me'] = True

                print('Session mail:', request.session.get('mail'))
                print('Session remember_me:', request.session.get('remember_me'))
                print('Session username:', request.session.get('username'))
                # Debug code: Print request headers
                print('Request headers:', request.headers)
                # Debug code: Print session cookie
                session_cookie = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
                print('Session cookie:', session_cookie)
                return redirect('dashboard/')
                # return redirect('homepage/')
                # return redirect('homepage/')
        else:
            logger.info('Otp is invalid and redirect to login page')
            error_message = 'Invalid OTP. Please try again.'
            return render(request, 'validate.html', {'error_message': error_message})


def dashboard(request):
    mail = request.session.get('mail')
    user = User.objects.get(email=mail)
    overall_progress = PlayerActivity.objects.filter(user=user).values_list('percentage', flat=True)
    list_overall_progress = list(overall_progress)
    sum_overall_progress = sum(list_overall_progress)
    formatted_progress = round(sum_overall_progress, 2)
    print('overall_progress', formatted_progress)
    context = {'categories': Category.objects.all(), 'overall_progress':formatted_progress}
    return render(request, 'dashboard.html', context)


def index(request):
    return render(request, 'index.html')


def homepage(request):
    context = {'categories': Category.objects.all()}
    if request.GET.get('category'):
        return redirect(f"/quiz/?category={request.GET.get('category')}")
    return render(request, 'index.html', context)


def url(score, category):
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
        print("Suggesting Beginner")
        logger.info('Based on employee score we are suggesting Beginner course')
        suggesstion = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='BG')
        suggestion_vdo = Video.objects.filter(technology_v__category_name__icontains=category, difficulty='BG')
        for val in suggesstion:
            print('value------------->', val)
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            break
        for v_id in suggestion_vdo:
            print('-------->', v_id)
            YouTube_id = v_id.video_id
            Title = v_id.title
            print('----------', YouTube_id)
            break

    elif 50 < score <= 70:
        # elif score>50 and score<80:
        print("Suggesting Intermediate")
        logger.info('Based on employee score we are suggesting Intermediate course')
        suggesstion = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='IN')
        suggestion_vdo = Video.objects.filter(technology_v__category_name__icontains=category, difficulty='IN')
        for val in suggesstion:
            print('value------------->', val)
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            break
        for v_id in suggestion_vdo:
            print('-------->', v_id)
            YouTube_id = v_id.video_id
            Title = v_id.title
            print('----------', YouTube_id)
            break

    elif score > 70 <= 100:
        print("Suggesting Advanced!")
        logger.info('Based on employee score we are suggesting Advanced course')
        suggesstion = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='AD')
        suggesst_vdo = Video.objects.filter(technology_v__category_name__icontains=category, difficulty='AD')
        print(suggesst_vdo)
        for val in suggesstion:
            print('value------------->', val)
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            break
        for v_id in suggesst_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            break

    return suggesstion_url, course_name, ratings, instructor, duration, difficulty, YouTube_id, Title


@login_required(login_url='login')
def history(request):
    mail = request.session.get('mail')
    print('MAIL in HISTORY:---->', mail)
    user = User.objects.get(email=mail)
    score_details = QuizUserScore.objects.filter(user=user).order_by('-created_at').values_list('score', 'created_at', 'quiz_domain')[:3]
    print('score_details', score_details)
    user_history = list(score_details)
    print('user_history', user_history)
    if user_history:
        logger.info('Employee previous quiz history present')
        attempts_data = []

        for score, user_time, user_domain in user_history:
            print('employee_previous_score:----->', score)
            logger.info(f'Employee previous quiz score: {score}')
            print('user_last_timer:---->', user_time)
            user_time = timezone.localtime(user_time, timezone=pytz.timezone('Asia/Kolkata'))
            logger.info(f'Employee previous quiz attempt date: {user_time}')
            print("last_domain---->", user_domain)
            logger.info(f'Employee previous attempted quiz domain: {user_domain}')

            suggesstion_url, course_name, ratings, instructor, duration, difficulty, YouTube_id, Title = url(score,
                                                                                                             category=user_domain)

            # Create a dictionary for each attempt and append it to the attempts_data list
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

        print('history data', attempts_data)
        return render(request, 'history.html', context={'attempts_data': attempts_data})
    else:
        logger.info('Employee previous quiz history is not present')
        print("no history")
        data = {
            'no_data': True  # Add a flag to indicate no data
        }
        return render(request, 'history.html', context=data)


def logout(request):
    request.session.flush()
    return redirect('/')


@login_required(login_url='login')
def quiz(request):
    mail = request.session.get('mail')
    user = User.objects.get(email=mail)
    time_remaining = QuizAttempt.objects.filter(user=user).values_list('timer', 'domain')
    if time_remaining:
        # print('timer_remaining--->', time_remaining)
        rem_time = list(time_remaining)
        # print('rem_timer---->', rem_time)
        update_timer = rem_time[0][0]
        logger.info(f'Employee still having the previous quiz timer with {update_timer} sec')
        print('updated_timer_db--------->', update_timer)
        if request.GET.get('category') == rem_time[0][1] and rem_time[0][0] > 5:
            new_timer = update_timer
        else:
            new_timer = 60
    else:
        new_timer = 60
    context = {'category': request.GET.get('category'), 'new_timer': new_timer}
    print(context)
    logger.info(
        'Employee agreed to terms and conditions with selected domain {} and timer will starts from {} seconds, redirecting to quiz page'.format(
            request.GET.get('category'), new_timer))
    return render(request, 'quiz.html', context)


@login_required(login_url='login')
def get_quiz(request):
    try:
        questions_objs = Question.objects.all()
        if request.GET.get('category'):
            questions_objs = questions_objs.filter(category__category_name__icontains=request.GET.get('category'))
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
        print(e)
    return HttpResponse("Something went worng")


@login_required(login_url='login')
def render_quiz(request, quiz_id):
    # quiz = get_object_or_404(Quiz, quiz_id)
    # form = QuizForm(questions=quiz.question_set.all())
    form = Question.objects.all()
    print(questions_objs)
    if request.GET.get('category'):
        questions_objs = questions_objs.filter(category__category_name__icontains=request.GET.get('category'))
    questions_objs = list(questions_objs)
    data = []
    random.shuffle(questions_objs)
    if request.method == "POST":
        form = QuizForm(request.POST, questions=quiz.question_set.all())
        if form.is_valid():  ## Will only ensure the option exists, not correctness.
            attempt = form.save()
            return redirect(attempt)
    return render('quiz.html', {"form": form})


@login_required(login_url='login')
def save_remaining_time(request):
    if request.method == 'POST':
        remaining_time = request.POST.get('remainingTime')
        category = request.POST.get('category')
        print('timer_value_js----------->', remaining_time)
        quiz_timer = QuizAttempt()
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        quiz_timer.timer = remaining_time
        # quiz_timer.id = update
        quiz_timer.user = user
        quiz_timer.domain = category
        quiz_timer.save()
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
    if request.method == 'POST':
        quiz_add = QuizUserScore()
        global score, suggesstion_url, course_name, ratings, duration, instructor, difficulty, YouTube_id, Title
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
        # check = QuizUserScore.objects.filter(user=user)

        # if check.count() > 0:
        #     QuizUserScore.objects.filter(user=user).update(created_at=datetime.now(), score=quiz_add.score,
        #                                                    quiz_domain=quiz_add.quiz_domain)
        # else:
        quiz_add.save()
        print('Score received:', score * 10, 'category:', category)
        suggesstion_url, course_name, ratings, instructor, duration, difficulty, YouTube_id, Title = url(
            score=quiz_add.score,
            category=category)
        logger.info(f'Based on quiz attempt employee got {score * 10} score')
        return HttpResponse(status=200)


@login_required(login_url='login')
def skip_quiz(request):
    selected_category = request.GET.get('category')
    context = {}
    if selected_category:
        suggestions = CourseSuggession.objects.filter(technology__category_name__icontains=selected_category)
        context['suggestions'] = suggestions
    logger.info(
        'Employee skipped the quiz and select domain {} and redirected to all recomendations page with all the avaliable courses'.format(
            request.GET.get('category')))
    return render(request, 'skipquiz.html', context)


@login_required(login_url='login')
def final(request):
    context = {
        "score": score * 10, 'suggested': suggesstion_url, 'course_name': course_name, 'ratings': ratings,
        'duration': duration, 'instructor': instructor, 'difficulty': difficulty, 'YouTube_id': YouTube_id,
        'title': Title}
    logger.info(f'Employee submitted quiz and redirect to results page with course suggestion')
    return render(request, 'results.html', context=context)


@csrf_exempt
def save_time(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        current_time = data.get('current_time')
        youtube_id = data.get('youtube_id')
        percentage = data.get('percentage')
        print("percentage==================", percentage)
        if current_time is None:
            current_time = 0  # Assign a numeric default value
        try:
            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
            player_activity = PlayerActivity.objects.filter(youtube_id=youtube_id, user=user).latest('id')
            player_activity.current_time = current_time
            player_activity.percentage = percentage
            player_activity.save()
            return JsonResponse({'message': 'Time saved successfully'})

        except PlayerActivity.DoesNotExist:
            PlayerActivity.objects.create(current_time=current_time, percentage=percentage, youtube_id=youtube_id, user=user)
            return JsonResponse({'message': 'Time saved successfully'})
        except IntegrityError as e:
            print(f"Error saving time: {str(e)}")
            return JsonResponse({'message': 'Error saving time'}, status=500)
    else:
        return HttpResponseBadRequest('Invalid request method')
        

def my_learning(request):
    mail = request.session.get('mail')
    print('MAIL in Mylearning:---->', mail)
    user = User.objects.get(email=mail)
    retrieve_time = PlayerActivity.objects.filter(user=user).values_list('current_time','youtube_id')[0:3]
    resume = list(retrieve_time)
    if resume:
        print('checking',resume)
        data = {
            'videos': [{'youtube_id': item[1], 'resume_time': item[0]} for item in resume]
        }

        return render(request, 'mylearning.html', context=data)
    else:
        logger.info('Employee doesnt have any learning as of now')
        print("no my learning")
        data = {
            'no_data': True  # Add a flag to indicate no data
        }
        return render(request, 'mylearning.html',context=data)
    
