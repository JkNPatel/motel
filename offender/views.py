from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.views import View
from .models import Offender,Experience,Extra_info,Blocked_user,NC_offender_experience,NC_Blocked_user,MCS_offender_experience,MCS_Blocked_user
from django.utils import timezone
from datetime import datetime,date
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User,auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator
from dateutil import parser
import mechanicalsoup
import time
from bs4 import BeautifulSoup
from url_parser import parse_url, get_url, get_base_url
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import requests

## find Criminal Records ##
def getCriminals(para):
    

    driver = webdriver.Chrome(ChromeDriverManager().install())

    browser = mechanicalsoup.Browser()

    #for site A
    urlA = f"https://webapps.doc.state.nc.us/opi/offendersearch.do?method=list&searchLastName={para['searchLastName']}&searchFirstName={para['searchFirstName']}&searchMiddleName={para['searchMiddleName']}&searchOffenderId={para['searchOffenderId']}&searchGender={para['searchGender']}&searchRace={para['searchRace']}&searchDOB={para['searchDOB']}&searchDOBRange={para['searchDOBRange']}&ethnicity={para['ethnicity']}&ageMinimum={para['ageMinimum']}&ageMaximum={para['ageMaximum']}&page=1"
    pageA = browser.get(urlA)
    htmlA = pageA.soup
    #print(htmlA)
    
    
    
    #function to get result array from htmlA
    
    last = htmlA.find_all("a", string=" Last ")
    #print(last)
    tmpResultA = list()
    if(len(last)==0):    
        urlA = f"https://webapps.doc.state.nc.us/opi/offendersearch.do?method=list&searchLastName={para['searchLastName']}&searchFirstName={para['searchFirstName']}&searchMiddleName={para['searchMiddleName']}&searchOffenderId={para['searchOffenderId']}&searchGender={para['searchGender']}&searchRace={para['searchRace']}&searchDOB={para['searchDOB']}&searchDOBRange={para['searchDOBRange']}&ethnicity={para['ethnicity']}&ageMinimum={para['ageMinimum']}&ageMaximum={para['ageMaximum']}&page=1"
        pageA = browser.get(urlA)
        htmlA = pageA.soup
        #print(htmlA)
        #function to get result array from htmlA
        testResult = getResultHtmlA(htmlA)
        tmpResultA.extend(testResult)
    else:
        href = last[0]['href']
        lastPageUrl = parse_url(href)
        lastPage = lastPageUrl['query']['page']
        if(int(lastPage)<=10):
            pass
        else:
            lastPage = 10
            #loop through all pages
        for page in range(1,int(lastPage)+1):
            #print(page)
            urlA = f"https://webapps.doc.state.nc.us/opi/offendersearch.do?method=list&searchLastName={para['searchLastName']}&searchFirstName={para['searchFirstName']}&searchMiddleName={para['searchMiddleName']}&searchOffenderId={para['searchOffenderId']}&searchGender={para['searchGender']}&searchRace={para['searchRace']}&searchDOB={para['searchDOB']}&searchDOBRange={para['searchDOBRange']}&ethnicity={para['ethnicity']}&ageMinimum={para['ageMinimum']}&ageMaximum={para['ageMaximum']}&page={page}"
            pageA = browser.get(urlA)
            htmlA = pageA.soup
            #print(htmlA)
            #function to get result array from htmlA
            testResult = getResultHtmlA(htmlA)
            if(testResult == 'None'):
                print('No Record')
            else:    
                tmpResultA.extend(testResult)
            #print(testResult)
              
    #print(tmpResultA)
    resultA = {'A': tmpResultA }

    
    #for site B

    urlB = f"https://inmateinquiryweb.mecklenburgcountync.gov/Inmate?activeOnly=False&lastName={para['searchLastName']}&firstName={para['searchFirstName']}&page=1"
    driver.get(urlB)

    driver.implicitly_wait(6)
    #time.sleep(3)

    myhtml = driver.execute_script('return document.getElementById("divInmateDetailsDeskTop").innerHTML')

    htmlB = BeautifulSoup(myhtml,'html.parser')
    #print(htmlB)
    array = list()
    array = getResultHtmlB(htmlB)
    if(len(array)==0):
        array.append('N')
    else:
        pass
    driver.quit()
    
    #print(array)
    #function to get result array from htmlB
    resultB = {'B': array }
    
        
    result = dict(resultA)
    result.update(resultB)
    #result.update(para)
    #print(result)
    return result


## get array from htmlA ##
def getResultHtmlA(htmlA):
    table = htmlA.find('table',{'class':'resultstable'})
    if(table==None):
        print('too big')
        return 'L'
    else:
        if(table.find('td',{'class':'tableCell'}).text == 'Nothing found to display'):
            print('No Record Found')
            return 'N'
        else:
            rows = table.find_all('tr')
            array = list() 
            
            for index1,row in enumerate(rows):
                data = row.find_all("td")
                #print(data)
                temp = [0 for x in range(9)] 
                for index2,column in enumerate(data):
                    rn = column
                    if(index1 != 0 and index1 != 1 and index1 != 2):
                        #print('('+str(index1)+'-'+str(index2)+'->'+rn)
                        if(index2 == 0):
                            temp[index2] = rn.find('a',{'class':'tablelink'}).get('href')
                        elif(index2 == 2):
                            pass
                        else:
                            temp[index2] = rn.get_text().strip()
                if(index1 != 0 and index1 != 1 and index1 != 2):
                    array.append(temp)
            return array
    
       
    


