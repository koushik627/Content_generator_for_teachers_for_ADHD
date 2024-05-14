from flask import Flask, render_template, url_for, request, redirect
from flask_cors import CORS
from gpt import ChatGPTSession
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)
chatgptSession = ChatGPTSession()

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    class_ = db.Column(db.String(50), nullable=False)
    adhd_type = db.Column(db.String(50))
    phone_no = db.Column(db.String(20), nullable=False)


class StudentForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max=100)], render_kw={"placeholder": "Name"})
    age = IntegerField('Age', validators=[InputRequired()], render_kw={"placeholder": "Age"})
    class_ = StringField('Class', validators=[InputRequired(), Length(max=50)], render_kw={"placeholder": "Class"})
    adhd_type = StringField('ADHD Type', validators=[Length(max=50)], render_kw={"placeholder": "ADHD Type"})
    phone_no = StringField('Phone No', validators=[InputRequired(), Length(max=20)], render_kw={"placeholder": "Phone no."})
    submit = SubmitField('Add Student')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def root():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    students = Student.query.all()
    return render_template('dashboard.html', students=students)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/addStudent', methods=['GET', 'POST'])
@login_required
def addStudent():
    form = StudentForm()
    if form.validate_on_submit():
        new_student = Student(
            name=form.name.data,
            age=form.age.data,
            class_=form.class_.data,
            adhd_type=form.adhd_type.data,
            phone_no=form.phone_no.data
        )
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('addStudent.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/content')
def content():
    name = request.args.get('name')
    class_ = request.args.get('class_')
    adhd_type = request.args.get('adhd_type')
    age = request.args.get('age')
    phone_no = request.args.get('phone_no')
    
    return render_template('gpt.html', name=name, class_=class_, adhd_type=adhd_type, age=age, phone_no=phone_no)


@app.route('/gpt.html/get_answer', methods=['GET', 'POST'])
def get_answer():
    if request.method == 'POST':
        topic = request.form['text-input']
        age = request.form['age-input']
        adhdType = request.form['adhd-dropdown']
        emotion = request.form['emotion-dropdown']
        prompt = ""
        
        if(adhdType == "Inattentive"):
            prompt = "Teach a " + age +" year old about "+ topic + ". Explain it in a detailed way in points, based on the emotion " + emotion + " and based on all the inputs make the output easy to grasp. Bold the keywords. Keep in points with numbering 1, 2, etc. Add some questions about the topic at the end numbered with 1,2, etc. You should keep the questions only at the end and not in the explanation. Also, Directly display the content, don't keep any sure here is your content kind of lines."
        elif(adhdType == "Hyperactive"):
            prompt = "Teach a " + age +" year old about "+ topic + ". Explain it in a detailed way in story telling format, based on the emotion " + emotion + " and based on all the inputs make the output easy to grasp. Bold the keywords. Add some questions about the topic at the end numbered with 1,2, etc. You should keep the questions only at the end and not in the explanation. Also, Directly display the content, don't keep any sure here is your content kind of lines."
        else:
            prompt = "Teach a " + age +" year old about "+ topic + ". Explain it in a detailed way in story telling format in points, based on the emotion " + emotion + " and based on all the inputs make the output easy to grasp. Bold the keywords. Add some questions about the topic at the end numbered with 1,2, etc. You should keep the questions only at the end and not in the explanation. Also, Directly display the content, don't keep any sure here is your content kind of lines."
        print(prompt)
        answer = chatgptSession.get_ans(prompt)
        return answer
    else:
        return "Method Not Allowed", 405

if __name__ == '__main__':
    app.run(debug=True)
