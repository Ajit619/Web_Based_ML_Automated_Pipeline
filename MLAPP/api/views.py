from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
import pandas as pd,numpy as np
import plotly.express as plotly
from sklearn.preprocessing import LabelEncoder,StandardScaler,MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression,LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier,DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
import string    
import random
from yellowbrick.classifier import ConfusionMatrix
from sklearn.metrics import precision_score,recall_score
import pickle
from time import strftime,gmtime
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import io
from reportlab.lib.pagesizes import A4
from textwrap import wrap
import plotly.io as pio
@api_view(('GET',))
def read_dataset(request,data="none"):
    global domain
    domain='http://'+str(request.get_host())   
    data=pd.read_csv((request.query_params['data']).replace(' ', '_'))
    data.fillna('NaN',inplace=True)
    column_name=data.columns
    data=data.to_numpy()
    return Response({"column_name":column_name,"data":data},content_type='application/json')

@api_view(('GET',))
def mean_value(request):
    data=eval(request.query_params['data'])
    target_col=(request.query_params['target_column'])
    column_name=eval(request.query_params['column_name']) 
    data=pd.DataFrame(data)
    data.columns=column_name
    data=data.replace('NaN',np.nan,regex=True)    
    data[target_col]=data[target_col].fillna(data[target_col].mean())   
    data=data.to_numpy()
    return Response({"column_name":column_name,"data":data},content_type='application/json')
@api_view(('GET',))
def mode_value(request):
    data=eval(request.query_params['data'])
    target_col=(request.query_params['target_column'])
    column_name=eval(request.query_params['column_name'])
    data=pd.DataFrame(data)
    data.columns=column_name
    data=data.replace('NaN',np.nan,regex=True)
    data[target_col]=data[target_col].fillna(data[target_col].mode()[0])
    data=data.to_numpy()
    return Response({"column_name":column_name,"data":data},content_type='application/json')

@api_view(('GET',))
def median_value(request):
    data=eval(request.query_params['data'])
    target_col=(request.query_params['target_column'])
    column_name=eval(request.query_params['column_name'])
    data=pd.DataFrame(data)
    data.columns=column_name
    data=data.replace('NaN',np.nan,regex=True)
    data[target_col]=data[target_col].fillna(data[target_col].median())
    data=data.to_numpy()
    return Response({"column_name":column_name,"data":data},content_type='application/json')

@api_view(('GET',))
def zero_value(request):
    data=eval(request.query_params['data'])
    target_col=(request.query_params['target_column'])
    column_name=eval(request.query_params['column_name'])
    data=pd.DataFrame(data)
    data.columns=column_name
    data=data.replace('NaN',np.nan,regex=True)
    data[target_col]=data[target_col].fillna(0)
    data=data.to_numpy()
    return Response({"column_name":column_name,"data":data},content_type='application/json')

@api_view(('GET',))
def del_na_row(request):
    data=eval(request.query_params['data'])
    column_name=eval(request.query_params['column_name'])
    data=pd.DataFrame(data)
    data.columns=column_name
    data=data.replace('NaN',np.nan,regex=True)
    data=data.dropna()
    data=data.to_numpy()
    return Response({"column_name":column_name,"data":data},content_type='application/json')

@api_view(('GET',))
def check_null_values(request):
    temp=eval(str(request.query_params['data']))
    data=pd.DataFrame(temp)
    data=data.replace('NaN',np.nan,regex=True)
    temp=data.isnull().sum()
    data=data.fillna('NaN')
    temp.to_numpy()
    return Response({"check":temp})

@api_view(('GET',))
def unwanted_column(request):
    temp=(request.query_params['data'])
    target_col=(request.query_params['target_col'])
    column_name=(request.query_params['column_name'])
    temp=eval(temp)
    column_name=eval(column_name)
    temp=pd.DataFrame(temp)
    temp.columns=column_name
    temp=temp.replace('NaN',np.nan,regex=True)
    # temp[target_col]=temp[target_col].fillna(temp[target_col].mean())
    temp=temp.drop([target_col], axis=1)
    temp=temp.fillna('NaN')

    column_name=temp.columns
    column_name=column_name.to_numpy()
    temp=temp.to_numpy()
    return Response({"column_name":column_name,"data":temp},content_type='application/json')