## get array from htmlB ##
def getResultHtmlB(htmlB):
   
    div = htmlB.find('div',{'data-bind':'foreach: inmates'})
    if(div == None):
        print('from site B Too big')
    records = div.find_all('a',{'data-bind':'attr: { href: DetailsUrl }'})
    array = list() 
    
    for index1,record in enumerate(records):
        if(record.get('href')==None):
            array.append('T')
        else:
            datas = record.find_all("label")
            temp = [0 for x in range(13)] 
            for index2,data in enumerate(datas):
                #print(data.text)
                #if(index2%2!=1 or index2==0):
                    #temp[index2] = data.text.strip()
                if(index2==0):
                    href = record.get('href')
                    newHref = href.replace('/Inmate/Details','')
                    temp[0] = newHref
                    temp[1] = data.text.strip().split(', ')[0]
                    temp[2] = 0
                    temp[3] = data.text.strip().split(', ')[1]
                    #print(data.text.strip().split(', ')[0])
                    #print(data.text.strip().split(', ')[1])
                elif(index2==1):
                    #temp[index2] = data.text.strip()
                    pass
                elif(index2==2):
                    temp[index2] = 0
                elif(index2==3):
                    #temp[index2] = data.text.strip()
                    pass
                elif(index2==4):
                    temp[index2] = 0
                elif(index2==5):
                    #temp[index2] = data.text.strip()
                    pass
                elif(index2==6):
                    temp[7] = data.text.strip()
                    temp[8] = calculateAge(date(int(data.text.strip().split('/')[2]),int(data.text.strip().split('/')[0]),int(data.text.strip().split('/')[1])))
                    pass
                elif(index2==7):
                    #temp[index2] = data.text.strip()
                    pass
                elif(index2==8):
                    temp[5] = data.text.strip().split('/')[1]
                    temp[6] = data.text.strip().split('/')[0]
                elif(index2==9):
                    #temp[index2] = data.text.strip()
                    pass
                elif(index2==10):
                    temp[index2] = data.text.strip()
                elif(index2==11):
                    #temp[index2] = data.text.strip()
                    pass
                elif(index2==12):
                    temp[index2] = data.text.strip()
                else:
                    #temp[index2] = data.text.strip()
                    pass
                #[0,  'PATE',  0, 'AARON',      0,  'M',    'CAU',        '5/15/1996'    , 0, 0, '5\'09"', 0, '140']
               # [[0, 'PATEL', 0, 'RAMJIBHAI', 'S', 'MALE', 'ASIAN/ORTL', '04/15/1966', '54']
               #[['PATE, AARON', 0, '0000420303', 0, '20-017631', 0, '5/15/1996', 0, 'CAU/M', 0, '5\'09"', 0, '140']
               #PATERSON, DONALD -0|PID:-1|0000120249-2|JID:-3|18-011173-4|DOB:-5|1/6/1970-6|Race/Sex:-7|W/M-8|Height:-9|604-10|Weight:-11|220-12
            array.append(temp)    
            
    #print(array)  
    return array

## Age Calculate ##
  
def calculateAge(birthDate):
     
    today = date.today() 
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day)) 

    return age


## function for getting criminal records ##

## find Criminal Records ##
def criminalDetails(offenderID):
  
    driver = webdriver.Chrome(ChromeDriverManager().install())

    #-for img

    browser = mechanicalsoup.Browser()
    
    #for site A
    urlA = f"https://webapps.doc.state.nc.us/opi/viewoffender.do?method=view&offenderID={offenderID}"
    driver.get(urlA)
    imgClick = driver.find_element_by_id("dopPicture")

    imgClick.click()
    driver.implicitly_wait(3)
    
    #print(driver.page_source)
    clickSoup = BeautifulSoup(driver.page_source, 'html.parser')
    pageA = browser.get(urlA)
    htmlA = pageA.soup
    page = requests.get(urlA)
    soup = BeautifulSoup(page.text, 'html.parser')

    result = {}
    
    #type(soup)
    #print('Image : '+'https://webapps.doc.state.nc.us/opi/'+soup.find('img',{'id':'dopPicture'}).get('src'))
    result['image'] = 'https://webapps.doc.state.nc.us/opi/'+clickSoup.find('img',{'id':'dopPicture'}).get('src')
    #print(result)
    table = soup.find('table',{'class':'displaydatatable'})
    #print(table)
    #print(soup)
    table2 = soup.find_all('table',{'class':'datainput'})

    records = list()
    
    for index,each_table in enumerate(table2):
        if(index==0 and each_table.find('th').text == 'Last Name'):
            pass
        else:
        #column = rows.find_all('td')
        #print(each_table.find_all('tr'))
            for index1,column in enumerate(each_table.find_all('tr')):
                #print(column.find_all('td'))
                tmpRecord = list()
                for index2,data in enumerate(column.find_all('td')):
                    #print(data.text)
                    tmpRecord.append(data.text)
                    
                    #print('---------------'+str(index2)+"--------------")
                records.append(tmpRecord)
        #for index2,each_record in enumerate(column):
        #    print(each_record.text)
        #print('-----------------------------')
    #print(table2)
    result['records'] = records
    rows = table.find_all("td")

    for index,each in enumerate(rows):
        if(index == 0):
            result['name'] = each.text
        elif(each.text == 'Offender Number:'):
            result['OffenderNumber'] =  rows[index+1].text.strip()
        elif(each.text == 'Inmate Status:'):
            result['InmateStatus'] =  rows[index+1].text
        elif(each.text == 'Gender:'):
            result['Gender'] =  rows[index+1].text
        elif(each.text == 'Race:'):
            result['Race'] =  rows[index+1].text
        elif(each.text == 'Birth Date:'):
            result['BirthDate'] =  rows[index+1].text
        elif(each.text == 'Age:'):
            result['Age'] =  rows[index+1].text
        else:
            pass

    

    return result



## Inmate details ##

def inmateDetails(pid,jid):
   
    driver = webdriver.Chrome(ChromeDriverManager().install())

    browser = mechanicalsoup.Browser()
    
    #for site B
    urlB = f"https://inmateinquiryweb.mecklenburgcountync.gov/Inmate/Details?pid={pid}&jid={jid}"
    driver.get(urlB)

    result = {}
    driver.implicitly_wait(10)
    time.sleep(1)

    myhtml = driver.execute_script('return document.querySelector("div.container.body-content").innerHTML')
    
    htmlB = BeautifulSoup(myhtml,'html.parser')

    image = 'https://inmateinquiryweb.mecklenburgcountync.gov'+str(htmlB.find('img',{'data-bind':'attr:{src: ImageUrl}'}).get('src'))

    name = htmlB.find('p',{'data-bind':'text: Name'}).text
    fname = name.split(',')[1]
    lname = name.split(',')[0]
    result['image'] = image
    result['fname'] = fname
    result['lname'] = lname
    
    
    basic = htmlB.find('div',{'id':'divInmateDetailsDesktopMediaQuery'})

    for index,each in enumerate(basic.find_all('label')):
        #print(each.text)
        if(each.text == 'PID:'):
            result['PID'] = basic.find_all('label')[index+1].text
        elif(each.text == 'JID:'):
            result['JID'] = basic.find_all('label')[index+1].text
        elif(each.text == 'DOB:'):
            result['DOB'] = basic.find_all('label')[index+1].text
        elif(each.text == 'Race/Sex:'):
            raceSex = basic.find_all('label')[index+1].text
            result['Race'] = raceSex.split('/')[0]
            result['Sex'] = raceSex.split('/')[1]
        elif(each.text == 'Height:'):
            result['Height'] = basic.find_all('label')[index+1].text
        elif(each.text == 'Address:'):
            result['Address'] = basic.find_all('label')[index+1].text
        elif(each.text == 'Status:'):
            result['Status'] = basic.find_all('label')[index+1].text
        elif(each.text == 'Commited:'):
            result['Commited'] = basic.find_all('label')[index+1].text
        elif(each.text == 'Released:'):
            result['Released'] = basic.find_all('label')[index+1].text
        else:
            pass

    charges = htmlB.find('div',{'id':'divInmateDetailsDesktopCharges'})

    data = list()

    table = charges.find_all('label')
    temp = list()
    #print(table)
    for i,charge in enumerate(charges.find_all('label')):
        #print(charges.find_all('label')[i].text)
        if(i>5):
            temp.append(charges.find_all('label')[i].text)
        else:
            pass
        
    #print(temp) 
    length = (len(table)-6)/10
    tag = 0
    for index in range(1,int(length)+1):
        tmp = list()
        for index2 in range(10):
            if(index2 ==6 or index2==8):
                pass
            else:
                tmp.append(temp[index2+tag])
        tag = tag + 10
        data.append(tmp)
        

    result['Charges'] = data
    driver.quit()
    
    return result


