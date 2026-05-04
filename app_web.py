from flask import Flask, render_template, request, redirect, url_for, flash
from models.database import SessionLocal
from repositories.algoritm_repo import AlgoritmRepository
from repositories.framework_repo import FrameworkRepository
from repositories.fisier_repo import FisierRepository
from repositories.cheie_repo import CheieRepository
from repositories.performanta_repo import PerformantaRepository
from services.crypto_manager import CryptoManagerService
import sqlalchemy.exc
import os
import hashlib


# Importuri pentru generare RSA
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)
app.secret_key = "kms_premium_violet_key"

#functie pentru calculare hash sha 256 pentru fisier
def calculeaza_hash_fisier(cale_fisier):
    sha256 = hashlib.sha256()

    #deschide fisierul in mod binar si citeste-l in bucati pentru a calcula hash-ul
    with open(cale_fisier, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
            #actualizeaza hash-ul cu fiecare bucata citita
    
    #transforma rezultatul intr un string hexadecimal
    return sha256.hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/algoritmi', methods=['GET', 'POST'])
def algoritmi():
    db = SessionLocal()
    repo = AlgoritmRepository(db)
    if request.method == 'POST':
        try:
            repo.create(nume=request.form['nume'], tip=request.form['tip'])
            flash("Algoritm adăugat cu succes!", "success")
        except sqlalchemy.exc.IntegrityError:
            flash("Eroare: Acest nume de algoritm există deja în baza de date!", "error")
        except Exception as e:
            flash(f"Eroare neașteptată: {str(e)}", "error")
        finally:
            db.close()
        return redirect(url_for('algoritmi'))
    
    pagina = request.args.get('pagina', 1, type=int)
    items, total_pagini = repo.read_paginat(pagina=pagina, pe_pagina=5)
    db.close()
    return render_template('algoritmi.html', items=items, pagina_curenta=pagina, total_pagini=total_pagini)

@app.route('/algoritmi/delete/<int:id>')
def delete_algoritm(id):
    db = SessionLocal()
    AlgoritmRepository(db).delete(id)
    db.close()
    return redirect(url_for('algoritmi'))

@app.route('/frameworks', methods=['GET', 'POST'])
def frameworks():
    db = SessionLocal()
    repo = FrameworkRepository(db)
    if request.method == 'POST':
        try:
            repo.create(nume=request.form['nume'], versiune=request.form.get('versiune'))
            flash("Framework înregistrat cu succes!", "success")
        except sqlalchemy.exc.IntegrityError:
            flash("Eroare: Această combinație de nume și versiune pentru framework există deja!", "error")
        except Exception as e:
            flash(f"Eroare neașteptată: {str(e)}", "error")
        finally:
            db.close()
        return redirect(url_for('frameworks'))
   
    pagina = request.args.get('pagina', 1, type=int)
    items, total_pagini = repo.read_paginat(pagina=pagina, pe_pagina=5)
    
    db.close()
    return render_template('frameworks.html', items=items, pagina_curenta=pagina, total_pagini=total_pagini)

@app.route('/frameworks/delete/<int:id>')
def delete_framework(id):
    db = SessionLocal()
    FrameworkRepository(db).delete(id)
    db.close()
    return redirect(url_for('frameworks'))

@app.route('/fisiere', methods=['GET', 'POST'])
def fisiere():
    db = SessionLocal()
    repo = FisierRepository(db)

    if request.method == 'POST':
        try:
            cale_fisier = request.form['cale'].strip()

            if not os.path.isfile(cale_fisier):
                raise ValueError("Calea introdusă nu indică un fișier existent.")

            hash_final = calculeaza_hash_fisier(cale_fisier)

            repo.create(
                nume_original=request.form['nume'].strip(),
                cale_stocare=cale_fisier,
                hash_sha256=hash_final,
                status_fisier=request.form['status']
            )

            flash("Fișier salvat! Hash-ul SHA-256 a fost calculat automat.", "success")

        except Exception as e:
            flash(f"Eroare: {str(e)}", "error")
        finally:
            db.close()

        return redirect(url_for('fisiere'))

    pagina = request.args.get('pagina', 1, type=int)
    items, total_pagini = repo.read_paginat(pagina=pagina, pe_pagina=5)

    db.close()

    return render_template(
        'fisiere.html',
        items=items,
        pagina_curenta=pagina,
        total_pagini=total_pagini
    )

@app.route('/fisiere/delete/<int:id>')
def delete_fisier(id):
    db = SessionLocal()
    FisierRepository(db).delete(id)
    db.close()
    return redirect(url_for('fisiere'))

@app.route('/chei', methods=['GET', 'POST'])
def chei():
    db = SessionLocal()
    repo_chei = CheieRepository(db)
    repo_algo = AlgoritmRepository(db)
    
    if request.method == 'POST':
        try:
            import os 
            id_algo = int(request.form['id_algo'])
            algoritm = repo_algo.read_by_id(id_algo)
            
            if not algoritm:
                raise ValueError("Algoritmul selectat nu există!")

            if algoritm.tip == 'asimetric':
                private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
                val_bytes = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                iv_sau_salt = "RSA_KEY_PAIR"
                flash("Cheie RSA generată automat cu succes!", "success")

            #  ALGORITM SIMETRIC (AES) 
            else:
                val_hex = request.form.get('valoare', '').strip()
                
                if not val_hex:
                    val_bytes = os.urandom(32)
                    flash("Cheie simetrică (AES) generată automat!", "success")
                else:
                    val_bytes = bytes.fromhex(val_hex)
                    flash("Cheia simetrică manuală a fost salvată!", "success")
                
                iv_sau_salt = request.form.get('salt', '').strip()
                if not iv_sau_salt:
                    iv_sau_salt = os.urandom(16).hex()
                    flash("Vectorul de inițializare (IV) a fost generat automat!", "info")

            repo_chei.create(id_algoritm=id_algo, valoare_criptata=val_bytes, iv_sau_salt=iv_sau_salt)
            
        except ValueError as ve:
            flash(f"Eroare date: {str(ve)}", "error")
        except sqlalchemy.exc.IntegrityError:
            flash("Eroare: Problemă de integritate în baza de date!", "error")
        except Exception as e:
            flash(f"Eroare generală: {str(e)}", "error")
        finally:
            db.close()
        return redirect(url_for('chei'))
    
    pagina = request.args.get('pagina', 1, type=int)
    items, total_pagini = repo_chei.read_paginat(pagina=pagina, pe_pagina=10)

    algoritmi = repo_algo.read()
    
    db.close()
    return render_template('chei.html', items=items, algoritmi=algoritmi, pagina_curenta=pagina, total_pagini=total_pagini)

@app.route('/chei/delete/<int:id>')
def delete_cheie(id):
    db = SessionLocal()
    CheieRepository(db).delete(id)
    db.close()
    return redirect(url_for('chei'))

@app.route('/performante')
def performante():
    db = SessionLocal()
    repo = PerformantaRepository(db)

    pagina = request.args.get('pagina', 1, type=int)

    statistici = repo.read_statistici_medii()
    items, total_pagini = repo.read_paginat(pagina=pagina, pe_pagina=10)

    db.close()

    return render_template(
        'performante.html',
        items=items,
        statistici=statistici,
        pagina_curenta=pagina,
        total_pagini=total_pagini
    )


@app.route('/operatii', methods=['GET', 'POST'])
def operatii():
    db = SessionLocal()
    repo_fis = FisierRepository(db)
    repo_chei = CheieRepository(db)
    repo_fw = FrameworkRepository(db)
    repo_perf = PerformantaRepository(db)
    
    crypto_service = CryptoManagerService(repo_fis, repo_chei, repo_perf)

    if request.method == 'POST':
        try:
            actiune = request.form.get('actiune')
            id_fisier = int(request.form.get('id_fisier'))
            id_cheie = int(request.form.get('id_cheie'))
            id_framework = int(request.form.get('id_framework'))
            
            framework = repo_fw.read_by_id(id_framework)
            if not framework:
                raise ValueError("Framework invalid.")

            cheie_selectata = repo_chei.read_by_id(id_cheie)
            if not cheie_selectata:
                raise ValueError("Cheia selectată nu există.")

            if cheie_selectata.algoritm.tip == 'asimetric' and "CRYPTOGRAPHY" not in framework.nume.upper():
                raise ValueError("Pentru RSA se poate folosi doar framework-ul Cryptography.")

            if actiune == 'cripteaza':
                cale_noua = crypto_service.cripteaza_fisier(id_fisier, id_cheie, framework.nume, framework.id_framework)
                flash(f"Fișier criptat! Salvat la: {cale_noua} (Hash și DB actualizate)", "success")
            elif actiune == 'decripteaza':
                cale_noua = crypto_service.decripteaza_fisier(id_fisier, id_cheie, framework.nume, framework.id_framework)
                flash(f"Fișier decriptat! Salvat la: {cale_noua} (Hash și DB actualizate)", "success")
                
        except Exception as e:
            flash(f"Eroare la procesare: {str(e)}", "error")
        finally:
            db.close()
        return redirect(url_for('operatii'))

    fisiere = repo_fis.read()
    chei = repo_chei.read()
    frameworks = repo_fw.read()

    chei_select = []
    for cheie in chei:
        chei_select.append({
            "id_cheie": cheie.id_cheie,
            "id_algoritm": cheie.id_algoritm,
            "algoritm_nume": cheie.algoritm.nume,
            "algoritm_tip": cheie.algoritm.tip
        })

    db.close()
    
    return render_template('operatii.html', fisiere=fisiere, chei=chei_select, frameworks=frameworks)

if __name__ == '__main__':
    app.run(debug=True, port=5000)