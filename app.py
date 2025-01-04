from flask import Flask,request,jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
from db import get_connection
app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'secret_key'  # Cheia secretă pentru JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=48)  # Token-ul expiră după 1 oră
jwt = JWTManager(app)
#baza de date
connection = get_connection()
if connection and connection.open:
    
        print("Conexiune realizata")

else:
    print("Nu s-a putut stabili conexiunea cu baza de date.")


#utilizatori si cont

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


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    parola = data.get('parola')

    try:
        # Verificăm dacă avem email și parolă
        if not email or not parola:
            return jsonify({'error': 'Email și parola sunt obligatorii'}), 400

        # Începem interogarea
        with connection.cursor() as cursor:
            query = "SELECT * FROM userdata WHERE email = %s AND parola = %s"
            cursor.execute(query, (email, parola))
            user = cursor.fetchone()  # Corectăm eroarea (apelăm funcția `fetchone()`)

        if user:
            # Creăm un token JWT pentru utilizator
            access_token = create_access_token(identity={'id': user[0], 'email': user[2]})

            # Salvăm token-ul în baza de date
            with connection.cursor() as cursor:
                update_query = "UPDATE userdata SET access_token = %s WHERE id = %s"
                cursor.execute(update_query, (access_token, user[0]))
                connection.commit()

            return jsonify({'mesaj': 'Autentificare reușită', 'access_token': access_token}), 200
        else:
            return jsonify({'eroare': 'Email sau parolă greșită!'}), 401

    except Exception as e:
        # Capturăm toate erorile și le logăm pentru debugging
        print(f"Eroare la login: {str(e)}")
        return jsonify({'error': f'Eroare la login: {str(e)}'}), 500


@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    token = data.get('access_token')

    try:
        with connection.cursor() as cursor:
            # Ștergem token-ul din baza de date
            update_query = "UPDATE userdata SET access_token = NULL WHERE access_token = %s"
            cursor.execute(update_query, (token,))
            connection.commit()

        return jsonify({'mesaj': 'Deconectare reușită'}), 200
    except Exception as e:
        return jsonify({'error': f'Eroare la deconectare: {str(e)}'}), 500

    


#produse
@app.route('/delete/<int:product_id>',methods=['DELETE'])

def delete_products(product_id):
    try:
        with connection.cursor() as cursor:
            query = "DELETE FROM produse WHERE id = %s"
            cursor.execute(query,(product_id,))
            connection.commit()
            return jsonify({'mesaj':'Produs sters'}), 200
    except Exception as e:
        return jsonify({'eroare': str(e)}), 500

          
@app.route('/produse',methods=['GET'])
def  get_products():
    try:
        with connection.cursor() as cursor:
            query_produse = "select * from produse"
            cursor.execute(query_produse)
            produse = cursor.fetchall() 
            query_tip_produse = "select * from tipproduse"
            cursor.execute(query_tip_produse)
            tip_produse = cursor.fetchall()

        return jsonify({
             "tipuri produse": tip_produse,
             "produse": produse
        })
    except Exception as e:
         return jsonify({"eroare": str(e)})
              
                
@app.route('/add_product',methods=['POST'])
def add_product():
        data = request.json
        nume= data.get('nume')
        id_tip = data.get('id_tip')
        brand = data.get('brand')
        descriere = data.get('descriere')
        pret_buc = data.get('pret_bucata')
        stoc = data.get('stoc')
        imagine = data.get('imagine')
        if not (nume and pret_buc and stoc and imagine):
            return jsonify({'error': 'Toate câmpurile sunt obligatorii'}), 400

        try:
            with connection.cursor() as cursor:
                query = """
                           INSERT INTO produse (IdTip,Nume, Brand,Descriere, PretBucata, Stoc, Imagine)
                           VALUES (%s, %s, %s, %s, %s)
                           """
                cursor.execute(query, (id_tip,nume,brand,descriere,pret_buc,stoc,imagine))
                connection.commit()


                return jsonify({'message': 'Produs adăugat cu succes'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/update_product/<int:product_id>',methods=['PUT'])
def update_product(product_id):
    data = request.json
    nume= data.get('nume')
    id_tip = data.get('id_tip')
    brand= data.get('brand')
    descriere = data.get('descriere')
    pret_buc = data.get('pret_bucata')
    stoc = data.get('stoc')
    imagine = data.get('imagine')
    try:
        with connection.cursor() as cursor:
            query = """
            UPDATE produse
            SET Nume = %s, Brand=%s,Descriere = %s, PretBucata = %s, Stoc = %s, Imagine = %s
            WHERE id = %s
            """
            cursor.execute(query,(nume,brand,descriere,pret_buc,stoc,imagine))
            connection.commit()
            return jsonify({'mesaj':'Produs updatat'}), 200
    except Exception as e:
            return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug = True)