## user login ##

class Login(View):
    def get(self,request):
        print('get login')
        return render(request,'login.html')
    def post(self,request):
        print('post login')

        user_email = request.POST['user_email']
        user_pass = request.POST['user_pass']

        print(user_email)
        print(user_pass)
        user = auth.authenticate(username=user_email,password=user_pass)

        if user is not None:
            print('Login successful')
            auth.login(request,user)
            return redirect("offender:dashboard")
        else:
            print('Login invalid')
            return render(request,'login.html',{'login_error':'error`'})
            
@login_required       
def logout(request):
    auth.logout(request)
    print("logout")
    return redirect("offender:login")



## signup

"""

class Signup(View):
    def get(self,request):
        print('get signup')
        return render(request,'signup.html')
    def post(self,request):
        print('post signup')

        user_email = request.POST['user_email']
        user_pass = request.POST['user_pass']
        user_repeat_pass = request.POST['user_repeat_pass']
        
        user_created_date = timezone.now()

        user = User.objects.create_user(username=user_email,password = user_pass, date_joined = user_created_date)

        user.save()
        print('User created')
        return redirect('offender:login')

"""


## forgot_password

class Forgot_password(View):
    def get(self,request):
        print('get forgot password')
        return render(request,'forgot_password.html',{'security_question':'','security_answer':'','password':'','email':''})
        
    def post(self,request):
        print('post forgot password')
        
        username = request.POST['username']
        
        if not 'security_answer' in request.POST:

            if(username != ''):

                if User.objects.filter(username=username).exists():
                    user_data = User.objects.get(username=username)
                    if Extra_info.objects.filter(user_id=user_data.id).exists():
                        extra = Extra_info.objects.get(user_id=user_data.id)
                        print(extra.security_question)
                        return render(request,'forgot_password.html',{'security_question':extra.security_question,'security_answer':'','password':'','email':username})
            
                else:
                    return render(request,'forgot_password.html',{'security_question':'','security_answer':'','password':'','error_email':'Please enter registered email address','email':username})
        
        else:
            security_question = request.POST['security_question']
            security_answer = request.POST['security_answer']
            if(security_answer != ''):
                if(username != ''):

                    if User.objects.filter(username=username).exists():
                        user_data = User.objects.get(username=username)
                        extra = Extra_info.objects.get(user_id=user_data.id)

                        if not 'new_password' in request.POST:
                            if(security_answer == extra.security_answer and security_question==extra.security_question):
                                print('match')
                                return render(request,'forgot_password.html',{'security_question':extra.security_question,'security_answer':security_answer,'password':user_data.password,'email':username})
                            else:
                                print('not match')
                                return render(request,'forgot_password.html',{'security_question':extra.security_question,'security_answer':security_answer,'password':'','email':username,'error_ans':'This answer is not correct'})
        
                        else:
                            new_password = request.POST['new_password']
                            if(new_password != ''): 
                                user_data.set_password(new_password)
                                user_data.save()
                                return redirect("offender:login")
                            else:
                                return redirect("offender:login")
        

            
        return redirect("offender:login")

#@login_required(login_url='/login/')
@method_decorator(login_required, name='dispatch')
class Profile(View):
    def get(self,request,id):
        print('get profile')
        user_data = User.objects.get(pk=id)

        if Extra_info.objects.filter(user_id=user_data.id).exists():
            extra = Extra_info.objects.get(user_id=user_data.id)
            return render(request,'profile.html',{'name':extra.motel_name,'address':extra.motel_address,'city':extra.motel_city,'state':extra.motel_state,'country':extra.motel_country,'pincode':extra.motel_pincode})


        return render(request,'profile.html')

    def post(self,request,id):
        print('post profile ')

        motel_name = request.POST['name']
        motel_address = request.POST['address']
        motel_city = request.POST['city']
        motel_state = request.POST['state']
        motel_country = request.POST['country']
        motel_pincode = request.POST['pincode']
        
        if(motel_name.strip()!='' or motel_address.strip()!='' or motel_city.strip()!='' or motel_state.strip()!='' or motel_country.strip()!='' or motel_pincode.strip()!=''):
            user_data = User.objects.get(pk=id)

            if Extra_info.objects.filter(user_id=user_data.id).exists():
                extra = Extra_info.objects.get(user_id=user_data.id)
                extra.motel_name = motel_name
                extra.motel_address = motel_address
                extra.motel_city = motel_city
                extra.motel_state = motel_state
                extra.motel_country = motel_country
                extra.motel_pincode = motel_pincode
                extra.save()
                return render(request,'profile.html',{'name':motel_name,'address':motel_address,'city':motel_city,'state':motel_state,'country':motel_country,'pincode':motel_pincode})

            else:
                extra = Extra_info.objects.create(user_id=user_data.id,motel_name=motel_name,motel_address = motel_address, motel_city = motel_city,motel_state=motel_state,motel_country=motel_country,motel_pincode=motel_pincode)
                extra.save()
                return render(request,'profile.html',{'name':motel_name,'address':motel_address,'city':motel_city,'state':motel_state,'country':motel_country,'pincode':motel_pincode})

        return render(request,'profile.html')
        
