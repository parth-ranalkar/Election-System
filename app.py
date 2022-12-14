
from distutils.log import info
import string
from tabnanny import check
from flask import Flask, jsonify,render_template,request,session,redirect,url_for,flash,session,Response
from flaskext.mysql import MySQL

import datetime 
from datetime import date
import re

import base64
from cv2 import cv2


import numpy as np
import glob
import  sys
from PIL import Image
from logging import FileHandler,WARNING
import os
from os import listdir
from os.path import isfile, join
from itsdangerous import base64_encode, base64_decode
import pymysql





# Database Configs
app = Flask(__name__)
app.secret_key='raishaf'
app.config.from_object(__name__)


mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Parth@1313'
app.config['MYSQL_DATABASE_DB'] = 'biometric'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor =conn.cursor()

# Database Object
#mysql.init_app(app)

#mysql.init_app(app)
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
def face_detector(img, size = 0.5):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray,1.3,5)

    if faces is():
        return img,[]

    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y),(x+w,y+h),(0,255,255),2)
        roi = img[y:y+h, x:x+w]
        roi = cv2.resize(roi, (200,200))

    return img,roi





def face_identifire():
    size = 4
    haar_file = 'haarcascade_frontalface_default.xml'
    datasets = 'datasets'
  
# Part 1: Create fisherRecognizer 
    print('Recognizing Face Please Be in sufficient Lights...') 
  
# Create a list of images and a list of corresponding names 
    (images, lables, names, id) = ([], [], {}, 0) 
    for (subdirs, dirs, files) in os.walk(datasets): 
        for subdir in dirs: 
            names[id] = subdir 
            subjectpath = os.path.join(datasets, subdir) 
            for filename in os.listdir(subjectpath): 
                path = subjectpath + '/' + filename 
                lable = id
                images.append(cv2.imread(path, 0)) 
                lables.append(int(lable)) 
            id += 1
    (width, height) = (130, 100) 
  
# Create a Numpy array from the two lists above 
    (images, lables) = [np.asarray(lis) for lis in [images, lables]] 
  
# OpenCV trains a model from the images 
# NOTE FOR OpenCV2: remove '.face' 
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(images, lables) 
  
# Part 2: Use fisherRecognizer on camera stream 
    face_cascade = cv2.CascadeClassifier(haar_file) 
    webcam = cv2.VideoCapture(0,cv2.CAP_DSHOW) 
    c=0
    x=0
    id=""
    while True: 
        ret, im = webcam.read() 
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        confidence=0
        for (x, y, w, h) in faces: 
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
            face = gray[y:y + h, x:x + w] 
            face_resize = cv2.resize(face, (width, height)) 
        # Try to recognize the face 
            prediction = model.predict(face_resize) 
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3) 
  
            if prediction[1]<500: 
                confidence = int(100*(1-(prediction[1])/300))
                print(confidence)
            
            if confidence>75 :
                
                cv2.putText(im, '% s - %.0f' % (names[prediction[0]], prediction[1]), (x-10, y-10),  cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
                id=names[prediction[0]]
                x=1
                
                
            else: 
                cv2.putText(im, 'not recognized',(x-10, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0)) 
                c=c+1
                print("count=",c)
                redirect(url_for("vote"))

        cv2.imshow('OpenCV', im) 
        key = cv2.waitKey(1)
        if x==1:
            webcam.release()
            cv2.destroyAllWindows()
            return(1,id)
            break
        elif key == 27 or c==100:
            webcam.release()
            cv2.destroyAllWindows()
            return(0,0)
            
            break
        
    
    
    








def face_extractor(img):

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray,1.3,5)

    if faces is():
        return None

    for(x,y,w,h) in faces:
        cropped_face = img[y:y+h, x:x+w]

    return cropped_face



