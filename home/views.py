import json
from django.shortcuts import render,redirect,get_object_or_404
from django.http import request, HttpResponse,JsonResponse,response
from django.contrib.auth import login, logout, authenticate
from .forms import *
from .models import *
import random
import math
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail


def generate_otp():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


count = 0
def loginPage(request):
    print("yes")
    if request.method == "POST":
        if request.POST.get('mail'):
            Employee_Mail = request.POST.get('mail')
            username = request.POST.get('username')
            print(Employee_Mail)
            # return render(request,'index.html')
            otp = generate_otp()
            print("otp:",otp)
            database = Otp()
            update_count = count + 1
            send_mail(subject="OTP",message= f"Your otp {otp}",from_email="switchingtechsystem@gmail.com",recipient_list=[Employee_Mail],fail_silently=False)
            database.mail = Employee_Mail
            database.otp = otp
            database.username = username
            database.count = update_count
            check = Otp.objects.filter(mail=database.mail)
            if check.count() > 0:
                cc_count = Otp.objects.filter(mail=database.mail).values_list('count', flat=True)
                new_count = list(cc_count)
                new_count1 = new_count[0]
                new_count2 = new_count1 + 1
                print('--------->',new_count2)
                Otp.objects.filter(mail=database.mail).update(otp=database.otp,username=database.username, count=new_count2)
                check_count = Otp.objects.filter(mail=database.mail).values_list('count', flat=True)
                time_entred = list(check_count)
                time_hours = time_entred[0]
                print(time_hours)
                if time_hours > 30:
                    return render(request, 'restrict.html')
            else:
                database.save()
            return render(request, 'validate.html')
    else:
        return render(request,'login.html')

global mail
def validate(request):
    context = {'categories': Category.objects.all()}
    if request.GET.get('category'):
        return redirect(f"/quiz/?category={request.GET.get('category')}")

    if request.method == 'POST':
        mail = request.POST.get('mail')
        otp = request.POST.get('otp')
        print('validate:', mail)
        print('validate:', otp)
        sc = Otp.objects.filter(mail=mail, otp=otp)
        if sc:
            # return redirect('home')
            request.session['mail'] = mail
            return render(request, 'index.html', context)
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')
    

def url(score, category):
    if score <= 50:
        print("Suggesting Begginer")
        suggesstion = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='BG')

        for val in suggesstion:
            print('value------------->',val)
            suggesstion_url = val  
            course_name = val.course_name
            ratings= val.ratings
            instructor=val.course_instructor
            duration=val.course_duration
            difficulty=val.difficulty

            break     
    elif 50 < score <= 70:
    # elif score>50 and score<80:
        print("Suggesting Intermediate")
        suggesstion = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='IN')
        for val in suggesstion:
            suggesstion_url = val 
            course_name = val.course_name
            ratings= val.ratings
            instructor=val.course_instructor
            duration=val.course_duration
            difficulty=val.difficulty
            
            break       
    elif score > 70 <= 100:
        print("Suggesting Advanced!")
        suggesstion  = CourseSuggession.objects.filter(technology__category_name__icontains=category, difficulty='AD')
        for val in suggesstion:
            suggesstion_url = val  
            course_name = val.course_name
            ratings= val.ratings
            instructor=val.course_instructor
            duration=val.course_duration
            difficulty=val.difficulty
            break
    return suggesstion_url, course_name, ratings, instructor, duration, difficulty

def history(request):
    mail = request.session.get('mail')
    print('MAIL in HISTORY:---->',mail)
    username = Otp.objects.filter(mail=mail).values_list('id', flat=True)
    print(username)
    new = list(username)
    print("check us:", new)
    update = new[0]
    score_details = QuizUserScore.objects.filter(user=update).values_list('score', 'created_at', 'quiz_domain')
    user_history = list(score_details)
    if user_history:
        score = user_history[0][0]
        user_time = user_history[0][1]
        user_domain = user_history[0][2]
        print('user_remaining_score:----->', score)
        print('user_last_timer:---->', user_time)
        print("last_domain---->", user_domain)
        
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
        print("no history")
        return JsonResponse({'message': 'No history'})

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
    return render(request,'index.html',context)
    