@method_decorator(login_required, name='dispatch')
class Recovery_password(View):
    def get(self,request,id):
        print('get recovery password')
        
        user_data = User.objects.get(pk=id)
        if Extra_info.objects.filter(user_id=user_data.id).exists():
            extra = Extra_info.objects.get(user_id=user_data.id)
            return render(request,'recovery_password.html',{'security_question':extra.security_question,'security_answer':extra.security_answer})
        else:
            return render(request,'recovery_password.html')

    def post(self,request,id):
        print('post recovery password')
        security_question = request.POST['security_question']
        security_answer = request.POST['security_answer']


        if(security_question.strip()!='' and security_answer.strip()!=''):
            print('posted')
            user_data = User.objects.get(pk=id)
            
           
            if Extra_info.objects.filter(user_id=user_data.id).exists():
                print('edit')
                extra = Extra_info.objects.get(user_id=user_data.id)
                extra.security_question = security_question
                extra.security_answer = security_answer
                extra.save()

            else:
                print('create')  
                extra = Extra_info.objects.create(security_question=security_question, security_answer=security_answer, user_id=user_data.id)
                extra.save()
            
            #user_data.extra_info.security_question = security_question.strip()
            #user_data.extra_info.security_answer = security_answer.strip()
            #user_data.save()
            
            return redirect("offender:dashboard")
        else:
            return redirect("offender:dashboard")

## dashboard view ##
@method_decorator(login_required, name='dispatch')
class Dashboard(View):
    def get(self,request):
        #record_list = Record.objects.filter(off_status="Active").filter(off_last_name__contains='').filter(off_first_name__contains='').filter(off_birth_date='2020-11-30').order_by('-off_created_date')       
        return render(request,'dashboard.html')
    def post(self,request):
        print('post dashboard')
        
        searchFirstName = request.POST['searchFirstName']
        searchLastName = request.POST['searchLastName']
        searchDOB = request.POST['searchDOB']
        searchMiddleName = request.POST['searchMiddleName']
        searchGender = request.POST['searchGender']
        searchRace = request.POST['searchRace']
        ethnicity = request.POST['ethnicity']
        searchOffenderId = request.POST['searchOffenderId']
        searchDOBRange = request.POST['searchDOBRange']
        pid = request.POST['pid']
        jid = request.POST['jid']
        PrisType = request.POST['PrisType']
        ageMinimum = request.POST['ageMinimum']
        ageMaximum = request.POST['ageMaximum']   

        if(searchLastName.strip()!='' or searchFirstName.strip()!='' or searchMiddleName.strip()!='' or searchOffenderId.strip()!='' or searchGender.strip()!='' or searchRace.strip()!='' or searchDOB.strip()!='' or searchDOBRange.strip()!='' or ethnicity.strip()!='' or ageMinimum.strip()!='' or ageMaximum.strip()!='' or pid.strip()!='' or jid.strip()!='' or PrisType.strip()!=''):
            
            lastname_error = firstname_error = birthdate_error=middlename_error=offenderid_error = ageminimum_error = agemaximum_error = pid_error = jid_error=''


            if(len(searchLastName.strip()) >0):        
                if(len(searchLastName.strip()) >35):
                    lastname_error = "Last name length should be less than 35 characters"
                    print(lastname_error)
               

            if(len(searchFirstName.strip()) >0):        
                if(len(searchFirstName.strip()) >25):
                    firstname_error = "First name length should be less than 25 characters"
                    print(firstname_error)
                    
           
            if(len(searchDOB.strip()) >0):   
                if(len(searchDOB.strip()) >10 ):
                    birthdate_error = "Birth Date length should be less than 10 characters"
                    print(birthdate_error)
                    

            if(len(searchMiddleName.strip()) >0):        
                if(len(searchMiddleName.strip()) >1 or searchMiddleName.strip().isnumeric() == True):
                    middlename_error = "Middle name length should be 1 character only and should be numeric"
                    print(middlename_error)
                

            if(len(searchOffenderId.strip()) >0):     
                if(len(searchOffenderId.strip()) >7 or searchOffenderId.strip().isnumeric()==False):
                    offenderid_error  = "Offender Id is numeric and it's length should be less than 7 characters"
                    print(offenderid_error)
               

            if(len(ageMinimum.strip()) >0 ):   
                if(len(ageMinimum.strip()) >3 or ageMinimum.strip().isnumeric() == False or int(ageMinimum.strip())<0 or int(ageMinimum.strip())>150):
                    ageminimum_error = "Minimum age is numeric(between 1 to 150) and it's length should be less than 3 characters"
                    print(ageminimum_error)
               

            if(len(ageMaximum.strip()) >0 ):
                if(len(ageMaximum.strip()) >3 or ageMaximum.strip().isnumeric() == False or int(ageMaximum.strip())<0 or int(ageMaximum.strip())>150):
                    agemaximum_error = "Maximum age is numeric(between 1 to 150) and it's length should be less than 3 characters"
                    print(agemaximum_error)
                    

            if(len(pid.strip()) >0):   
                if(len(pid.strip()) >10 or pid.strip().isnumeric() == False ):
                    pid_error = "PID length should be less than 10 characters and should be numeric"
                    print(pid_error)
                    

            if(len(jid.strip()) >0):   
                if(len(jid.strip()) >10 ):
                    jid_error = "JID length should be less than 10 characters"
                    print(jid_error)

            if(lastname_error =='' and firstname_error =='' and birthdate_error=='' and middlename_error=='' and offenderid_error=='' and ageminimum_error=='' and agemaximum_error=='' and pid_error=='' and jid_error==''):
                print('search data now')
                print(searchLastName)
                print(searchFirstName)
                if searchDOB == '':
                    print('none')
                    record_list = Offender.objects.filter(off_status="Active").filter(off_last_name__contains=searchLastName).filter(off_first_name__contains=searchFirstName).filter(off_birth_date__contains='').order_by('-off_created_date')
                
                else:
                    print('else ')
                    print(parse_date(searchDOB))
                    record_list = Offender.objects.filter(off_status="Active").filter(off_last_name__contains=searchLastName).filter(off_first_name__contains=searchFirstName).filter(off_birth_date=parse_date(searchDOB)).order_by('-off_created_date')
                
                #print(parse_date(searchDOB))
                #search in database
                
       
                para = {'searchLastName':searchLastName.strip(),'searchFirstName':searchFirstName.strip(),'searchMiddleName':searchMiddleName.strip(),'searchOffenderId':searchOffenderId.strip(),'searchGender':searchGender.strip(),'searchRace':searchRace.strip(),'searchDOB':searchDOB.strip(),'searchDOBRange':searchDOBRange.strip(),'ethnicity':ethnicity,'ageMinimum':ageMinimum.strip(),'ageMaximum':ageMaximum.strip(),'pid':pid.strip(),'jid':jid.strip(),'prisType':PrisType.strip()}
                dic_record = getCriminals(para)
                #print(dic_record)
                #print(type(dic_record['A']))
                return render(request,'dashboard.html',{'dic_record_a':dic_record['A'],'dic_record_b':dic_record['B'],'searchFirstName':searchFirstName,'searchLastName':searchLastName,'searchDOB':searchDOB,'record':record_list})
            else:
                return render(request,'dashboard.html',{'lastname_error':lastname_error,'firstname_error':firstname_error,'birthdate_error':birthdate_error,'middlename_error':middlename_error,'offenderid_error':offenderid_error,'ageminimum_error':ageminimum_error,'agemaximum_error':agemaximum_error,'pid_error':pid_error,'jid_error':jid_error})

            
        else:
            print("Fill atleast one field")
            return render(request,'dashboard.html')




