from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from items.models import Item
from django.core.mail import send_mail

from datetime import date
import datetime
# Create your views here.
def login(request):
    if request.method == 'POST':
        uname = request.POST.get('un','')
        pass1 = request.POST.get('pa','')
        user = auth.authenticate(username=uname,password=pass1)

        if user == None:
            messages.info(request,"invalid username/password")
            return redirect('login')
        else:
            auth.login(request,user)
            return redirect("home")
            
    else:
        return render(request,'login.html')


def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        mail = request.POST['email']
        p1 = request.POST['p1']
        p2 = request.POST['p2']
        if p1 == p2:
            if User.objects.filter(email=mail).exists():
                messages.info(request,"Already an User with this Email")
                return redirect('register')
            elif User.objects.filter(username=name).exists():
                messages.info(request,"Already an User with this Username")
                return redirect('register')
            else:
                user = User.objects.create_user(email=mail,password=p1,username=name)
                user.save()
                subject = "Online Bidding"  
                msg     = "Congratulations you are registered successfully."
                to      = mail  
                res     = send_mail(subject, msg, "bidmafia007@gmail.com", [to])
                if res == 1:
                    return redirect('/')
                else:
                    messages.info(request,"Some thing is wrong")
                    return redirect('register')
        else:
            messages.info(request,"Password does not match")
            return redirect('register')
    else:
        return render(request,'register.html')




def forgotpassword(request):
     return render(request,'forgot.html')


def sendMailTowinners(request):
    today = date.today()
    yesterday = today - datetime.timedelta(days=1) 
    item = Item.objects.filter(start_date=yesterday).filter(sold="sold").filter(sendwinmail="unsended")
    for i in item :
        # print("1")
        try:
            # print("2")
            winnerid = i.highest_bidder
            print(winnerid)
            user_obj = User.objects.get(id=winnerid)
            winnermail = user_obj.email
            # print(winnermail)

            subject = "Online Bidding"  
            msg     = "Congratulations you are winner of item"+i.name+", Seller id is "+i.ownermail+"  contact him for further informations Thank You :)"
            to      = winnermail  
            res     = send_mail(subject, msg, "bidmafia007@gmail.com", [to])
            if res ==1:
                print ("mail sended to winner")
            else:
                print("something wrong for sending mail to winner")
            subject = "Online Bidding"  
            msg     = "Congratulations your item "+i.name+"'s higgest bidder is "+winnermail+",contact him for further informations Thank You :)"
            to      = i.ownermail  
            res     = send_mail(subject, msg, "bidmafia007@gmail.com", [to])
            if res ==1:
                print ("mail sended to seller")
            else:
                print("something wrong for sending mail to seller")
            i.sendwinmail="sended"
            i.save()
        except:
            pass
    # print("aa")

def pastConfigurations(request):
    # cuser =request.user
    # cmail = cuser.email
    # item = Item.objects.filter(ownermail=cmail)
    item = Item.objects.all()
    for i in item:
        try:
            hb = i.highest_bidder
            if hb is not None:
                i.sold="sold"
                i.save()
            else:
                i.sold="unsold"
                i.save()
        except:
            pass
    # print("hy")

@login_required(login_url='login')
def home(request):
    items = Item.objects.all()
    today = date.today()
    yesterday = today - datetime.timedelta(days=1) 
    # print(today)
    # print(yesterday)    
    for i in items:
        # print (i.start_date)
        if(today > i.start_date):
            i.status = "past"
            # print("past")
        if(today < i.start_date):
            i.status="future"
            # print("future")
        if(today == i.start_date):
            i.status="live"
            # print("live")
        i.save()
        # print("-------")
    pastConfigurations(request)
    sendMailTowinners(request)
    items = Item.objects.filter(status="live")
    return render(request,"home.html",{'items':items})
    
def logout(request):
    auth.logout(request)
    return redirect("login") 

def ilogout(request):
    auth.logout(request)
    return redirect("login") 

def myprofile(request):
    bidder = request.user
    # item_obj = Item.objects.get(highest_bidder=bidder.id)
    details = bidder   
    # ,"item_obj":item_obj
    return render(request,"myprofile.html",{"details":details})

def log(request):
    cuser =request.user
    cmail = cuser.email
    cid = cuser.id
    item_obj = Item.objects.filter(highest_bidder=cid)

    biddeditem = item_obj
    # item = Item.objects.filter(ownermail=cmail)
    pitem = Item.objects.filter(ownermail=cmail).filter(status="past") 
    litem = Item.objects.filter(ownermail=cmail).filter(status="live") 
    fitem = Item.objects.filter(ownermail=cmail).filter(status="future") 
    return render(request,"log.html",{'pitem':pitem,'litem':litem,'fitem':fitem,"biddeditem":biddeditem})

def future(request):
    items = Item.objects.filter(status="future")
    return render(request,"future.html",{"items":items})