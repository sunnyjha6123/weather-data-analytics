import requests #this  library helps to fetch datas from api
import pandas as pd #pandas for handling and analysing data
import  numpy as  np #for  numerical operations
from sklearn.model_selection import train_test_split  #to split data into trainning and testing  sets
from sklearn.preprocessing import LabelEncoder#to convert categoriticsl data
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor #models  for  classification and rigression  tasks
from sklearn.metrics import accuracy_score #to measure  the  accurecy of aur predctions
from datetime import datetime, timedelta #to andle  date and ti,me
import pytz

API_KEY ='36c0c2b35085f8e0e8de2514cd44e539' 
BASE_URL ='https://api.openweathermap.org/data/2.5/' #base  url formakin api request

#Fetch current weather  data
def get_current_weather(city):
    url =  f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metrics" #construct the APIrequest URL
    response = requests.get(url) #send the getr  request5 to  api
    data = response.json()
    return {
        'city':data['name'],
        'current_temp':round(data['main']['temp']),
        'feels_like':round(data['main']['temp']),
        'temp_min': round(data['main']['temp_min']),
        'temp_max': round(data['main']['temp_max']),
        'humidity':round(data['main']['humidity']),
        'temp_map':round(data['main']['temp_max']),
        'description':data['weather'][0]['description'],
        'description':data['weather'][0]['description'],
        'country': data['sys']['country'],
        'wind_gust_dir':data['wind']['deg'],
        'pressure':data['main']['pressure'],
        'wind_gust_speed':data['wind']['speed']
    }
def read_historical_data(filename):
    df = pd.read_csv(filename)#load csv file into datafr4ame
    df= df.drop_duplicates()
    return df
def  prepare_data(data):
    print(data.columns)
    data = data.dropna()
    le=LabelEncoder() #create a label encoderinstance
    #data['Wind_Bearing']=le.fit_transform(data['Wind_Bearing'])
    data['normalized_label']=le.fit_transform(data['normalized_label'])
    x= data[['Pressure','global_radiation','temp_mean(c)','temp_min(c)','temp_max(c)','Wind_Speed','Wind_Bearing']]#feature  variablews
    y =data['normalized_label']
    return x,y,le #tretrurn fesature vsriable tsserhget variable and the label encodere
def train_rain_model(x,y):
    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=42)
    model = RandomForestClassifier(n_estimators=100,random_state=42)
    model.fit(x_train,y_train)
    y_pred = model.predict(x_test) 
    print("Accuracy:",accuracy_score(y_test,y_pred))
    #print('mean squared error for rain model')
    #print(mean_squared_error(y_test,y_pred)) 
    return model
def prepare_regression_data(data,feature):
    x,y=[],[]
    for i in range(len(data)-1):
        x.append(data[feature].iloc[i])
        y.append(data[feature].iloc[i+1])
    x=np.array(x).reshape(-1,1)
    y=np.array(y)
    return x,y
def train_regression_model(x,y):
    model=RandomForestClassifier(n_estimators=100,random_state=42)
    model.fit(x,y)
    return model
def  predict_future(model,current_value):
    predictions = [current_value]
    for i in range(5):
        next_value = model.predict(np.array([[predictions[-1]]]))
        predictions.append(next_value[0])
        return predictions[1:]
def  weather_view():
     city =input('enter any city name:')
     current_weather = get_current_weather(city)
     historical_data =read_historical_data('data/weather.csv.csv')
     x ,y, le = prepare_data(historical_data)
     rain_model = train_rain_model(x,y)
    # map w2ind direction campass points
     wind_deg = current_weather['wind_gust_dir'] % 360
     compass_points = [
    ("N", 0, 11.25), ("NNE", 11.25, 33.75), ("NE", 33.75, 56.25),
    ("ENE", 56.25, 78.75), ("E", 78.75, 101.25), ("ESE", 101.25, 123.75),
    ("SE", 123.75, 146.25), ("SSE", 146.25, 168.75), ("S", 168.75, 191.25),
    ("SSW", 191.25, 213.75), ("SW", 213.75, 236.25), ("WSW", 236.25, 258.75),
    ("W", 258.75, 281.25), ("WNW", 281.25, 303.75), ("NW", 303.75, 326.25),
    ("NNW", 326.25, 348.75)
]
     compass_direction = next(point for point, start, end in compass_points if start <= wind_deg < end)
     compass_direction_encoded = le.transform([compass_direction])[0] if compass_direction in le.classes_ else-1
     current_data= {
    'mintemp':current_weather['temp_min'],
    'maxtemp':current_weather['temp_max'],
    'windgustdir':compass_direction_encoded,
    'windgustspeed':current_weather['wind_gust_speed'],
    'humidity':current_weather['humidity'],
    'pressure':current_weather['pressure'],
    'temp':current_weather['current_temp'],
    }
     print(current_weather)
     current_df = pd.DataFrame({'Pressure':[current_weather['pressure']],'global_radiation':[0],'temp_mean(c)':[current_weather['current_temp']],'temp_min(c)':[current_weather['temp_min']],'temp_max(c)':[current_weather['temp_max']],'Wind_Speed':[current_weather['wind_gust_speed']],'Wind_Bearing':[current_weather['wind_gust_dir']]})
     rain_prediction= rain_model.predict(current_df)[0]
     x_temp,y_temp=prepare_regression_data(historical_data,'temp_mean(c)')
     #x_hum,y_hum=prepare_regression_data(historical_data,'humidity')
     temp_model = train_regression_model(x_temp,y_temp)
     #hum_model = train_regression_model(x_hum,y_hum)
     future_temp = predict_future(temp_model,current_weather['temp_min'])
     #future_humidity = predict_future(hum_model,current_weather['humidity'])
     timezone = pytz.timezone('Asia/Kolkata')
     now=datetime.now(timezone)
     next_hour = now+ timedelta(hours=1)
     next_hour = next_hour.replace(minute=0,second=0,microsecond=0)
     future_times = [(next_hour + timedelta(hours=i)).strftime("%H:00") for i in range(5)]
     print(f"city:{city},{current_weather['country']}")
     print(f"current Temprature:{current_weather['current_temp']}")
     print(f"feels like:{current_weather['feels_like']}")
     print(f"minimum Temprature:{current_weather['temp min']}°c")
     print(f"maximum Tempurature:{current_weather['temp_max']}°c")
     print(f"Humidity:{current_weather['humidity']}%")
     print(f"weather predection:{current_weather['description']}")
     print(f"Rain predection:{'yes'if rain_prediction else 'NO'}")
     print('\nFuture Temperature predictions:')
     for time,temp in zip(future_times,future_temp):
      print(f"(time):{round(temp,1)}°c")
     print('\nFuture Humidity predictions:')
     for time,humidity in zip(future_times,future_humidity):
      print(f"{time}:{round(humidity,1)}%")
weather_view()