## New record add ##          
@method_decorator(login_required, name='dispatch')
class Add_record(View):
    def get(self,request):
        print('get add record')
        return render(request,'add_history.html')
    def post(self,request):
        print('post record')
        
        if(request.POST['searchFirstName'] != '' and request.POST['searchLastName'] != '' and request.POST['searchDOB'] != '' and  request.POST['searchGender'] != '' and request.POST['searchRace'] != '' and request.POST['experience'] != '' and request.POST['off_permission'] != ''):
            
            first_name = request.POST['searchFirstName']
            last_name = request.POST['searchLastName']
            birth_date = request.POST['searchDOB']
            gender = request.POST['searchGender']
            race = request.POST['searchRace']
            experience = request.POST['experience']
            permission = request.POST['off_permission']

            days = (datetime.now().date() - parse_date(request.POST['searchDOB'])).days
            if(days>=1):
                age = int((datetime.now().date() - parse_date(request.POST['searchDOB'])).days / 365.25)
            else:
                print('returned')
                return render(request,'add_history.html',{'first_name':first_name,'last_name':last_name,'birth_date':birth_date,'gender':gender,'race':race,'experience':experience,'permission':permission})
            

            check_record = Offender.objects.filter(off_first_name=first_name).filter(off_last_name=last_name).filter(off_birth_date=birth_date).filter(off_gender=request.POST['searchGender']).filter(off_race=request.POST['searchRace'])
            print(check_record.count())
            
            if(check_record.count() ==1):
                
                
                for row in check_record:
                    tem_id = row.id
                        
                new_experience = Experience.objects.create(record_experience=experience,record_status="Active",record_updated_date=datetime.now(),record_owner_id_id=request.user.id,record_id_id=tem_id)
                new_experience.save()

                block_user_list = Blocked_user.objects.filter(blocked_record_id_id =tem_id).filter(blocked_user_owner_id_id =request.user.id)
                print(block_user_list.count())

                if(block_user_list.count() ==1):
                    print('count 1 ')

                    for row_data in block_user_list:
                        tem_row_id = row_data.id

                        block_user_data = Blocked_user.objects.get(pk=tem_row_id)
                        block_user_data.blocked_user_status = permission
                        block_user_data.save()
          
                else:
                    print('count 2 ')
                    block_user_new = Blocked_user.objects.create(blocked_user_status=permission,blocked_user_updated_date=datetime.now(),blocked_record_id_id=tem_id,blocked_user_owner_id_id =request.user.id)
                    block_user_new.save()
                

                print('appended')

            else:
                print('it is fine')   

                record = Offender.objects.create(off_first_name=first_name,off_last_name=last_name,off_birth_date=birth_date,off_gender=gender,off_race=race,off_status="Active",off_age=age,off_updated_date=datetime.now())
                record.save()

                
                experience = Experience.objects.create(record_experience=experience,record_status="Active",record_updated_date=datetime.now(),record_owner_id_id=request.user.id,record_id_id=record.pk)
                experience.save() 

                block_user = Blocked_user.objects.create(blocked_user_status=permission,blocked_user_updated_date=datetime.now(),blocked_record_id_id=record.pk,blocked_user_owner_id_id =request.user.id)
                block_user.save()
            

            return redirect('offender:view_record')

        else:
            print('checked')
            return redirect('offender:add_record')





## View list of records by owner ##
@method_decorator(login_required, name='dispatch')
class View_record(View):
    def get(self,request):
        print('get for view record')
        
        #all_experience=Experience.objects.values_list('record_id_id', flat=True).distinct()
        
        all_owner=Experience.objects.filter(record_status="Active").filter(record_owner_id_id=request.user.id).order_by('-record_updated_date').values_list('record_id_id',flat=True).distinct()
        print(all_owner.count())


        tem = list()
        for data1 in all_owner:
              tem.append(data1)
        #print(tem)
      
        #print('-----')
    
        offenders = list()
        for data in tem:
            if data not in offenders: 
                offenders.append(data)  
        #print(offenders)
        
        record= list()
        for data2 in offenders:
            each_record = Offender.objects.get(pk=data2)
            if(each_record.off_status=='Active'):
                record.append(each_record)
        #print(record)
        #print('--')   
            
    
        #experience_data = Experience.objects.filter(record_owner_id_id=request.user.id).filter(record_status="Active").order_by('-record_updated_date')
        

        #record_list = Offender.objects.filter(off_status="Active").order_by('-off_updated_date')

        #block_data = Blocked_user.objects.filter(blocked_user_status='B').filter()
    
        return render(request,'history_list.html',{'record':record})





## each record details entered by owner ##
@method_decorator(login_required, name='dispatch')
class Record_detail(View):
    def get(self,request,id):
        print('get record detail')
        
        record_data = Offender.objects.get(pk=id)
        age = int((datetime.now().date() - parse_date(str(record_data.off_birth_date))).days / 365.25)
       
        experience_data = Experience.objects.filter(record_id_id=id).filter(record_status="Active").order_by('-record_updated_date')

        block_user_data = Blocked_user.objects.filter(blocked_record_id_id=id).filter(blocked_user_owner_id_id =request.user.id)
        
        if(block_user_data.count()==1):
            return render(request,'history_detail.html',{'record_data':record_data,'age':age,'experience':experience_data,'blocklist':block_user_data[0].blocked_user_status})
        
        else:
            return render(request,'history_detail.html',{'record_data':record_data,'age':age,'experience':experience_data})
        
        

        
    def post(self,request,id):

        print('post record')
        
       
        if (request.POST.get("add_experience") != None):
            
            user_id = request.POST['user']
            record_id = request.POST['record']
            experience = request.POST.get('add_experience')

            record = Experience.objects.create(record_experience=experience,record_status="Active",record_updated_date=datetime.now(),record_owner_id_id=user_id,record_id_id=record_id)
            record.save()

            return HttpResponseRedirect('/offender/record-detail/%d'%int(record_id))

        elif(request.POST['edit_experience'] != None ):

            print('edit')

            user_id = request.POST['user']
            record_id = request.POST['record']
            record_data = Experience.objects.get(pk=record_id)

            experience = request.POST.get('edit_experience')
            record_data.record_experience =experience
            record_data.record_updated_date = datetime.now()

            record_data.save()

            return HttpResponseRedirect('/offender/record-detail/%d'%int(id))

        else:
            print('checked')
            return HttpResponseRedirect('/offender/record-detail/%d'%int(id))



