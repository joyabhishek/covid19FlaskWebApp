# covid19FlaskWebApp

Version: Beta 1.0
This version of web app shows below information regarding COVID19 in India:

1. Total no of effected cases till now.
2. Realtime count of people getting effected each day.
3. Total no of active cases till now.
4. Total no of recovered cases till now.
5. Realtime count of people getting recovered each day.
6. Sad no of people decreased till now.
7. Realtime count of sad people decreasing each day.
8. Graph showing no of people effected w.r.t date in each lockdown period.
9. Doubling rate, recovery rate, Mortality rate in each lockdown phase.
10. In each lockdown phase top 10 states based on the cases found.

The front UI looks like this:
![alt text](https://github.com/joyabhishek/covid19FlaskWebApp/blob/master/UI%20Design/iPhone%20X-XS-11%20Pro%20%E2%80%93%201.jpg "UI Design for this webApp can be found in tree/master/UI%20Design")

To setup the web app locally

1. Pull the code: 
`Git clone "https://github.com/joyabhishek/covid19FlaskWebApp.git"`

2. Activate the environment:
`covid19DjangoEnv\Scripts\activate.bat`

3. Set flask app
`SET FLASK_APP=index1.py`

4. Run the flask app
`flask run`