def createfacedataset():
    
  
    cursor.execute("SELECT max(id) FROM voters")
    rs=cursor.fetchone()
    datasets = 'datasets' 
    rs=int(rs[0])
    rs=rs+1
    print(rs)
    sub_data = str(rs)
    
    cap = cv2.VideoCapture(0)
    path = os.path.join(datasets, sub_data) 
    if not os.path.isdir(path): 
        os.mkdir(path) 
    count = 0
    while True:
        ret, frame = cap.read()
        
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray,1.3,5)

        if faces is not None:
            for(x,y,w,h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2) 
                
                face = cv2.resize(frame[y:y+h, x:x+w],(200,200))
                face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                cv2.imwrite('% s/% s.jpg' % (path, count), face) 
                count+=1
                cv2.putText(frame,str(count),(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                #cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2) 
                
        else:
            print("Face not Found")
            pass

        if cv2.waitKey(1)==13 or count==100:
            break
        cv2.imshow('identifying',frame)
    
    cv2.destroyWindow('identifying')
    cap.release()
    
    print('Colleting Samples Complete!!!')













  
    
@app.route('/')
def index():
    return render_template("home.html")

@app.route('/register')
def register():
    return render_template("voteregister/register.html")


@app.route('/candidates')
def candidates():
    
    cursor.execute("SELECT * FROM candidate")
    result = cursor.fetchall()
    
    x='<image xlink:href="data:image/png;base64, width="240" height="240" x="0" y="0" />'
    if result is not None:
        
        #for data in result:
           # text="<tr><td>"+str(data[0])+"</td>"+"<td>"+str(data[1])+"</td>"+"<td>"+str(data[2])+"</td>"+"<td>"+str(data[4])+"</td>"+"<td>"+str(data[5])+"</td>"+"<td>"+str(data[6])+"</td>"+"<td><img src="+str(data[7])+"/></td><form action=""><td class='text-center'><a class='btn btn-info btn-xs' href='#'>"+"<span class='glyphicon glyphicon-edit'></span> Edit</a> <a href='#' class='btn btn-danger btn-xs'><span class='glyphicon glyphicon-remove'>"+"</span> Del</a></td></form></tr>"

        return render_template("/candidates/candidate.html",result=result)


@app.route('/update', methods=['POST','GET'])
def update():
    try:
        
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            
            field = request.form['field'] 
            value = request.form['value']
            editid = request.form['id']
            
             
            if field == 'firstname':
                sql = "UPDATE candidate SET candidate_name=%s WHERE id=%s"
            if field == 'lastname':        
                sql = "UPDATE candidate SET candidate_lastname=%s WHERE id=%s"
            if field == 'dob':        
                sql = "UPDATE candidate SET candidate_dob=%s WHERE id=%s"
            if field == 'gender':        
                sql = "UPDATE candidate SET candidate_gender=%s WHERE id=%s"
            if field == 'adhar':        
                sql = "UPDATE candidate SET candidate_aadhaar=%s WHERE id=%s"
            if field == 'phone':        
                sql = "UPDATE candidate SET candidate_number=%s WHERE id=%s"
            if field == 'party':        
                sql = "UPDATE candidate SET candidate_symbol=%s WHERE id=%s"
                            
                
 
            data = (value, editid)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            success = 1
        return jsonify(success)
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()
    
@app.route('/del/<string:id>', methods=['GET','POST'])
def delete(id):
    
    cursor.execute("delete from candidate where id=%s",[id])
    conn.commit()
    return redirect('/candidates')


@app.route('/voters')
def voters():
    
    cursor.execute("SELECT * FROM voters")
    result = cursor.fetchall()
    
    if result is not None:
        
        return render_template("voters/voters.html",result=result)



        

@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("SELECT * from admin WHERE username=%s AND password=%s",(username,password))
        data = cursor.fetchone()
       
        if data is not None:
            
            return render_template('adminpanel.html')
        else :
            return redirect('/admin')
    else :
        return render_template('admin.html')

@app.route('/back')
def backToAdminPanel():
        return render_template('adminpanel.html')

@app.route('/candidate_register', methods = ['GET', 'POST'])
def candidate_register():
    
    if request.method == 'POST':
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        dob = request.form['birthday']
        gender = request.form['gender']
        aadhar = request.form['aadhar']
        phone = request.form['phone']
        symbol=request.form['symbol']

        print('Dob is : ',dob)

        check_fname = any(map(str.isdigit, firstname))
        check_lname = any(map(str.isdigit, lastname))

        def isvalidphone(phone_n):
            regex = ("^\(?([7-9]{1})\)?\d{9}$")
            p = re.compile(regex)
            if (phone_n == None):
                return False
            if(re.search(p, phone_n)):
                return True
            else:
                return False

        def isValidAadhaarNumber(str):
            regex = ("^[2-9]{1}[0-9]{3}[0-9]{4}[0-9]{4}$")
            p = re.compile(regex)
            if (str == None):
                return False
            if(re.search(p, str)):
                return True
            else:
                return False

        def calculateAge(birthDate):
            today = date.today()
            age = today.year - birthDate.year -((today.month, today.day) < (birthDate.month, birthDate.day))
 
            return age
            
        to_dob =  datetime.datetime.strptime(dob, '%Y-%m-%d')
        age = calculateAge(to_dob)


        error = None
        if check_fname == True or not firstname:
            error = 'Please Enter valid First name'
        if check_lname == True or not lastname:
            error = 'Please Enter valid Last name'
        if not dob or not dob.strip() or age < 18:
            error = 'Error : Candidate should be 18 year old'
        if not aadhar or not aadhar.strip() or isValidAadhaarNumber(aadhar) == False:
            error = 'Error : Aadhar Number is not Valid'
        if not phone or not phone.strip() or isvalidphone(phone) == False:
            error = 'Error : Phone Number is not Valid'        

        if error:
            return  render_template('/candidateregister/candidate_register.html', error = error, first_name=firstname)
        
        if not error:   
            cursor.execute("SELECT * FROM candidate WHERE candidate_aadhaar=%s OR candidate_symbol=%s",(aadhar,symbol))
            rs=cursor.fetchone()
           
            if rs is None:
                res = cursor.execute("INSERT INTO candidate(candidate_name,candidate_lastname,candidate_dob,candidate_gender,candidate_aadhaar,candidate_number,candidate_symbol) VALUES (%s,%s,%s,%s,%s,%s,%s)",(firstname, lastname,dob,gender,aadhar,phone,symbol))
                conn.commit()
                cursor.execute("SELECT max(id) FROM candidate")
                rs=cursor.fetchone()
                cursor.execute("INSERT INTO vote_result(candidate_id,no_of_votes) VALUE(%s,%s)",(rs[0],0))
                conn.commit()
                if res:
                    success_msg = 'Candidate Registered Successfully...'
                return render_template('/candidateregister/candidate_register.html',success_msg=success_msg)
            else :
                return("candidate already exist OR Symbol already exist")    
    else :
        
        return render_template('/candidateregister/candidate_register.html')




@app.route('/voter_register', methods = ['GET', 'POST'])
def voter_register():
    if request.method == 'POST':
        firstname = request.form['first_name']
        lastname = request.form['last_name']
        dob = request.form['birthday']
        gender = request.form['gender']
        aadhar = request.form['aadhar']
        phone = request.form['phone']
        
        # print('Dob is : ',dob)

        check_fname = any(map(str.isdigit, firstname))
        check_lname = any(map(str.isdigit, lastname))

        def isvalidphone(phone_n):
            regex = ("^\(?([7-9]{1})\)?\d{9}$")
            p = re.compile(regex)
            if (phone_n == None):
                return False
            if(re.search(p, phone_n)):
                return True
            else:
                return False

        def isValidAadhaarNumber(str):
            regex = ("^[2-9]{1}[0-9]{3}[0-9]{4}[0-9]{4}$")
            p = re.compile(regex)
            if (str == None):
                return False
            if(re.search(p, str)):
                return True
            else:
                return False

        def calculateAge(birthDate):
            today = date.today()
            age = today.year - birthDate.year -((today.month, today.day) < (birthDate.month, birthDate.day))
 
            return age
            
        to_dob =  datetime.datetime.strptime(dob, '%Y-%m-%d')
        age = calculateAge(to_dob)


        error = None

        error = None
        if check_fname == True or not firstname:
            error = 'Please Enter valid First name'
        if check_lname == True or not lastname:
            error = 'Please Enter valid Last name'
        if not dob or not dob.strip() or age < 18:
            error = 'Error : Candidate should be 18 year old'
        if not aadhar or not aadhar.strip() or isValidAadhaarNumber(aadhar) == False:
            error = 'Error : Aadhar Number is not Valid'
        if not phone or not phone.strip() or isvalidphone(phone) == False:
            error = 'Error : Phone Number is not Valid'       

        if error:
            return  render_template('/voterregister/voter_register.html', error = error, name = phone)

        if not error:    
            createfacedataset()
            cursor.execute("SELECT * FROM voters WHERE voter_aadhar=%s ",(aadhar))
            rs=cursor.fetchone()
            if rs is None:
                res = cursor.execute("INSERT INTO voters(voter_name,voter_lastname,voter_gender,voter_dob,voter_aadhar,voter_phone) VALUES (%s,%s,%s,%s,%s,%s)",(firstname,lastname,gender,dob,aadhar,phone))
                conn.commit()
                if res:
                    success_msg = 'Voter Registered Successfully...'
            # app.run(debug=True)
                return render_template('/voterregister/voter_register.html',success_msg=success_msg)
            else :
                app.run(debug=True)
                return("voter already Exist")
        
    else :
        return render_template('/voterregister/voter_register.html')


@app.route('/vote',methods=['GET','POST'])
def vote(): 
    if request.method == 'POST' :
        
        aadhar=request.form['aadhar']
        cursor.execute("SELECT voter_aadhar from voters WHERE voter_aadhar=%s",(aadhar))
        data = cursor.fetchone()
        if data is not None:
            session["aadhar"]=aadhar
            return redirect(url_for("faceDetect"))
        else :
            flash("voter aadhar does not exist")
    else :
        redirect(url_for("vote"))
    return render_template("vote/vote.html")

@app.route('/faceDetect',methods=['GET','POST'])
def faceDetect():
    
    if request.method == 'POST':
        print("welcome 1")
        a,b=face_identifire()
        print("welcome")
        session['id']=b
        print(a)
        print(b)
        if a==1:
            print(b)
            print(session["aadhar"])
            cursor.execute("SELECT * FROM voters WHERE id=%s AND voter_aadhar=%s AND voter_vote=%s",(b,session["aadhar"],"false"))
            rs=cursor.fetchone()
            if(rs is not None):
                print("b")
                app.run(debug=True)
                return redirect(url_for("votes"))
            elif a==0:
                app.run(debug=True)
                return ("voter does not exist in database or check aadhar and image")

    return render_template("vote/faceDetect.html")

@app.route('/votes',methods=['GET','POST'])
def votes():
    cursor.execute("SELECT id,upper(candidate_name),upper(candidate_lastname),upper(candidate_symbol) FROM candidate")
    result=cursor.fetchall()
    cursor.execute("UPDATE voters SET voters.voter_vote=%s WHERE voters.id=%s",("true",session["id"]))
    conn.commit()
    return render_template("votes/votes.html",result=result)
@app.route('/votessubmit/<string:id>',methods=['GET','POST'])
def votessubmit(id):
    cursor.execute("UPDATE vote_result set no_of_votes=no_of_votes + 1 WHERE candidate_id=%s",([id]))
    conn.commit()
    session.clear()
    return redirect(url_for("index"))



@app.route('/result')
def result():
    cursor.execute("SELECT candidate.candidate_name,candidate.candidate_lastname,candidate.candidate_symbol,vote_result.no_of_votes FROM candidate,vote_result WHERE vote_result.candidate_id=candidate.id order by vote_result.no_of_votes desc limit 1 ")

    result=cursor.fetchall()
    
    return render_template("candidates/result.html",result=result)

@app.route('/declareResult')
def declareResult():
    cursor.execute("SELECT candidate.candidate_name,candidate.candidate_symbol,vote_result.no_of_votes FROM candidate,vote_result WHERE vote_result.candidate_id=candidate.id")

    result=cursor.fetchall()
    xvalues=[]
    yvalues=[]
    for data in result:
            xvalues.append(data[0])
            yvalues.append(data[2])


    return render_template("candidates/declareResult.html",xvalues=xvalues,yvalues=yvalues)

@app.route('/decResult')
def decResult():
    cursor.execute("SELECT candidate.candidate_name,candidate.candidate_symbol,vote_result.no_of_votes FROM candidate,vote_result WHERE vote_result.candidate_id=candidate.id")

    result=cursor.fetchall()
    xvalues=[]
    yvalues=[]
    for data in result:
            xvalues.append(data[0])
            yvalues.append(data[2])


    session["res"]="yes"
    return render_template("candidates/declareResult.html",xvalues=xvalues,yvalues=yvalues)


@app.route('/resetResult')
def resetResult():
    cursor.execute("SELECT candidate.candidate_name,candidate.candidate_symbol,vote_result.no_of_votes FROM candidate,vote_result WHERE vote_result.candidate_id=candidate.id")

    result=cursor.fetchall()
    xvalues=[]
    yvalues=[]
    for data in result:
            xvalues.append(data[0])
            yvalues.append(data[2])

    print(xvalues)
    print(yvalues)

    session["res"]="no"
    
    return render_template("candidates/declareResult.html",xvalues=xvalues,yvalues=yvalues)


@app.route('/VotingStage')
def VotingStage():
    
    return render_template("candidates/votingStage.html")


@app.route('/startVotingStage')
def startVotingStage():
    
    session["startVoting"]="yes"
    
    return render_template("candidates/votingStage.html")

@app.route('/stopVotingStage')
def stopVotingStage():
    
    session["startVoting"]="no"
    
    return render_template("candidates/votingStage.html")


if __name__=="__main__":
    app.run(debug=True)
