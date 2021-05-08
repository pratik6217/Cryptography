import streamlit as st 
from cryptography.fernet import Fernet
import SessionState 
from pymongo import MongoClient
import smtplib, ssl
import rsa

session_state = SessionState.get(username = '', login = True, register = False, reg_valid = False, log_valid = False, logged_in = False)

client = MongoClient('mongodb+srv://admin:admin@password-manager.bl1uj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client['CSS']
cursor = db['Login']
#key = Fernet.generate_key()
#with open('./key.key', 'wb') as file:
#	file.write(key)

with open('./key.key', 'rb') as file:
	key = file.read()

f = Fernet(key)

def send_mail(receiver, message):
	try:
		user = 'cryptography.smtp@gmail.com'
		with open('pass.pass', 'r') as file:
			password = file.read()
		context = ssl.create_default_context()
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context= context)
		server.ehlo()
		server.login(user, password)
		server.sendmail(user, receiver, message)
		server.ehlo()
	except Exception as e:
		st.error(e)
	finally:
		server.quit()
		st.success('Email sent successfully !!')


def Steganography():
	st.title(f'Welcome to Our WebApp, {session_state.username}')
	menu = ['Encode', 'Decode']
	ch = st.sidebar.selectbox('Menu', menu)
	#key = Fernet.generate_key()
	#with open('./Encryption.key', 'wb') as file:
	#	file.write(key)
	with open('./Encryption.key', 'rb') as file:
		key = file.read()
	f = Fernet(key)

	if ch == 'Encode':
		st.title('Encode:')
		st.write(' ')
		st.write('Here you can encrypt your message and send this message to anyone you like !!')
		m = st.text_area('Enter your message:')
		encrypted_message = f.encrypt(m.encode()).decode()
		receiver = st.text_input("Enter the receiver's email:")
		send = st.button('Encrypt & Send')
		if send:
			send_mail(receiver, encrypted_message)

	elif ch == 'Decode':
		st.title('Decode:')
		received_message = st.text_area('Enter your encrypted message:')
		decode = st.button('Decode')
		if decode:
			decrypted_message = f.decrypt(received_message.encode()).decode()
			st.write(decrypted_message)

def register():
	st.title('Register')
	name = st.beta_columns(2)
	firstName = name[0].text_input('Enter your First Name:')
	lastName = name[1].text_input("Enter your Last Name:")

	email = st.text_input('Enter your email:')

	uname = st.beta_columns(2)
	username = uname[0].text_input('Select your username:')
	phone = uname[1].text_input('Enter your Phone Number:')

	pas = st.beta_columns(2)
	password1 = pas[0].text_input('Create a password:', type= 'password')
	password2 = pas[1].text_input('Confirm the password:', type= 'password')

	register_submit = st.button('Submit')

	if register_submit:
		try:
			if firstName == '':
				st.error('Please Enter Your Name !!')
				session_state.valid = False
			elif email == '':
				st.error('Please Enter Your Email !!')
				session_state.valid = False
			elif username == '' or len(username) < 5:
				st.error('Please Enter a proper Username !!')
				session_state.valid = False
			elif password1 == '' or password2 == '':
				st.error('Password Field cannot be blank !!')
				session_state.valid = False
			elif len(password1) < 5:
				st.warning('Please create a longer and stronger Password !!')
				session_state.valid = False
			elif password1 != password2:
				st.error('The two passwords did not match !!')
				session_state.valid = False
			elif len(phone) < 10 or len(phone) > 10:
				st.error('Please Enter a Proper 10 digit Phone Number !!')
				session_state.valid = False
			else:
				session_state.reg_valid = True
			phone = int(phone)
		except Exception as e:
			st.error(e)
		

	if session_state.reg_valid:
		if cursor.find_one({'username' : username}):
			st.error('This username already exists !!')
		else:
			d = { 'Name' : firstName + ' ' + lastName,
				'Email': email,
				'Phone': phone,
				'username': username,
				'password': f.encrypt(password1.encode())}
			insert = cursor.insert_one(d)
			if insert:
				st.success('Successfully Registered !!')
				session_state.login = True
				session_state.register = False
				st.button('Login -->')
			else:
				st.error('Some Error Occured :( Please try again !!')

def login():
	st.title('Login')
	st.write(' ')
	username = st.text_input('Enter your username:')
	password = st.text_input('Enter your password:', type= 'password')

	s = st.beta_columns(2)
	login_submit = s[0].button('submit')
	reg = s[1].button('Do not have an account? Register Here.')

	if reg:
		session_state.log_valid  = False
		session_state.register = True
		session_state.login = False
		st.warning('You will leave this page !!')
		st.button('continue')
	
	if login_submit:
		if username == '':
			st.error('username cannot be blank !!')
			session_state.log_valid = False
		elif password == '':
			st.error('Password cannot be blank !!')
			session_state.log_valid = False
		else:
			session_state.log_valid = True

	if session_state.log_valid:
		cred = cursor.find_one({'username' : username})
		if password == f.decrypt(cred['password']).decode():
			st.success('Logged in Successfully !!')
			session_state.username = username
			session_state.login = False
			session_state.register = False
			session_state.logged_in = True
			st.button('Enter the App -->')
		else:
			st.error('Please enter correct details !!')

PAGE_CONFIG = {'page_title': 'Text Steganography', 'page_icon': './icon.jpg', 'layout': 'centered'}
st.set_page_config(**PAGE_CONFIG)
	

if session_state.login:
	login()
elif session_state.register:
	register()
elif session_state.logged_in:
	Steganography()