"""

## edit record entered by owner ##
@method_decorator(login_required, name='dispatch')
class Edit_record(View):
    def get(self,request,id):
        print('get edit record detail')
        record_data = Offender.objects.get(pk=id)
        print(record_data.off_first_name)
        return render(request,'edit_history.html',{'record_data':record_data})

    def post(self,request,id):
        print('post edited record')
        
        if(request.POST['searchFirstName'] == '' or request.POST['searchLastName'] == '' or request.POST['searchDOB'] == ''):
            return HttpResponseRedirect('/offender/edit-record/%d'%int(id))
        
        

        firstname = request.POST['searchFirstName']
        lastname = request.POST['searchLastName']



        days = (datetime.now().date() - parse_date(request.POST['searchDOB'])).days
        if(days>=1):
            birthdate = request.POST['searchDOB']
            print('ok')
        else:
            return HttpResponseRedirect('/offender/edit-record/%d'%int(id))

        # type here 
        print(birthdate)

        record_data = Offender.objects.get(pk=id)
        date = parser.parse(birthdate).date()

        

        if(firstname != record_data.off_first_name or lastname != record_data.off_last_name or date != record_data.off_birth_date or request.POST['searchGender'] != record_data.off_gender or request.POST['searchRace']!= record_data.off_race ):
            print('true ')
            check_record = Offender.objects.filter(off_first_name=firstname).filter(off_last_name=lastname).filter(off_birth_date=birthdate).filter(off_gender=request.POST['searchGender']).filter(off_race=request.POST['searchRace'])
            print(check_record.count())
            
            if(check_record.count() ==1):
                print('do somethinng')
                
                #record_data.off_status='Inactive'
                all_exp = Experience.objects.filter(record_status="Active").filter(record_id_id=record_data.id).order_by('-record_updated_date')

                for row in all_exp:
                    for r in check_record:
                        tem_id = r.id
                    row.record_id_id = tem_id
                    row.save()
                
            else:
                print('it is fine')    
       
        

        record_data.off_first_name = request.POST['searchFirstName']
        record_data.off_last_name  = request.POST['searchLastName']
        
        record_data.off_gender = request.POST['searchGender']
        record_data.off_race = request.POST['searchRace']
        #record_data.off_experience =request.POST['experience']
        record_data.off_permission = request.POST['off_permission']

        record_data.off_updated_date = datetime.now()
       
        record_data.off_age = int((datetime.now().date() - parse_date(request.POST['searchDOB'])).days / 365.25)
        record_data.off_birth_date = request.POST['searchDOB']
      
        
      
        record_data.save()
       # todo.save()
        print("updated")
        
        return redirect('offender:view_record')


"""


## delete record ##
@method_decorator(login_required, name='dispatch')
class Delete_record(View):
    def get(self,request,id):
        
        

        all_experience_number = Experience.objects.filter(record_status="Active").filter(record_id_id=id).order_by('-record_updated_date')
        
        all_experience = Experience.objects.filter(record_status="Active").filter(record_id_id=id).filter(record_owner_id_id=request.user.id).order_by('-record_updated_date')
        print(all_experience.count())

        if(all_experience_number.count() == all_experience.count()):
            print('no other user added exp')
            record_data = Offender.objects.get(pk=id)
            record_data.off_status = "Inactive"
            record_data.save()

        else:
            print('record availbale')

        

        for experience in all_experience:
            print(experience.record_status) 
            experience.record_status = "Inactive"
            experience.save()
        
        
        print("record deletded and update")
        return redirect('offender:view_record')



## delete record ##
@method_decorator(login_required, name='dispatch')
class Delete_experience(View):
    def get(self,request,id):

        record_data = Experience.objects.get(pk=id)
        record_data.record_status = "Inactive"
        record_data.save()
        print("Experience deletded and update")

        all_experience = Experience.objects.filter(record_status="Active").filter(record_id_id=record_data.record_id_id).order_by('-record_updated_date')
        print(all_experience.count())

        if(all_experience.count() == 0):
            print('no record')
            offender =  Offender.objects.get(pk=record_data.record_id_id)
            offender.off_status = 'Inactive'
            offender.save()
            return redirect('offender:view_record')

        else:
            print('record availbale')
            return HttpResponseRedirect('/offender/record-detail/%d'%int(record_data.record_id_id))

        
# change block user status       
@method_decorator(login_required, name='dispatch')
class Change_block_status(View):
    def get(self,request,id):

        block_data = Blocked_user.objects.filter(blocked_record_id_id=id).filter(blocked_user_owner_id=request.user.id)
        print(block_data.count())
        
        if(block_data.count()==1):
            
            for data in block_data:
                if(data.blocked_user_status=='A'):
                    data.blocked_user_status = 'B'
                    data.save()
                else:
                    data.blocked_user_status = 'A'
                    data.save()
        

        else:
            print('0')
            block_user = Blocked_user.objects.create(blocked_user_status='B',blocked_user_updated_date=datetime.now(),blocked_record_id_id=id,blocked_user_owner_id_id =request.user.id)
            block_user.save()

        
        status = self.request.GET.get('status', None)
        if status is not None:
            print('pass')
            return redirect('offender:block_record')
             
        else:
            print('fail')

        return HttpResponseRedirect('/offender/record-detail/%d'%int(id))