@api_view(('GET',))
def detect_ouliers(request):
    data=eval(request.query_params['data'])
    print(1)
    target_col=(request.query_params['target_column'])
    print(2)
    column_name=eval(request.query_params['column_name'])
    
    data=pd.DataFrame(data)
  
    data.columns=column_name

    fig=plotly.box(data[target_col])    
    
    pio.write_image(fig,'media/images/{}.png'.format(target_col))
   
    url='{}/media/images/{}.png'.format(domain,target_col)    
   
    return Response({"file_url":url},content_type='application/json')

@api_view(('GET',))
def remove_outliers(request):
    data=eval(request.query_params['data'])
    target_col=(request.query_params['target_column'])
    column_name=eval(request.query_params['column_name'])
    less=eval(request.query_params['less'])
    more=eval(request.query_params['more'])
    data=pd.DataFrame(data)
    data.columns=column_name
    if less!='None':
        data= data.drop(data[data[target_col] < less].index)
    if more !='None':
        data= data.drop(data[data[target_col] > more].index)
    data=data.to_numpy()
    return Response({"column_name":column_name,"data":data},content_type='application/json')
    
    
@api_view(('GET',))
def label_encoding(request):
    data=eval(request.query_params['data'])
    target_col=(request.query_params['target_column'])
    column_name=eval(request.query_params['column_name'])
    data=pd.DataFrame(data)
    data.columns=column_name
    encoder=LabelEncoder()
    abr=data[target_col]    
    abr=abr.drop_duplicates().to_list()
    abrevation=[]
    inc=0    
    for i in abr:       
        abrevation.append([i,inc])        
        inc=inc+1
    data[target_col]=encoder.fit_transform(data[target_col])
    data=data.to_numpy()
    return Response({"column_name":column_name,"data":data,"abrevation":abrevation},content_type='application/json')

@api_view(('GET',))
def scaling(request):
    temp=eval(request.query_params['data'])
    target_col=(request.query_params['target_column'])
    column_name=eval(request.query_params['column_name'])
    option=(request.query_params['option'])
    temp=pd.DataFrame(temp)
    temp.columns=column_name
    target_var=temp[target_col].to_numpy()    
    feature_var=temp.drop([target_col],axis=1)
    if str(option)=="MinMax Scaling":
        scaler=MinMaxScaler()
    else:
        scaler=StandardScaler()
    feature_var=scaler.fit_transform(feature_var)
    feature_var=np.round(feature_var,10)
    feature_var=pd.DataFrame(feature_var).to_numpy()
    column_name.remove(target_col)
    return Response({"feature_data":feature_var,'feature_name':column_name,"target_data":target_var,'target_name':target_col},content_type='application/json')
@api_view(('GET',))
def train_test(request):
    feature_data=eval(request.query_params['feature_data'])
    target_data=eval(request.query_params['target_data'])
    test_size=eval(request.query_params['test_size'])
    feature_train, feature_test,target_train, target_test = train_test_split(feature_data,target_data ,random_state=104, test_size=test_size,shuffle=True) 
    return Response({"feature_train":feature_train,'feature_test':feature_test,"target_train":target_train,'target_test':target_test},content_type='application/json')

