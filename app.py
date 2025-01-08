from flask import Flask,request,jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,decode_token
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


import traceback

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        parola = data.get('parola')

        if not email or not parola:
            return jsonify({'error': 'Email și parola sunt obligatorii'}), 400

        # Verificăm conexiunea la baza de date
        if connection is None or not connection.open:
            return jsonify({'error': 'Conexiune la baza de date eșuată'}), 500

        with connection.cursor() as cursor:
            query = "SELECT * FROM userdata WHERE email = %s AND parola = %s"
            cursor.execute(query, (email, parola))
            user = cursor.fetchone()

            if user:
                try:
                    access_token = create_access_token(identity={'id': user['IdUserData'], 'email': user['Email']})
                except Exception as e:
                    return jsonify({'error': f"Eroare la generarea token-ului JWT: {str(e)}"}), 500

                if not user['token']:
                    with connection.cursor() as cursor:
                        update_query = "UPDATE userdata SET token = %s WHERE IdUserData = %s"
                        cursor.execute(update_query, (access_token, user['IdUserData']))
                        connection.commit()

                return jsonify({'mesaj': 'Autentificare reușită', 'access_token': access_token}), 200
            else:
                return jsonify({'eroare': 'Email sau parolă greșită!'}), 401

    except Exception as e:
        # Logăm eroarea completă pentru debugging
        return jsonify({'error': f'Eroare la login: {str(e)} \n {traceback.format_exc()}'}), 500





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

          
@app.route('/produse', methods=['GET'])
def get_products():
    try:
        # Obținem parametrii de query din URL
        id_tip = request.args.getlist('Id_tip')  # Acum putem obține mai multe valori pentru Id_tip

        if not id_tip:
            # Dacă nu sunt furnizați parametrii Id_tip, returnăm toate produsele
            query_produse = "SELECT * FROM produse"
            with connection.cursor() as cursor:
                cursor.execute(query_produse)
                produse = cursor.fetchall()
        else:
            # Verificăm și conversia tipului de date pentru Id_tip
            id_tip = tuple(map(int, id_tip))  # Conversie la int dacă este necesar

            # Construim o interogare SQL cu IN pentru a include toate valorile
            format_strings = ','.join(['%s'] * len(id_tip))  # creează %s, %s, %s, etc.
            query_produse = f"SELECT * FROM produse WHERE IdTip IN ({format_strings})"

            with connection.cursor() as cursor:
                cursor.execute(query_produse, id_tip)
                produse = cursor.fetchall()

        # Obținem tipurile de produse (nefiltrate)
        query_tip_produse = "SELECT * FROM tipproduse"
        with connection.cursor() as cursor:
            cursor.execute(query_tip_produse)
            tip_produse = cursor.fetchall()

        return jsonify({
            "tipuri produse": tip_produse,
            "produse": produse
        })
    except Exception as e:
        print(f"Eroare la obținerea produselor: {str(e)}")
        return jsonify({"eroare": str(e)}), 500





              
                
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

@app.route('/get_user_id', methods=['POST'])
def get_user_id():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email-ul este necesar'}), 400

    try:
        if connection is None or not connection.open:
            return jsonify({'error': 'Conexiune la baza de date eșuată'}), 500

        # Începem interogarea
        with connection.cursor() as cursor:
            query = "SELECT IdUserData FROM userdata WHERE email = %s"
            cursor.execute(query, (email))
            user = cursor.fetchone()
            print(user)#
            if user:
                return jsonify({'user_id':user['IdUserData']})# Obținem rezultatul interogării
        # Închide și deschide conexiunea înainte de a executa interogarea
        # with connection.cursor() as cursor:
        #     query = "SELECT IdUserData FROM userdata WHERE email = %s"
        #     cursor.execute(query, (email))
        #     result = cursor.fetchone()
        #     print(email)
        #     if result:
        #         return jsonify({'user_id': result[0]}), 200
        #     else:
        #         return jsonify({'error': 'Utilizatorul nu a fost găsit'}), 404
    except Exception as e:
        return jsonify({'error': f'Eroare la căutarea utilizatorului: {str(e)}'}), 500





