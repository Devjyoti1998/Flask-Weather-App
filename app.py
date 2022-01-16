from flask import Flask,request,render_template,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
import requests

app=Flask(__name__)
app.secret_key='Devjyoti'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
app.config['SQLALCHEMY_EXCEPTIONS']=True

db=SQLAlchemy(app)
@app.before_first_request
def create_tables():
        db.create_all()

class City(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)

def get_cities(city):
    url=f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=0281e878b65577f5e28784a36b1263dd'
    r=requests.get(url).json()
    return r

@app.route('/')
def get_index():
    cities=City.query.all()
    weather_list=[]
    for city in cities:
        r=get_cities(city.name)
        weather={
            'city': city.name,
            'temperature': r['main']['temp'],
            'description':r['weather'][0]['description'],
            'icon':r['weather'][0]['icon']
        }
        print (weather)
        weather_list.append(weather)
    return render_template('weather.html',weather_list=weather_list)

@app.route('/',methods=['POST'])
def post_index():
    city=request.form.get('city')
    err_msg=''
    if city:
        req=get_cities(city)
        if req['cod']==200:
            if City.query.filter_by(name=city).first():
                err_msg='City already exists!'
            else:
                db.session.add(City(name=city))
                db.session.commit()
        else:
            err_msg='Invalid city!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('Successfully Added city')

    return redirect(url_for('get_index'))

@app.route('/delete/<name>')
def delete_city(name):
    city=City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f'Successfully deleted {city.name}','success')
    return redirect(url_for('get_index'))



if __name__=='__main__':
    app.run(port=5001,debug=True)