def quiz(request):
    mail = request.session.get('mail')
    username = Otp.objects.filter(mail=mail).values_list('id', flat=True)
    new = list(username)
    print("check us:", new)
    update = new[0]
    time_remaining = QuizAttempt.objects.filter(id=update).values_list('timer', 'domain')
    if time_remaining :
        print('timer_remaining--->', time_remaining)
        rem_time = list(time_remaining)
        print('rem_timer---->', rem_time)
        update_timer = rem_time[0][0]
        print('updated_timer_db--------->', update_timer)
        if request.GET.get('category') == rem_time[0][1] and rem_time[0][0] > 5:
            new_timer = update_timer
        else:
            new_timer = 60
    else:
        new_timer = 60
    context = {'category': request.GET.get('category'), 'new_timer': new_timer}
    print(context)
    return render(request,'quiz.html',context)

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
            counter+=1
            if counter < 11:
                data.append({
                    "uid":question_obj.uid,
                    "category" : question_obj.category.category_name,
                    "question": question_obj.question,
                    "marks" : question_obj.marks,
                    "time": request.POST.get('timer'),
                    "answers": question_obj.get_answers()
                })
        return JsonResponse({'data': data,'status': True})
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
        if form.is_valid(): ## Will only ensure the option exists, not correctness.
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
        # quiz_timer = QuizAttempt.objects.create(timer=remaining_time)
        quiz_timer.timer = remaining_time
        quiz_timer.id = update
        quiz_timer.domain = category
        quiz_timer.save()
        return JsonResponse({'message': 'Remaining time saved successfully'})

    return JsonResponse({'message': 'Invalid request method'}, status=400)


score = 0
suggesstion_url = str()
course_name=str()
ratings = 0
instructor=str()
duration=float()
difficulty=str()
def result(request):
    if request.method == 'POST':
        quiz_add = QuizUserScore()
        global score, suggesstion_url,course_name,ratings,duration,instructor,difficulty
        # username = User.objects.filter(id= request.user.id).values_list('username',flat=True)
        mail = request.session.get('mail')
        username = Otp.objects.filter(mail=mail).values_list('id',flat=True)
        new = list(username)
        print("check us:",new)
        update = new[0]

        score_data = json.loads(request.body)
        score = score_data.get('score')
        
        category = score_data.get('category')
        quiz_add.quiz_domain = category
        quiz_add.score = score*10
        quiz_add.user = update

        check = QuizUserScore.objects.filter(user=quiz_add.user)
        if check.count() > 0:
            QuizUserScore.objects.filter(user=quiz_add.user).update(created_at=datetime.now(), score=quiz_add.score, quiz_domain=quiz_add.quiz_domain)
        else:
            quiz_add.save()
        print('Score received:', score * 10,'category:',category)

        suggesstion_url, course_name, ratings, instructor, duration, difficulty = url(score=quiz_add.score, category=category)


        context = {'score': score,
                   'url':suggesstion_url,
				   'course_name':course_name,
                   'ratings' :ratings,
                   'duration':duration,
                   'instructor': instructor,
                   'difficulty': difficulty}
        
        return HttpResponse(status=200)



def skip_quiz(request):
    selected_category = request.GET.get('category')
    context = {}
    if selected_category:
        suggestions = CourseSuggession.objects.filter(technology__category_name__icontains=selected_category)
        context['suggestions'] = suggestions

    return render(request, 'skipquiz.html', context)

def final(request):
    context = {
        "score":score * 10, 'suggested':suggesstion_url, 'course_name': course_name ,'ratings':ratings,'duration':duration,
          'instructor':instructor,'difficulty':difficulty  }
    return render(request,'results.html',context=context)