## View list of blocked records by owner ##
@method_decorator(login_required, name='dispatch')
class Block_user_records(View):
    def get(self,request):
        print('get for blocked record')
        
        #all_experience=Experience.objects.values_list('record_id_id', flat=True).distinct()
        
        all_blocked_user_data=Blocked_user.objects.filter(blocked_user_status="B").filter(blocked_user_owner_id=request.user.id).order_by('-blocked_user_updated_date')
        print(all_blocked_user_data.count())

        if(all_blocked_user_data.count() >= 1):

            record = list()

            for each in all_blocked_user_data:
                tem = Offender.objects.filter(pk=each.blocked_record_id_id)
                record.append(tem)
        
        all_mcs_blocked_user_data=MCS_Blocked_user.objects.filter(mcs_blocked_user_status="B").filter(mcs_blocked_user_owner_id_id=request.user.id).order_by('-mcs_blocked_user_updated_date')
        print(all_mcs_blocked_user_data.count())
        #print(all_mcs_blocked_user_data[0].mcs_blocked_user_first_name)

        all_nc_blocked_user_data=NC_Blocked_user.objects.filter(nc_blocked_user_status="B").filter(nc_blocked_user_owner_id_id=request.user.id).order_by('-nc_blocked_user_updated_date')
        print(all_nc_blocked_user_data.count())

        
        return render(request,'blocked_list.html',{'record':record,'mcs_record':all_mcs_blocked_user_data,'ncs_record':all_nc_blocked_user_data})

        

        
        


## function for detail of offender ##
@method_decorator(login_required, name='dispatch')
class Offender_details(View):
    def get(self,request):
        print('get for offender detail record')

        id = self.request.GET.get('offenderID', None)
        if id is not None:
            print('pass')
            print(id)
            data = criminalDetails(id)
            print(data)
        else:
            return redirect("offender:dashboard")
            
        
        all_exp = NC_offender_experience.objects.filter(nc_off_id=id).filter(nc_off_exp_status='Active')
        print(all_exp.count())

        block_user_data = NC_Blocked_user.objects.filter(nc_blocked_user_id=id).filter(nc_blocked_user_owner_id_id =request.user.id)
        print(block_user_data.count())
        if(block_user_data.count()==1):
            print(block_user_data[0].nc_blocked_user_status)
            return render(request,'offender_detail.html',{'record':data,'experience':all_exp,'blockllist':block_user_data[0].nc_blocked_user_status})
        else:
            return render(request,'offender_detail.html',{'record':data,'experience':all_exp})

       

    def post(self,request):

        print('post record')
        
        
        if (request.POST.get("add_experience") != None):
            
            print('in add')
            user_id = request.POST['user']
            offender_id = request.POST['record']
            experience = request.POST.get('add_experience')
            

            nc_exp = NC_offender_experience.objects.create(nc_off_experience=experience,nc_off_exp_status="Active",nc_off_exp_updated_date=datetime.now(),nc_off_id=offender_id,nc_off_owner_id_id =user_id)
            nc_exp.save()


            data = criminalDetails(offender_id)

            all_exp = NC_offender_experience.objects.filter(nc_off_owner_id_id=request.user.id).filter(nc_off_id=offender_id).filter(nc_off_exp_status="Active")
            print(all_exp.count())

            

            return HttpResponseRedirect('/offender/offender-detail/?viewoffender.do?method=view&offenderID=%s'%str(offender_id))
            
            #return render(request,'offender_detail.html',{'record':data,'experience':all_exp})


        elif(request.POST['edit_experience'] != None ):

            print('edit')

            user_id = request.POST['user']
            record_id = request.POST['record']

            record_data = NC_offender_experience.objects.get(pk=record_id)

            experience = request.POST.get('edit_experience')
            record_data.nc_off_experience =experience
            record_data.nc_off_exp_updated_date = datetime.now()

            record_data.save()

            print(record_id)

            data = criminalDetails(record_data.nc_off_id)

            all_exp = NC_offender_experience.objects.filter(nc_off_owner_id_id=request.user.id).filter(nc_off_id=record_data.nc_off_id).filter(nc_off_exp_status="Active")
            print(all_exp.count())

            return HttpResponseRedirect('/offender/offender-detail/?viewoffender.do?method=view&offenderID=%s'%str(record_data.nc_off_id))
            
        
            

        else:
            print('checked')

            return redirect(request,'dashboard.html')


#function for deleteing experience of offender

@method_decorator(login_required, name='dispatch')
class Delete_offender_experience(View):
    def get(self,request,id):

        record_data = NC_offender_experience.objects.get(pk=id)
        record_data.nc_off_exp_status = "Inactive"
        record_data.save()
        print("Experience deletded and update")

        data = criminalDetails(record_data.nc_off_id)

        all_exp = NC_offender_experience.objects.filter(nc_off_owner_id_id=request.user.id).filter(nc_off_id=record_data.nc_off_id).filter(nc_off_exp_status='Active')
        print(all_exp.count())

        return HttpResponseRedirect('/offender/offender-detail/?viewoffender.do?method=view&offenderID=%s'%str(record_data.nc_off_id))
            


# change block user status       
@method_decorator(login_required, name='dispatch')
class Change_offender_block_status(View):
    def get(self,request):

        off_id = self.request.GET.get('off_id', None)
        name = self.request.GET.get('fname', None)
        DOB = self.request.GET.get('DOB', None)
        Race = self.request.GET.get('Race', None)
        Sex = self.request.GET.get('Sex', None)
        flag = self.request.GET.get('flag', None)

        if off_id is not None and name is not None and DOB is not None and Race is not None and Sex is not None: 
            
            fname = name.split(' ')[0]
            
            lname = name.split(' ')[1]
            print('-------')
            print(len(name.split(' ')))

            if(len(name.split(' ')) ==3):
                lname = name.split(' ')[2]
                fname = fname + ' '+ name.split(' ')[1]

            if(len(name.split(' ')) ==4):

                lname = name.split(' ')[2] + name.split(' ')[3]
                fname = fname + ' '+ name.split(' ')[1]


            print('pass')
            print(off_id)
           
            print(fname)
            print(lname)
            print(DOB)
            print(Race)
            print(Sex)
         
        
        if off_id is not None:  
        
       
            block_data = NC_Blocked_user.objects.filter(nc_blocked_user_id=off_id).filter(nc_blocked_user_owner_id_id=request.user.id)
            print(block_data.count())
            
            if(block_data.count()==1):
                
                for data in block_data:
                    if(data.nc_blocked_user_status=='A'):
                        data.nc_blocked_user_status = 'B'
                        data.save()
                    else:
                        data.nc_blocked_user_status = 'A'
                        data.save()
            

            else:
                print('0')
                if(name is not None and DOB is not None and Race is not None and Sex is not None):

                    block_user = NC_Blocked_user.objects.create(nc_blocked_user_status='B',nc_blocked_user_updated_date=datetime.now(),nc_blocked_user_id=off_id,nc_blocked_user_owner_id_id =request.user.id,nc_blocked_user_first_name=fname,nc_blocked_user_last_name=lname,nc_blocked_user_dob=DOB,nc_blocked_user_race=Race,nc_blocked_user_sex=Sex)
                    block_user.save()

        if (flag=='offender' ):
             return redirect("offender:block_record")

        else:

       
            return HttpResponseRedirect('/offender/offender-detail/?viewoffender.do?method=view&offenderID=%s'%str(off_id))
            



