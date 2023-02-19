from django.shortcuts import render
import pyrebase

# pyrebase
config = {
  "apiKey": "AIzaSyBW2NgwNMEnPQEJeUyQeNdKHLJIHqJfarA",
  "authDomain": "django-practice-7c129.firebaseapp.com",
  "projectId": "django-practice-7c129",
  "storageBucket": "django-practice-7c129.appspot.com",
  "messagingSenderId": "558203147786",
  "appId": "1:558203147786:web:8d81879b63b3eaa19e31f3",
  "databaseURL":"https://django-practice-7c129-default-rtdb.firebaseio.com/"
}

# here we are doing firebase authentication
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()


def firebase_test(request):
        #accessing our firebase data and storing it in a variable
        name = database.child('Data').child('Name').get().val()
        framework = database.child('Data').child('Framework').get().val()
    
        context = {
            'name':name,
            'framework':framework
        }
        return render(request, 'blog/firebase_test.html', context)

def signIn(request):
    return render(request,"blog/login.html")
def home(request):
    return render(request,"Home.html")
 
def postsignIn(request):
    email=request.POST.get('email')
    pasw=request.POST.get('pass')
    try:
        # if there is no error then signin the user with given email and password
        user=authe.sign_in_with_email_and_password(email,pasw)
    except:
        message="Invalid Credentials!!Please ChecK your Data"
        return render(request,"Login.html",{"message":message})
    session_id=user['idToken']
    request.session['uid']=str(session_id)
    return render(request,"home.html",{"email":email})
 
def logout(request):
    try:
        del request.session['uid']
    except:
        pass
    return render(request,"Login.html")
 
def signUp(request):
    return render(request,"registration.html")
 
def postsignUp(request):
     email = request.POST.get('email')
     passs = request.POST.get('pass')
     name = request.POST.get('name')
     try:
        # creating a user with the given email and password
        user=authe.create_user_with_email_and_password(email,passs)
        uid = user['localId']
        idtoken = request.session['uid']
        print(uid)
     except:
        return render(request, "Registration.html")
     return render(request,"Login.html")