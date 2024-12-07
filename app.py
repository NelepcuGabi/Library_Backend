from flask import Flask,request,jsonify
from db import get_connection
app = Flask(__name__)


connection = get_connection()
if connection and connection.open:
    
        print("Conexiune realizata")

else:
    print("Nu s-a putut stabili conexiunea cu baza de date.")

@app.route('/register',methods = ['POST'])
def register():
     data = request.json
     nume= data.get('nume')
     prenume = data.get('prenume')
     email = data.get('email')
     username = data.get('username')
     parola = data.get('parola')
     datanastere = data.get('datanastere')

     if not nume or not prenume or not parola:
          return jsonify({'eroare':'Numele,prenume si parola sunt necesare'})
     
     try:
          with connection.cursor()as cursor:
               query = """INSERT INTO userdata (Nume, Prenume, Email, UserName, Parola, DataNastere)
    VALUES (%s, %s, %s, %s, %s, %s)"""
               cursor.execute(query, (nume, prenume, email, username, parola, datanastere))
               connection.commit()
          return jsonify({'message': 'Utilizator înregistrat cu succes'}), 201
     except Exception as e:
          return jsonify({'error': str(e)}), 500


@app.route('/login',methods=['POST'])
def login():
     data = request.json
     email = data.get('email')
     parola = data.get('parola')

     try:
        with connection.cursor() as cursor:
               query=" select * from userdata where email = %s and parola =%s"
               cursor.execute(query,(email,parola))
               user = cursor.fetchone
        if user:
             return jsonify({'mesaj':'Autentificare reusita'}),200
        else:
             return jsonify({'eroare': 'Email sau parola greista!'}),401
     except Exception as e:
          return jsonify({'error': str(e)}), 500

    
                
        
          

@app.route('/home')

def  index():
    return "Salutare"


if __name__ == "__main__":
    app.run(debug = True)
