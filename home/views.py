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
    print('^^^^^^^^',remember_me)
    if remember_me:
        logger.info('User session exists (remember me enabled), redirecting to the Instructions page')
        context = {'categories': Category.objects.all()}
        if request.GET.get('category'):
            return redirect(f"/quiz/?category={request.GET.get('category')}")
        return render(request, 'index.html', context)

    # if request.user.is_authenticated:
    #     logger.info('User session is exists redirecting to Instructions page')
    #     context = {'categories': Category.objects.all()}
    #     print(context)
    #     if request.GET.get('category'):
    #         return redirect(f"/quiz/?category={request.GET.get('category')}")
    #     return render(request, 'index.html', context)

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
            print('---------',keep_signed_in)
            print('mail',mail)
            user = User.objects.get(email=mail)
            print(user)
            # user = KeepMeSignedInBackend().authenticate(request, otp=otp)
            print('-----------',user)

            if user is not None:
                login(request, user)
                request.session['username'] = user.username

                # set persistent session or cookie if "Keep me signed in" is checked
                if keep_signed_in:
                    request.session.set_expiry(86400 * 30)  # set session expiration time (e.g., 30 days)
                    request.session['remember_me'] = True
                return redirect('homepage/')
        else:
            logger.info('Otp is invalid and redirect to login page')
            return render(request, 'login.html')


        

def homepage(request):
    context = {'categories': Category.objects.all()}
    if request.GET.get('category'):
        return redirect(f"/quiz/?category={request.GET.get('category')}")
    return render(request, 'index.html', context)


def url(score, category):
    if score <= 50:
        print("Suggesting Beginner")
        logger.info('Based on employee score we are suggesting Beginner course')
        suggesstion = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='BG')
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

    elif 50 < score <= 70:
        # elif score>50 and score<80:
        print("Suggesting Intermediate")
        logger.info('Based on employee score we are suggesting Intermediate course')
        suggesstion = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='IN')
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

    elif score > 70 <= 100:
        print("Suggesting Advanced!")
        logger.info('Based on employee score we are suggesting Advanced course')
        suggesstion = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='AD')
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

    return suggesstion_url, course_name, ratings, instructor, duration, difficulty


def history(request):
    mail = request.session.get('mail')
    print('MAIL in HISTORY:---->', mail)
    # username = Otp.objects.filter(mail=mail).values_list('id', flat=True)
    # new = list(username)
    # print("Employee ID :", new)
    # update = new[0]
    user = User.objects.get(email=mail)
    score_details = QuizUserScore.objects.filter(user=user).values_list('score', 'created_at', 'quiz_domain')
    user_history = list(score_details)
    if user_history:
        logger.info('Employee previous quiz history present')
        score = user_history[0][0]
        user_time = user_history[0][1]
        user_domain = user_history[0][2]
        print('employee_previous_score:----->', score)
        logger.info(f'Employee previous quiz score : {score}')
        print('user_last_timer:---->', user_time)
        logger.info(f'Employee previous quiz attempt date {user_time}')
        print("last_domain---->", user_domain)
        logger.info(f'Employee previous attempted quiz domain {user_domain}')

        suggesstion_url, course_name, ratings, instructor, duration, difficulty = url(score, category=user_domain)

        data = {
            'user_score': score,
            'user_time': user_time,
            'previous_domain': user_domain,
            'suggestion_url': suggesstion_url,
            'course_name': course_name,
            'ratings': ratings,
            'instructor': instructor,
            'duration': duration,
            'difficulty': difficulty
        }

        return render(request, 'history.html', context=data)
    else:
        logger.info('Employee previous quiz history is not present')
        print("no history")
        data = {
            'no_data': True  # Add a flag to indicate no data
        }
        return render(request, 'history.html', context=data)


def logoutPage(request):
    logout(request)
    response = redirect('app.home.views.home')
    response.delete_cookie('user_location')
    return redirect('login')


@login_required(login_url='login')
def home(request):
    context = {'categories': Category.objects.all()}
    if request.GET.get('category'):
        return redirect(f"/quiz/?category={request.GET.get('category')}")
    return render(request, 'index.html', context)


def quiz(request):
    mail = request.session.get('mail')
    username = Otp.objects.filter(mail=mail).values_list('id', flat=True)
    new = list(username)
    print("Employee Id:", new)
    update = new[0]
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


def save_remaining_time(request):
    if request.method == 'POST':
        remaining_time = request.POST.get('remainingTime')
        category = request.POST.get('category')
        print('timer_value_js----------->', remaining_time)
        quiz_timer = QuizAttempt()
        mail = request.session.get('mail')
        username = Otp.objects.filter(mail=mail).values_list('id', flat=True)
        new = list(username)
        print("check us:", new)
        update = new[0]
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
def result(request):
    if request.method == 'POST':
        quiz_add = QuizUserScore()
        global score, suggesstion_url, course_name, ratings, duration, instructor, difficulty
        mail = request.session.get('mail')
        username = Otp.objects.filter(mail=mail).values_list('id', flat=True)
        new = list(username)
        print("check us:", new)
        update = new[0]
        user = User.objects.get(email=mail)
        score_data = json.loads(request.body)
        score = score_data.get('score')
        category = score_data.get('category')
        quiz_add.quiz_domain = category
        quiz_add.score = score * 10
        quiz_add.user = user
        check = QuizUserScore.objects.filter(user=user)
        if check.count() > 0:
            QuizUserScore.objects.filter(user=user).update(created_at=datetime.now(), score=quiz_add.score,
                                                                    quiz_domain=quiz_add.quiz_domain)
        else:
            quiz_add.save()
        print('Score received:', score * 10, 'category:', category)
        suggesstion_url, course_name, ratings, instructor, duration, difficulty = url(score=quiz_add.score,
                                                                                      category=category)
        logger.info(f'Based on quiz attempt employee got {score * 10} score')
        return HttpResponse(status=200)


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


def final(request):
    context = {
        "score": score * 10, 'suggested': suggesstion_url, 'course_name': course_name, 'ratings': ratings,
        'duration': duration,
        'instructor': instructor, 'difficulty': difficulty}
    logger.info(f'Employee submitted quiz and redirect to results page with course suggestion')
    return render(request, 'results.html', context=context)
