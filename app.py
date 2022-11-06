import os
from flask import Flask
from flask import render_template
from flask import request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(current_dir,"database.sqlite3")

db = SQLAlchemy()
db.init_app(app)#initializing db app by passing flask
app.app_context().push()#pushing it to context


class Student(db.Model):
	__tablename__='student'
	
	student_id=db.Column(db.Integer,autoincrement=True,primary_key=True)
	roll_number=db.Column(db.String,unique=True,nullable=False)
	first_name=db.Column(db.String,nullable=False)
	last_name=db.Column(db.String)
	courses = db.relationship('Course',secondary='enrollments')
	

class Course(db.Model):
	__tablename__="course"
	course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
	course_code=db.Column(db.String,unique=True,nullable=False)
	course_name=db.Column(db.String,nullable=False)
	course_description=db.Column(db.String)
	students=db.relationship('Student',secondary='enrollments')

class Enrollments(db.Model):
	#This is an association table
	__tablename__="enrollments"

	enrollment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
	estudent_id=db.Column(db.Integer,db.ForeignKey("student.student_id"),nullable=False,)
	ecourse_id=db.Column(db.Integer,db.ForeignKey("course.course_id"),nullable=False)

@app.route('/')
def home():
	students_list = db.session.query(Student).all()
	if Student.query.all()==[]:
		return render_template('empty_home.html')
	else:
		return render_template('home.html',students=students_list)


@app.route('/student/create', methods=['GET','POST'])
def add_student():
	students = db.session.query(Student).all()
	if request.method=="POST":
		#now we will get the values that the user input into the form
		first_n = request.form['f_name']
		last_n = request.form['l_name']
		roll_num = request.form['roll']
		ticks = request.form.getlist('courses')
		courses_taken = []
		for i in ticks:
			courses_taken.append(int(i.split("_")[-1]))

		#in ticks we have the course ID of all the courses we have in the table

		#now we move on to creating the objects from these classes

		#adding the student
		new_student = Student(roll_number=roll_num,first_name=first_n,last_name=last_n)

		#Creating the courses relation with this student
		total_enroll=[]
		for j in courses_taken:
			ticked_course = Course.query.filter_by(course_id=j).first()
			total_enroll.append(ticked_course)
		#We now have a list with the objects of the courses that were ticked
		try:
			#first we add the student
			db.session.add(new_student)
			db.session.commit()
			#Then we add the courses
			for k in total_enroll:
				new_student.courses.append(k)
			db.session.commit()
			return redirect(url_for('home'))
		except:
			return render_template('already_exists.html')
	else:
		students = Student.query.all()
		return render_template('add_student.html',students = students)

@app.route('/student/<int:student_id>/update', methods = ['GET','POST'])
def update_student(student_id):
	student_to_update= Student.query.get_or_404(student_id)
	current_f_name = student_to_update.first_name
	current_l_name = student_to_update.last_name
	current_roll = student_to_update.roll_number

	#Here we are getting all the courses the student currently has 
	courses_selected_enroll=Enrollments.query.filter_by(estudent_id=student_id).all()
	courses_selected_update=[]

	for i in courses_selected_enroll:
		courses_selected_update.append(i.ecourse_id)
	#courses_selected_update is being used to populate the checkbox based on enrollments

	if request.method=='POST':


		courses_remove=Enrollments.query.filter_by(estudent_id=student_id).delete()
		db.session.commit()
		

		ticks_update = request.form.getlist('courses')
		courses_taken_update = []
		for i in ticks_update:
			courses_taken_update.append(int(i.split("_")[-1]))

		student_to_update.first_name=request.form['f_name']
		student_to_update.last_name=request.form['l_name']
		student_to_update.roll_number=current_roll

		total_enroll_update=[]
		for j in courses_taken_update:
			ticked_course = Course.query.filter_by(course_id=j).first()
			total_enroll_update.append(ticked_course)

		try:
			db.session.commit()
			for k in total_enroll_update:
				student_to_update.courses.append(k)
			db.session.commit()
			return redirect(url_for('home'))
			
		except:
			return render_template('already_exists.html')
	else:
		return render_template('update.html',current_f_name=current_f_name,current_l_name=current_l_name,current_roll=current_roll,student_to_update=student_to_update,courses_selected_update=courses_selected_update)

@app.route('/student/<int:student_id>/delete')
def delete_student(student_id):
	student_to_delete = Student.query.get_or_404(student_id)
	try:
		db.session.delete(student_to_delete)
		db.session.commit()
		return redirect(url_for('home'))
	except:
		return "Yo"


@app.route('/student/<int:student_id>')
def show_student(student_id):
	student_to_show = Student.query.get_or_404(student_id)
	enrollments_taken = Enrollments.query.filter_by(estudent_id=student_id).all()
	courses_taken_id=[]
	for i in enrollments_taken:
		courses_taken_id.append(i.ecourse_id)
	courses_taken=[]
	for i in courses_taken_id:
		courses_taken.append(Course.query.filter_by(course_id=i).first())

	return render_template('student_details.html',student_to_show=student_to_show,courses_taken=courses_taken)


if __name__=='__main__':
	app.run(debug=True)