@api_view(('GET',))
def model_building(request):
    feature_train=(request.query_params['feature_train'])
    target_train=(request.query_params['target_train'])
    model_name=(request.query_params['model_name'])
    feature_test=(request.query_params['feature_test'])
    target_test=(request.query_params['target_test'])
    

    feature_train=eval(feature_train)
    
    target_train=eval(target_train)
    feature_test=eval(feature_test)
    target_test=eval(target_test)
   
    if model_name=='Linear Regression':
        model=LinearRegression()
    if model_name=='Logistic Regression':
        model=LogisticRegression()
    if model_name=='Decision Tree Regressor':
        model=DecisionTreeRegressor()
    if model_name=='Decision Tree Classifier':
        model=DecisionTreeClassifier()
    if model_name=='Random Forest Regressor':
        model=RandomForestRegressor()
    if model_name=='Random Forest Classifier':
        model=RandomForestClassifier()
    if model_name=='Support Vector Machine':
        model=SVC()
    model.fit(feature_train,target_train)
    y_pred=model.predict(feature_test)
    accuracy=model.score(feature_test,target_test)
    accuracy=round(accuracy,2)
    
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
    ran=str(ran)
    pickle.dump(model, open('media/models/{}.svg'.format(ran), 'wb'))
    model_url='{}/media/models/{}.svg'.format(domain,ran)
    if model_name=='Support Vector Machine' or model_name=='Random Forest Classifier' or model_name=='Decision Tree Classifier' or model_name=='Logistic Regression':
        precision=precision_score(target_test,y_pred,average='macro')
        precision=round(precision,2)
    
        recall=recall_score(target_test,y_pred,average='macro')
        recall=round(recall,2)
        cm = ConfusionMatrix(model)
        
        cm.fit(feature_train,target_train)
        cm.score(feature_test,target_test)

        cm.show(outpath='media/images/{}'.format(ran),clear_figure=True)
        cm_path='{}/media/images/{}.png'.format(domain,ran)
        
        
        return Response({"feature_train":feature_train,'feature_test':feature_test,"target_train":target_train,'target_test':target_test,'cm_path':cm_path,'model_path':model_url,'accuracy':accuracy,'is_diagram':True,'precision':precision,'recall':recall},content_type='application/json')
        
    return Response({"feature_train":feature_train,'feature_test':feature_test,"target_train":target_train,'target_test':target_test,'model_path':model_url,'accuracy':accuracy,'is_diagram':False},content_type='application/json')
@api_view(('GET',))
def predict(request):
    model_path=(request.query_params['model_path'])
    scaler_type=(request.query_params['scaler_type'])
    data=eval(request.query_params['data'])
    column_name=eval(request.query_params['column_name'])
    target_name=(request.query_params['target_name'])
    
    data=pd.DataFrame(data)
    data.columns=column_name
    feature_data=data.drop([target_name],axis=1)
    model_path='media'+str(model_path).split('media')[1]
    pred=(request.query_params['pred'])
    pred=eval(pred)
    loaded_model = pickle.load(open(model_path, 'rb'))

    if scaler_type=="Minmax Scaling":
        scaler=MinMaxScaler()
    else:
        scaler=StandardScaler()
    scaler.fit(feature_data)
    scaler.transform(feature_data)
    n=scaler.transform([pred])
    y_pred=loaded_model.predict(n)
    return Response({'result':y_pred},content_type='application/json')
@api_view(('GET',))
def track_file(request):
    filename=(request.query_params['track_filename'])
    message=(request.query_params['message']) 
    message = wrap(message, width=85)
    message="\n".join(message)
    temp=str(['{}'.format(strftime("%Y-%m-%d %H:%M:%S",gmtime())),message])
    with open('media/track_files/{}'.format(filename),'a') as f:         
                    f.write((','+str(['{}'.format(strftime("%d-%m-%Y %H:%M:%S",gmtime())),message])))
                    f.close()
    return Response({"Message":'Done'},content_type='application/json')
@api_view(('GET',))
def track_pdf(request):
    filename=(request.query_params['track_filename'])
    file1 = open('media/track_files/{}'.format(filename),"r")
    data=eval(file1.read())
    file1.close()
    df = pd.DataFrame(data[1:], columns=data[0])
    df.index.name='Step No.'
    df.reset_index(inplace=True)
    pdf_buffer = io.BytesIO()
    pdf_buffer = io.BytesIO()
    p = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    headline = Paragraph("Traceable Data",ParagraphStyle(name='center', alignment=TA_CENTER,fontSize=20,keepWithNext=True,spaceAfter=20))
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    tblstyle = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                  ('ALIGNMENT', (0, 0), (0, -1), 'CENTER'),
                                ('ALIGNMENT', (2, 0), (-1, -1), 'LEFT'),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black),
                               ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
                                   ('FONTSIZE', (0, 0), (-1, -1), 10)])
    for i in range(1,len(data)):
            if i%2 == 0:
                tblstyle.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
            else:
                tblstyle.add('BACKGROUND', (0, i), (-1, i), colors.white)
    table.setStyle(tblstyle)
    p.build([headline, table])
    pdf_data = pdf_buffer.getvalue()
    with open('media/pdf/{}.pdf'.format(filename), "wb") as f:
            f.write(pdf_data)      
    return Response({"filename":filename},content_type='application/json')   
   
    

    