## function for detail of Inmate ##
@method_decorator(login_required, name='dispatch')
class Inmate_details(View):
    def get(self,request):
        print('get for offender detail record')

       
        pid = self.request.GET.get('pid', None)
        jid = self.request.GET.get('jid',None)

        if pid is not None and jid is not None:
            print('pass')
            print(pid)
            print(jid)
            data = inmateDetails(pid,jid)
            print(data)
        else:
            return redirect("offender:dashboard")

        all_exp = MCS_offender_experience.objects.filter(mcs_off_pid=pid).filter(mcs_off_jid=jid).filter(mcs_off_exp_status='Active')
        print(all_exp.count())

        block_user_data = MCS_Blocked_user.objects.filter(mcs_blocked_user_pid=pid).filter(mcs_blocked_user_jid=jid).filter(mcs_blocked_user_owner_id_id =request.user.id)
        print(block_user_data.count())

        if(block_user_data.count()==1):
            print(block_user_data[0].mcs_blocked_user_status)
            return render(request,'inmate_detail.html',{'record':data,'experience':all_exp,'blockllist':block_user_data[0].mcs_blocked_user_status})
        else:
            return render(request,'inmate_detail.html',{'record':data,'experience':all_exp})


    
    def post(self,request):

        print('post record')
        
        if (request.POST.get("add_experience") != None):
            
            print('in add')

            user_id = request.POST['user']
            pid = request.POST['pid']
            jid = request.POST['jid']
            experience = request.POST.get('add_experience')
            

            mcs_exp = MCS_offender_experience.objects.create(mcs_off_pid=pid,mcs_off_jid=jid,mcs_off_experience=experience,mcs_off_exp_status="Active",mcs_off_exp_updated_date=datetime.now(),mcs_off_owner_id_id =user_id)
            mcs_exp.save()


            data = inmateDetails(pid,jid)

            all_exp = MCS_offender_experience.objects.filter(mcs_off_owner_id_id=request.user.id).filter(mcs_off_pid=pid).filter(mcs_off_jid=jid).filter(mcs_off_exp_status="Active")
            print(all_exp.count())

            

            return HttpResponseRedirect('/offender/inmate-detail/Inmate/Details/?pid='+str(pid)+'&jid='+str(jid))
            
            #return render(request,'offender_detail.html',{'record':data,'experience':all_exp})


        elif(request.POST['edit_experience'] != None ):

            print('edit')

            user_id = request.POST['user']
            record_id = request.POST['record']

            record_data = MCS_offender_experience.objects.get(pk=record_id)

            experience = request.POST.get('edit_experience')
            record_data.mcs_off_experience =experience
            record_data.mcs_off_exp_updated_date = datetime.now()

            record_data.save()

            print(record_id)

            data = inmateDetails(record_data.mcs_off_pid,record_data.mcs_off_jid)

            all_exp = MCS_offender_experience.objects.filter(mcs_off_owner_id_id=request.user.id).filter(mcs_off_pid=record_data.mcs_off_pid).filter(mcs_off_jid=record_data.mcs_off_jid).filter(mcs_off_exp_status="Active")
            print(all_exp.count())

            

            return HttpResponseRedirect('/offender/inmate-detail/Inmate/Details/?pid='+str(record_data.mcs_off_pid)+'&jid='+str(record_data.mcs_off_jid))
        
        else:
            print('checked')

            return redirect(request,'dashboard.html')
        
       


#function for deleteing experience of offender

@method_decorator(login_required, name='dispatch')
class Delete_inmate_experience(View):
    def get(self,request,id):

        record_data = MCS_offender_experience.objects.get(pk=id)
        record_data.mcs_off_exp_status = "Inactive"
        record_data.save()
        print("Experience deletded and update")

        data = inmateDetails(record_data.mcs_off_pid,record_data.mcs_off_jid)

        all_exp = MCS_offender_experience.objects.filter(mcs_off_owner_id_id=request.user.id).filter(mcs_off_pid=record_data.mcs_off_pid).filter(mcs_off_jid=record_data.mcs_off_jid).filter(mcs_off_exp_status="Active")
        print(all_exp.count())

            

        return HttpResponseRedirect('/offender/inmate-detail/Inmate/Details/?pid='+str(record_data.mcs_off_pid)+'&jid='+str(record_data.mcs_off_jid))
           


# change block user status       
@method_decorator(login_required, name='dispatch')
class Change_inmate_block_status(View):
    def get(self,request):
        print('---------')
        pid = self.request.GET.get('pid', None)
        jid = self.request.GET.get('jid', None)
        fname = self.request.GET.get('fname', None)
        lname = self.request.GET.get('lname', None)
        DOB = self.request.GET.get('DOB', None)
        Race = self.request.GET.get('Race', None)
        Sex = self.request.GET.get('Sex', None)
        flag = self.request.GET.get('flag',None)


        if pid is not None and jid is not None: 
            print('pass')
            print(pid)
            print(jid)
            print(fname)
            print(lname)
            print(DOB)
            print(Race)
            print(Sex)
      

        else:
            return redirect("offender:dashboard")
        
        block_data = MCS_Blocked_user.objects.filter(mcs_blocked_user_pid=pid).filter(mcs_blocked_user_jid=jid).filter(mcs_blocked_user_owner_id_id=request.user.id)
        print(block_data.count())
        
        if(block_data.count()==1):
            
            for data in block_data:
                if(data.mcs_blocked_user_status=='A'):
                    data.mcs_blocked_user_status = 'B'
                    data.save()
                else:
                    data.mcs_blocked_user_status = 'A'
                    data.save()
        

        else:
            print('0')

            if fname is not None and lname is not None and DOB is not None and Race is not None and Sex is not None:

                block_user = MCS_Blocked_user.objects.create(mcs_blocked_user_status='B',mcs_blocked_user_updated_date=datetime.now(),mcs_blocked_user_pid=pid,mcs_blocked_user_jid=jid,mcs_blocked_user_owner_id_id =request.user.id,mcs_blocked_user_first_name=fname,mcs_blocked_user_last_name=lname,mcs_blocked_user_dob=DOB,mcs_blocked_user_race=Race,mcs_blocked_user_sex=Sex)
                block_user.save()

        if(flag=='inmate'):
            return redirect("offender:block_record")
        else:

            return HttpResponseRedirect('/offender/inmate-detail/Inmate/Details/?pid='+str(pid)+'&jid='+str(jid))
        
            