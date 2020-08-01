import numpy as np
import pandas as pd
import math
from sklearn.metrics import roc_curve
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns

#Understanding the data
df = pd.read_csv('flightdata.csv')
df.head()
df.shape
df.isnull().values.any()
df.isnull().sum()

#Removing null values 
df = df.drop('Unnamed: 25', axis=1)
print(df.isnull().sum())

df = df[["MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", "ORIGIN", "DEST", "CRS_DEP_TIME", "ARR_DEL15"]]
print(df.isnull().sum())

print(df[df.isnull().values.any(axis=1)].head())

#Filling null coulmn values
df = df.fillna({'ARR_DEL15': 1})
print(df.iloc[177:185])

print(df.head())


for index, row in df.iterrows():
    df.loc[index, 'CRS_DEP_TIME'] = math.floor(row['CRS_DEP_TIME'] / 100)
print(df.head())

df = pd.get_dummies(df, columns=['ORIGIN', 'DEST'])
print(df.head())

#Data splitting into train and test 
train_x, test_x, train_y, test_y = train_test_split(df.drop('ARR_DEL15', axis=1), df['ARR_DEL15'], test_size=0.2, random_state=42)
print(train_x.shape)

print(test_x.shape)


model = RandomForestClassifier(random_state=13)
model.fit(train_x, train_y)

predicted = model.predict(test_x)
model.score(test_x, test_y)

probabilities = model.predict_proba(test_x)

roc_auc_score(test_y, probabilities[:, 1])

#Building confusion matrix based on the false and true positive values
confusion_matrix(test_y, predicted)
print('Confusion Matrix')
print(confusion_matrix(test_y, predicted))

train_predictions = model.predict(train_x)
print('Precision Value ',precision_score(train_y, train_predictions))


print('Recall value ',recall_score(train_y, train_predictions))

sns.set()


fpr, tpr, _ = roc_curve(test_y, probabilities[:, 1])
plt.plot(fpr, tpr)
plt.plot([0, 1], [0, 1], color='grey', lw=1, linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')

plt.show()


#A function which changes the input date,time,origin and destination into numerical values for passing it to the model
def predict_delay(departure_date_time, origin, destination):

    try:
        departure_date_time_parsed = datetime.strptime(departure_date_time, '%d/%m/%Y %H:%M:%S')
    except ValueError as e:
        return 'Error parsing date/time - {}'.format(e)

    month = departure_date_time_parsed.month
    day = departure_date_time_parsed.day
    day_of_week = departure_date_time_parsed.isoweekday()
    hour = departure_date_time_parsed.hour

    origin = origin.upper()
    destination = destination.upper()

    input = [{'MONTH': month,
              'DAY': day,
              'DAY_OF_WEEK': day_of_week,
              'CRS_DEP_TIME': hour,
              'ORIGIN_ATL': 1 if origin == 'ATL' else 0,
              'ORIGIN_DTW': 1 if origin == 'DTW' else 0,
              'ORIGIN_JFK': 1 if origin == 'JFK' else 0,
              'ORIGIN_MSP': 1 if origin == 'MSP' else 0,
              'ORIGIN_SEA': 1 if origin == 'SEA' else 0,
              'DEST_ATL': 1 if destination == 'ATL' else 0,
              'DEST_DTW': 1 if destination == 'DTW' else 0,
              'DEST_JFK': 1 if destination == 'JFK' else 0,
              'DEST_MSP': 1 if destination == 'MSP' else 0,
              'DEST_SEA': 1 if destination == 'SEA' else 0 }]

    return model.predict_proba(pd.DataFrame(input))[0][0]

print(predict_delay('1/10/2018 21:45:00', 'DTW', 'SEA'))
#Histogram generation for origin DTW to destination SEA between days Oct 1 to Oct 7
labels = ('09/08', '22/05', '30/10', '15/04', '25/07', '07/09', '11/03')
values = (predict_delay('09/08/2019 20:30:00', 'ATL', 'SEA'),
          predict_delay('22/05/2019 18:05:00', 'DTW', 'ATL'),
          predict_delay('30/10/2019 16:45:00', 'MSP', 'JFK'),
          predict_delay('15/04/2019 01:26:00', 'DTW', 'MSP'),
          predict_delay('25/07/2019 08:10:00', 'MSP', 'ATL'),
          predict_delay('07/09/2019 04:03:32', 'SEA', 'JFK'),
          predict_delay('11/03/2019 02:15:45', 'DTW', 'ATL'))
alabels = np.arange(len(labels))

plt.bar(alabels, values, align='center', alpha=0.5)
plt.xticks(alabels, labels)
plt.ylabel('Probability of On-Time Arrival')
plt.ylim((0.0, 1.0))
plt.show()
