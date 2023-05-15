from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic import View
from .forms import  Upload
from .models import Dataset
import requests
import pandas as pd,numpy as np
import plotly.express as plotly
import random
import string
from time import strftime,gmtime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import io
from reportlab.lib.pagesizes import A4
# Create your views here.
from django.http import FileResponse


domain=''
class MLRT(View):
    
    @staticmethod
    def home(request):
        
        global domain
        domain='http://'+str(request.get_host())
        if request.method=="POST":
            form=Upload(request.POST,request.FILES)
            file=request.FILES['file']
            if '.csv'  in str(file) :
                data=Dataset.objects.create(dataset=file)         
                data.save()                
                data='{}/media/{}'.format(domain,str(file))
                response=requests.get('{}/api/read_dataset/?data={}'.format(domain,data))
                response=response.json()
                data=(response['data'])                            
                column_name=(response['column_name'])               
                filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
                with open('media/track_files/{}'.format(filename),'w') as f:  
                    f.write(str(['Data and Time','Description']))       
                    f.write(',["{}"'.format(strftime("%d-%m-%Y %H:%M:%S",gmtime()))+',"New .csv file is loaded with {} name"]'.format(str(file)))
                    f.close()            
                return render(request,'MLAPP/unwanted_column.html',{'column_name':column_name,'data':data,'track_filename':filename})       
        upload=Upload()
        return render(request,'MLAPP/main.html',{'form':upload})
    
    @staticmethod
    def missing_value(request,skip=0):
        column_name=eval(request.POST.get('column_name'))
        data=eval(request.POST.get('data'))
        track_filename=request.POST.get('track_filename')
        if request.POST.get('skip'):
            temp=pd.DataFrame(data)
            temp.columns=column_name
            temp=temp.select_dtypes(include='object')
            if len(temp)==0:
                temp.append('No Columns')
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Skipped and Redirect to Label Encoding step'))
            return render(request,'MLAPP/label_encoding.html',{'column_name':column_name,'data':data,'cat_column_name':temp,'is_abr':False,'track_filename':track_filename})
        col = request.POST['option']
        option=request.POST['option1']
        is_na=pd.DataFrame(data)
        is_na.columns=column_name
        is_na=is_na.replace('NaN',np.nan,regex=True)   
        string=''
        if str(option)=='Mean':            
            string='{}/api/mean_value/'.format(domain)
        elif str(option)=='Median':
            string='{}/api/median_value/'.format(domain)            
        elif str(option)=='Mode':
            string='{}/api/mode_value/'.format(domain)           
        elif str(option)=="'0' Value":
            string='{}/api/zero_value/'.format(domain)           
        elif str(option)=='Delete Row':
            string='{}/api/del_na_row/'.format(domain)       
        response3=requests.get('{}?data={}&target_column={}&column_name={}'.format(string,data,col,column_name))
        temp=response3.json()
        data=temp['data']
        column_name=temp['column_name']
        response1=requests.get('{}/api/check_null_values/?data={}'.format(domain,data))
        null_val=response1.json()
        null_val=null_val['check']
        j=0        
        list=[]
        for i in column_name:
            temp=[i,null_val[j]]
            j=j+1
            list.append(temp)
        requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Handled missing values of {} column by {} value'.format(col,str(option))))
        return render(request,'MLAPP/missing_values.html',{'column_name':column_name,'null_val':list,'data':data,'track_filename':track_filename})

    @staticmethod
    def unwanted_column(request,skip=0):
        column_name=request.POST.get('column_name')
        track_filename=request.POST.get('track_filename')
        data=eval(request.POST.get('data'))
        if request.POST.get('skip'):
            response1=requests.get('{}/api/check_null_values/?data={}'.format(domain,data))
            null_val=response1.json()
            null_val=null_val['check']
            j=0
            list=[]
            column_name=eval(column_name)
            for i in column_name:
                temp=[i,null_val[j]]
                j=j+1
                list.append(temp)
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Skip and Redirect to Handle Missing Values step'))
            return render(request,'MLAPP/missing_values.html',{'column_name':column_name,'data':data,'null_val':list,'track_filename':track_filename})    
        target_col = request.POST['option']        
        response4=requests.get('{}/api/unwanted_column/?data={}&target_col={}&column_name={}'.format(domain,data,target_col,column_name))       
        temp=response4.json()
        requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'{}column removed from data'.format(target_col)))
        return render(request,'MLAPP/unwanted_column.html',{'column_name':temp['column_name'],'data':temp['data'],'track_filename':track_filename})

    
    @staticmethod
    def outliers(request,skip=0): 
        print('enter')       
        column_name=eval(request.POST.get('column_name')  )     
        data=eval(request.POST.get('data'))
        is_abr=eval(request.POST.get('is_abr'))
        try:
            abr=eval(request.POST.get('abr'))
        except:
            abr={}
        track_filename=request.POST.get('track_filename')        
        if request.POST.get('skip'):
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Skip and Redirect to Scaling step'))
            return render(request,'MLAPP/scaling.html',{'column_name':column_name,'data':data,'is_abr':False,'track_filename':track_filename,'abr':abr,'is_abr':is_abr})
        col = request.POST['option']
        print('exit')
        try:
            less = eval(request.POST['less'])
            more = eval(request.POST['more']      )  
        except:
            less="None"
            more="None"
        if less=='None' and more=='None':
            response4=requests.get('{}/api/detect_outliers/?data={}&target_column={}&column_name={}'.format(domain,data,col,column_name))            
            temp=response4.json()
            file_url=temp['file_url']
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Checking outliers for {} column '.format(col)))
            return render(request,'MLAPP/outlier.html',{'column_name':column_name,'data':data,'file_url':file_url,'detect':True,'select_col':col,'is_abr':is_abr,'abr':abr,'track_filename':track_filename})
        else:
            selected_col = request.POST['option3']            
            response4=requests.get('{}/api/remove_outliers/?data={}&target_column={}&column_name={}&less={}&more={}'.format(domain,data,selected_col,column_name,less,more))
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Removing outliers for {} column with values less than {} and greater than {}'.format(col,less,more)))
            temp=response4.json()
            data=temp['data']
            column_name=temp['column_name']
            print(is_abr,abr)
            return render(request,'MLAPP/outlier.html',{'column_name':column_name,'data':data,'detect':False,'is_abr':is_abr,'abr':abr,'track_filename':track_filename})
     

    @staticmethod
    def label_encoding(request,skip=0):
        column_name=eval(request.POST.get('column_name'))
        data=eval(request.POST.get('data'))
        track_filename=request.POST.get('track_filename')
        is_abr=eval(request.POST.get('is_abr'))
        if request.POST.get('skip'):
            if is_abr:
                abr=eval(request.POST.get('abr'))
                requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Skipped and Redirect to outlier step'))

                return render(request,'MLAPP/outlier.html',{'column_name':column_name,'data':data,'is_abr':True,'abr':abr,'detect':False,'track_filename':track_filename})
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Skipped and Redirect to outlier step'))
            return render(request,'MLAPP/outlier.html',{'column_name':column_name,'data':data,'is_abr':False,'detect':False,'track_filename':track_filename})
                

        col = request.POST['option']

        if col in column_name:         
            response4=requests.get('{}/api/label_encoding/?data={}&target_column={}&column_name={}'.format(domain,data,col,column_name))
            temp=response4.json()
            data=temp['data']
            column_name=temp['column_name']
            is_abr=eval(request.POST.get('is_abr')) 
            if is_abr:
                abr=eval(request.POST.get('abr')) 
            else: 
                abr=dict()
            abbrevation=temp['abrevation']
            
            abr[col]=abbrevation
           
            temp=pd.DataFrame(data)
            temp.columns=column_name
            temp=temp.select_dtypes(include='object')
            if len(temp)==0:
                temp.append('No Columns')
            
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Done Label Encoding of {} column name from data'.format(col)))
            return render(request,'MLAPP/label_encoding.html',{'column_name':column_name,'data':data,'cat_column_name':temp,'is_abr':True,'abr':abr,'track_filename':track_filename})
    @staticmethod
    def scaling(request):
        column_name=eval(request.POST.get('column_name'))
        data=eval(request.POST.get('data'))
        track_filename=request.POST.get('track_filename')     
        target_column = request.POST['option']
        option=request.POST['option1']
        response4=requests.get('{}/api/scaling/?data={}&target_column={}&column_name={}&option={}'.format(domain,data,target_column,column_name,option))      
        temp=response4.json()
        feature_name=temp['feature_name'] 
        feature_data=temp['feature_data']
        target_data=temp['target_data']
        target_name=temp['target_name']
        is_abr=eval(request.POST.get('is_abr'))
        try:
            abr=eval(request.POST.get('abr'))
        except:
            abr={}
        requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Data splitted into Feature and Target data'))            
        requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Done Scaling with choosing {} as target column by {} method'.format(target_column,option)))
        return render(request,'MLAPP/train_test.html',{'data':data,'column_name':column_name,'feature_name':feature_name,'feature_data':feature_data,'target_name':target_name,'target_data':target_data,'scaler_type':option,'is_abr':is_abr,'abr':abr,'track_filename':track_filename})

    @staticmethod
    def train_test(request):       
        column_name=eval(request.POST.get('column_name')        )
        data=eval(request.POST.get('data'))
        track_filename=request.POST.get('track_filename')
        feature_name=eval(request.POST.get('feature_name'))
        feature_data=eval(request.POST.get('feature_data'))
        target_name=request.POST.get('target_name')
        target_data=eval(request.POST.get('target_data'))
        scaler_type=request.POST.get('scaler_type')
        is_abr=eval(request.POST.get('is_abr'))
        try:
            abr=eval(request.POST.get('abr'))
        except:
            abr={}
        test_size=request.POST['test_size']
        response4=requests.get('{}/api/train_test/?feature_data={}&target_data={}&test_size={}'.format(domain,feature_data,target_data,test_size))       
        temp=response4.json()
        feature_train=temp['feature_train']
        feature_test=temp['feature_test']
        target_train=temp['target_train']
        target_test=temp['target_test']
        requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'With choosing {} as test size data is splitted into feature_train,feature_test,target_train,target_test'.format(test_size))) 
        return render(request,'MLAPP/model_building.html',{'data':data,'column_name':column_name,'feature_train':feature_train,'feature_test':feature_test,'target_train':target_train,'target_test':target_test,'feature_name':feature_name,'target_name':target_name,'model_generate':False,'feature_data':feature_data,'target_data':target_data,'scaler_type':scaler_type,'is_abr':is_abr,'abr':abr,'track_filename':track_filename})


    @staticmethod
    def model_building(request,predict=0):
        
        column_name=eval(request.POST.get('column_name'))
        data=eval(request.POST.get('data'))
        feature_name=eval(request.POST.get('feature_name'))
        feature_data=eval(request.POST.get('feature_data'))
        target_name=(request.POST.get('target_name'))
        target_data=eval(request.POST.get('target_data'))
        feature_train=eval(request.POST.get('feature_train'))
        feature_test=eval(request.POST.get('feature_test'))
        target_train=eval(request.POST.get('target_train'))
        target_test=eval(request.POST.get('target_test'))
        scaler_type=request.POST.get('scaler_type')
        track_filename=request.POST.get('track_filename')     
        model_name=request.POST['model_name']
        if predict==1:
            model_path=request.POST['model_path']           
            is_abr=eval(request.POST.get('is_abr'))
            try:
                 abr=eval(request.POST.get('abr'))
            except:
                abr={} 
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'Continuing with {} model  redirect to predict step'.format(model_name)))
            return render(request,'MLAPP/predict.html',{'feature_train':feature_train,'feature_test':feature_test,'target_train':target_train,'target_test':target_test,'feature_name':feature_name,'target_name':target_name,'model_path':model_path,'model_name':model_name,'data':data,'column_name':column_name,'feature_data':feature_data,'target_data':target_data,'scaler_type':scaler_type,'is_abr':is_abr,"abr":abr,'track_filename':track_filename})   
      
        response4=requests.get('{}/api/model_building/?feature_train={}&target_train={}&feature_test={}&target_test={}&model_name={}'.format(domain,feature_train,target_train,feature_test,target_test,model_name))
       
        temp=response4.json()
        feature_train=temp['feature_train']
        feature_test=temp['feature_test']
        target_train=temp['target_train']
        target_test=temp['target_test']
        is_diagram=temp['is_diagram']
        
        model_path=temp['model_path']
        
        accuracy=temp['accuracy']
        if is_diagram==True:
            precision=temp['precision']
            recall=temp['recall']
            cm_path=temp['cm_path']
            is_abr=eval(request.POST.get('is_abr'))
            try:
                abr=eval(request.POST.get('abr'))
            except:
                abr={}
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'{} model is build with precision score {},recall score {},and accurracy score {}'.format(model_name,precision,recall,accuracy)))
            return render(request,'MLAPP/model_building.html',{'feature_train':feature_train,'feature_test':feature_test,'target_train':target_train,'target_test':target_test,'feature_name':feature_name,'target_name':target_name,'model_generate':True,'cm_path':cm_path,'model_path':model_path,'precision':precision,'recall':recall,'accuracy':accuracy,'model_name':model_name,'is_diagram':True,'data':data,'column_name':column_name,'feature_data':feature_data,'target_data':target_data,'scaler_type':scaler_type,'is_abr':is_abr,'abr':abr,'track_filename':track_filename})
        is_abr=eval(request.POST.get('is_abr'))
        try:
            abr=eval(request.POST.get('abr'))
        except:
            abr={}
        requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'{} model is build with accurracy score {}'.format(model_name,accuracy)))
        return render(request,'MLAPP/model_building.html',{'feature_train':feature_train,'feature_test':feature_test,'target_train':target_train,'target_test':target_test,'feature_name':feature_name,'target_name':target_name,'model_generate':True,'is_diagram':False,'model_path':model_path,'accuracy':accuracy,'model_name':model_name,'data':data,'column_name':column_name,'feature_data':feature_data,'target_data':target_data,'scaler_type':scaler_type,'is_abr':is_abr,"abr":abr,'track_filename':track_filename})

    @staticmethod
    def predict(request):
        is_abr=eval(request.POST.get('is_abr'))
        is_abr=eval(request.POST.get('is_abr'))
        try:
            abr=eval(request.POST.get('abr'))
        except:
            abr={}
        track_filename=request.POST.get('track_filename')
        column_name=eval(request.POST.get('column_name'))
        data=eval(request.POST.get('data'))
        feature_name=eval(request.POST.get('feature_name'))
        feature_data=eval(request.POST.get('feature_data'))
        target_name=request.POST.get('target_name')
        target_data=eval(request.POST.get('target_data'))
        feature_train=eval(request.POST.get('feature_train'))
        feature_test=eval(request.POST.get('feature_test'))
        target_train=eval(request.POST.get('target_train'))
        target_test=eval(request.POST.get('target_test'))
        model_path=request.POST.get('model_path')
        model_name=request.POST.get('model_name')
        scaler_type=request.POST.get('scaler_type')   
        if request.method=="POST":
            pred=[]
            input1=[]           
            for i in feature_name:   
                j=request.POST.get(i)
               
                pred.append(eval(j))
                input1.append([i,j])           
            response4=requests.get('{}/api/predict/?model_path={}&pred={}&scaler_type={}&data={}&column_name={}&target_name={}'.format(domain,model_path,pred,scaler_type,data,column_name,target_name))
       
            temp=response4.json()
            result=temp['result'][0]
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'With model name {} ,{} this values are passed and model predict {}'.format(model_name,pred,result)))
            return render(request,'MLAPP/predict.html',{'is_result':True,'input':input1,'result':result,'feature_train':feature_train,'feature_test':feature_test,'target_train':target_train,'target_test':target_test,'feature_name':feature_name,'target_name':target_name,'model_generate':True,'model_path':model_path,'model_name':model_name,'data':data,'column_name':column_name,'feature_data':feature_data,'target_data':target_data,'scaler_type':scaler_type,'track_filename':track_filename,'abr':abr,'is_abr':is_abr})
        
        return render(request,'MLAPP/predict.html',{'is_result':False,'model_path':model_path,'model_name':model_name,'feature_name':feature_name,'scaler_type':scaler_type,'is_abr':is_abr,'abr':abr,'track_filename':track_filename,'feature_train':feature_train,'feature_test':feature_test,'target_train':target_train,'target_test':target_test,'feature_name':feature_name,'target_name':target_name,'model_generate':True,'model_path':model_path,'model_name':model_name,'data':data,'column_name':column_name,'feature_data':feature_data,'target_data':target_data,'scaler_type':scaler_type,'track_filename':track_filename,'abr':abr,'is_abr':is_abr})
        
    @staticmethod
    def download(request):
        track_filename=request.POST.get('track_filename')
        if request.POST.get('action')=='csv':
            ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
            ran=str(ran)+'.xlsx'
            writer = pd.ExcelWriter('media/csv/{}'.format(ran), engine='xlsxwriter')
            column_name=request.POST.get('column_name')
            column_name=eval(column_name)
            data=request.POST.get('data')
            data=eval(data)
            feature_name=request.POST.get('feature_name')
            feature_name=eval(feature_name)
            feature_data=request.POST.get('feature_data')
            feature_data=eval(feature_data)
            target_name=request.POST.get('target_name')
            target_data=request.POST.get('target_data')
            target_data=eval(target_data)
            feature_train=request.POST.get('feature_train')
            feature_train=eval(feature_train)
            feature_test=request.POST.get('feature_test')
            feature_test=eval(feature_test)
            target_train=request.POST.get('target_train')
            target_train=eval(target_train)
            target_test=request.POST.get('target_test')
            target_test=eval(target_test)
            data=pd.DataFrame(data)
            
            data.columns=column_name
            data.to_excel(writer, sheet_name='Data')
            feature_data=pd.DataFrame(feature_data)
            feature_data.columns=feature_name
            feature_data.to_excel(writer, sheet_name='Feature Data')
            target_data=pd.DataFrame(target_data)
            target_data.columns=[target_name]
            target_data.to_excel(writer, sheet_name='Target Data')
            feature_train=pd.DataFrame(feature_train)
            feature_train.columns=feature_name
            feature_train.to_excel(writer, sheet_name='Feature Train')
            feature_test=pd.DataFrame(feature_test)
            feature_test.columns=feature_name
            feature_test.to_excel(writer, sheet_name='Feature Test')
            target_train=pd.DataFrame(target_train)
            target_train.columns=[target_name]
            target_train.to_excel(writer, sheet_name='Target Train')
            target_test=pd.DataFrame(target_test)
            target_test.columns=[target_name]
            target_test.to_excel(writer, sheet_name='Target Test')
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'.csv file is downloaded with {} name'.format(ran)))


            writer.save()
            return redirect('{}/media/csv/{}'.format(domain,ran))
        elif request.POST.get('action')=='pdf':
            requests.get('{}/api/track_file/?track_filename={}&message={}'.format(domain,track_filename,'PDF  file is downloaded with MLRT_info.pdf name'))
            pdf_file = open('media/pdf/MLRT_info.pdf', 'rb')
            response = FileResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="MLRT_info.pdf"'
            return response
        else:
            requests.get('{}/api/track_pdf/?track_filename={}'.format(domain,track_filename))
            pdf_file = open('media/pdf/{}.pdf'.format(track_filename), 'rb')
            response = FileResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(track_filename)
            return response

            

        

        

            

    
       

        

                
        
        
        
        
    