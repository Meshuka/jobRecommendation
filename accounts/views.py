from django.contrib.auth import login, logout,authenticate
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from jobrec.models import *
from .forms import JobseekerForm,JobcreatorForm
from django.views.generic import CreateView 

import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import sqlalchemy

engine = sqlalchemy.create_engine('postgresql://postgres:1234@localhost:5432/jobrecdb')

def register(request):
    return render(request, "register.html")
    
class registerUser(CreateView):
    model = User
    form_class= JobseekerForm
    template_name= '../templates/registerUser.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("login")

# class registerUser(CreateView):
#     model = User
#     form_class= JobseekerForm
#     template_name= '../templates/registerUser.html'
    
#     def registerUser(request,id=0):
#         if request.method=="GET":
#             model= User
#             form =JobseekerForm()
#             return render(request,"registerUser.html")
#         else:
#             form=JobseekerForm(request.POST)
#             if form.is_valid():
#             form.save()
#             return redirect("login")

# def updateProfile(request,id):
#     return render(request, '../templates/updateProfile.html' ,{'id':id})

class registerEmp(CreateView):
    model=User
    form_class= JobcreatorForm
    template_name= '../templates/registerEmp.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("login")

def login_view(request):
    if request.method =='POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                if user.is_jobseeker:
                    login(request,user)
                    return redirect('userProfile')
                else:
                    login(request,user)
                    return redirect('empProfile')
            else:
                messages.error(request,"Invalid username or password")
        else:
                messages.error(request,"Invalid username or password")

    return render(request, '../templates/login.html',
    context={'form': AuthenticationForm()})

def logout_view(request):
    logout(request)
    return redirect('/')

def userProfile(request):

    current_user = request.user
    u_id = current_user.id
    u_list = Jobseeker.objects.get(pk=u_id)
    u_skills = u_list.skills

    recm = jobrec.objects.filter(index=u_id)
    if jobrec.objects.filter(index=u_id).exists() == False:
        #df_joblist = pd.read_csv('df_joblist.csv')
        df_joblist = pd.read_sql_table('jobrec_joblisttable',engine,columns=['jobid','jobtitle','advertiserurl','jobdescription','skills','jobstatus','company','joblocation'])
        #tfidf_vectorizer = pickle.load(open('tfidfvec.pkl','rb'))
        #tfidf_jobid = pickle.load(open('tfidfjob.pkl','rb'))
        import nltk
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('stopwords')
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        from nltk import word_tokenize
        import re
        import string

        wn = WordNetLemmatizer()
        stopwords = nltk.corpus.stopwords.words('english')

        def stop_word(word):
                if word not in stopwords:
                    return word

        def clean_txt(text):
            clean_text = []
            clean_text2 = []
            text = re.sub("'", "",str(text))
            text = re.sub("/", " ",str(text))
            for w in word_tokenize(text.lower()):
                if stop_word(w):
                    clean_text.append(wn.lemmatize(w,pos="v"))
            for word in clean_text :
                if stop_word(word):
                    clean_text2.append(word)
            return " ".join(clean_text2)
        
        df_joblist['skills'] = df_joblist['skills'].apply(clean_txt)
        from sklearn.feature_extraction.text import TfidfVectorizer
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_jobid = tfidf_vectorizer.fit_transform(df_joblist['skills']) #fitting and transforming the vector
    
        
      
        
        data = {
            'id':u_id,
            'Key_word':u_skills
        }
        user_q=pd.DataFrame(data,columns=['id','Key_word'],index=['0'])
        z=user_q.id[0]

     


        
        user_tfidf = tfidf_vectorizer.transform(user_q['Key_word'])
        

        cos_similarity_tfidf = map(lambda x: cosine_similarity(user_tfidf, x),tfidf_jobid)
       
        output2 = list(cos_similarity_tfidf)
        #len(output2)

        def get_recommendation(top, df_joblist, scores):
            recommendation = pd.DataFrame(columns=['jobid','jobtitle','advertiserurl','jobdescription','skills','jobstatus','company','joblocation'])
            count = 0
            for i in top:
                recommendation.at[count, 'index'] = z
                recommendation.at[count, 'jobid'] = df_joblist['jobid'][i]
                recommendation.at[count, 'jobtitle'] = df_joblist['jobtitle'][i]
                recommendation.at[count, 'advertiserurl'] = df_joblist['advertiserurl'][i]
                recommendation.at[count, 'score'] =  scores[count]
                recommendation.at[count, 'jobdescription'] = df_joblist['jobdescription'][i]
                recommendation.at[count, 'jobstatus'] = df_joblist['jobstatus'][i]
                recommendation.at[count, 'company'] = df_joblist['company'][i]
                recommendation.at[count, 'joblocation'] = df_joblist['joblocation'][i]
                count += 1
            return recommendation
        top = sorted(range(len(output2)), key=lambda i: output2[i], reverse=True)[:5] #sorted(iterable,key=func,reverse)
        #print(len(output2))
        #print(top)
        list_scores = [output2[i][0][0] for i in top]
        #print(list_scores)
        op=get_recommendation(top,df_joblist, list_scores)

        
        for i in range(len(op)):
            index = op['index'].values[i]
            jobid = op['jobid'].values[i]
            jobtitle = op['jobtitle'].values[i]
            advertiserurl=  op['advertiserurl'].values[i]
            score = op['score'].values[i]
            jobdescription = op['jobdescription'].values[i]
            joblocation = op['joblocation'].values[i]
            company = op['company'].values[i]
            jobstatus = op['jobstatus'].values[i]

    
            rec_info = jobrec(index=index,jobid=jobid,jobtitle=jobtitle,advertiserurl=advertiserurl,score=score,jobdescription=jobdescription,jobstatus=jobstatus,company=company,joblocation=joblocation)
            rec_info.save()


            #current_user = request.user
            #u_id = current_user.id
            #u_list = Jobseeker.objects.get(pk=u_id)
        recm = jobrec.objects.filter(index=u_id)
    else:
        recm = jobrec.objects.filter(index=u_id)
    jobseeker = Jobseeker.objects.get(pk=u_id)

    context = {'recm':recm,'jobseeker':jobseeker}
    

    return render(request, "userProfile.html",context)   

def empProfile(request):
    current_user = request.user
    u_id = current_user.id
    #jobinfo = JoblistTable.objects.get(createruser_id=u_id)
    # if JoblistTable.objects.filter(createruser_id=u_id).exists() == False :
    #     return render(request,"empProfile.html")
    # else:
    jobinfo = JoblistTable.objects.filter(createruser_id=u_id)
    jobcreater = Jobcreator.objects.filter(pk= u_id)
    context = {'jobinfo':jobinfo,'jobcreater':jobcreater}
    return render(request, "empProfile.html",context)  
    