@app.route('/add_order', methods=['POST'])
def add_order():
    data = request.json
    app.logger.debug(f"Received data: {data}")  # Log incoming request data for debugging
    iduser= data.get('IdUser')
    # Preluăm datele din body
    pret_total = data.get('PretTotal')
    modalitate_plata = data.get('ModalitatePlata')
    nr_telefon = data.get('NrTelefon')
    adresa = data.get('Adresa')
    user_id = data.get('IdUser')  # Preluăm user_id din body
    status_comanda = data.get('StatusComanda', 'În proces')

    if not pret_total or not modalitate_plata or not nr_telefon or not adresa or not user_id:
        return jsonify({'error': 'Datele comenzii sunt incomplete sau lipsesc user_id-ul'}), 400

    try:
        with connection.cursor() as cursor:
            # Adăugăm user_id în query-ul de inserare
            query_comanda = """
                INSERT INTO comenzi (IdUser,DataTranzatie, PretTotal, StatusComanda, ModalitatePlata, NrTelefon, Adresa)
                VALUES (%s,NOW(), %s, %s, %s, %s, %s)
            """
            cursor.execute(query_comanda, (iduser,pret_total, status_comanda, modalitate_plata, nr_telefon, adresa))
            connection.commit()

            comanda_id = cursor.lastrowid  # Folosește lastrowid pentru a obține ID-ul ultimei inserții

            return jsonify({'message': 'Comanda a fost plasată cu succes', 'comanda_id': comanda_id}), 201
    except Exception as e:
        return jsonify({'error': f'Eroare la crearea comenzii: {str(e)}'}), 500


@app.route('/user_orders', methods=['POST'])
def get_user_orders():
    try:
        data = request.get_json()  # Obținem datele trimise în body
        app.logger.debug(f"Received data: {data}")  # Logăm datele primite

        user_id = data.get('user_id')  # Obținem user_id din datele trimise

        if not user_id:
            return jsonify({'error': 'user_id este necesar'}), 400

        app.logger.debug(f"Querying orders for user_id: {user_id}")  # Logăm user_id-ul pe care îl folosim

        # Conectare la baza de date
        if connection is None or not connection.open:
            return jsonify({'error': 'Conexiune la baza de date eșuată'}), 500

        # Interogarea SQL
        with connection.cursor() as cursor:
            query_comenzi = """
                SELECT c.Id, c.DataTranzatie, c.PretTotal, c.StatusComanda, c.ModalitatePlata, c.NrTelefon, c.Adresa
                FROM comenzi c
                WHERE c.IdUser = %s
                ORDER BY c.DataTranzatie DESC
            """
            cursor.execute(query_comenzi, (user_id,))
            comenzi = cursor.fetchall()
            app.logger.debug(f"Found orders: {comenzi}")  # Logăm comenzile găsite

        if not comenzi:
            return jsonify({'message': 'Nu există comenzi pentru acest utilizator'}), 404

        return jsonify({'comenzi': comenzi}), 200

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")  # Logăm eroarea completă
        return jsonify({'error': f'Eroare la obținerea comenzilor: {str(e)}'}), 500


@app.route('/search_products', methods=['GET'])
def search_products():
    query = request.args.get('query')  # Obținem termenul de căutare din parametrii URL

    if not query:
        return jsonify({'error': 'Termenul de căutare este necesar'}), 400

    try:
        # Căutăm produsele care conțin termenul în nume
        with connection.cursor() as cursor:
            search_query = """
                SELECT * FROM produse
                WHERE Nume LIKE %s
                ORDER BY Nume
            """
            cursor.execute(search_query, ('%' + query + '%',))
            produse = cursor.fetchall()

        # Verificăm dacă au fost găsite produse
        if not produse:
            return jsonify({'message': 'Nu au fost găsite produse care să corespundă termenului de căutare'}), 404

        return jsonify({'produse': produse}), 200
    except Exception as e:
        return jsonify({'error': f'Eroare la căutarea produselor: {str(e)}'}), 500



if __name__ == "__main__":
    app.run(debug = True)

