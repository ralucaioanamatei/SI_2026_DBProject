from flask import Flask, render_template, request, redirect, url_for, flash
from models.database import SessionLocal
from repositories.algoritm_repo import AlgoritmRepository
from repositories.framework_repo import FrameworkRepository
from repositories.fisier_repo import FisierRepository
from repositories.cheie_repo import CheieRepository
from repositories.performanta_repo import PerformantaRepository
import sqlalchemy.exc

app = Flask(__name__)
app.secret_key = "kms_premium_violet_key"

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
    items = repo.read()
    db.close()
    return render_template('algoritmi.html', items=items)

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
    items = repo.read()
    db.close()
    return render_template('frameworks.html', items=items)

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
            repo.create(
                nume_original=request.form['nume'],
                cale_stocare=request.form['cale'],
                hash_sha256=request.form['hash'],
                status_fisier=request.form['status']
            )
            flash("Fișier salvat!", "success")
        except Exception as e:
            flash(f"Eroare: {str(e)}", "error")
        finally:
            db.close()
        return redirect(url_for('fisiere'))
    items = repo.read()
    db.close()
    return render_template('fisiere.html', items=items)

@app.route('/fisiere/delete/<int:id>')
def delete_fisier(id):
    db = SessionLocal()
    FisierRepository(db).delete(id)
    db.close()
    return redirect(url_for('fisiere'))

@app.route('/chei', methods=['GET', 'POST'])
def chei():
    db = SessionLocal()
    repo = CheieRepository(db)
    if request.method == 'POST':
        try:
            val_hex = request.form['valoare'].strip()
            val_bytes = bytes.fromhex(val_hex) 
            repo.create(
                id_algoritm=int(request.form['id_algo']),
                valoare_criptata=val_bytes,
                iv_sau_salt=request.form.get('salt')
            )
            flash("Cheia a fost generată și salvată!", "success")
        except ValueError:
            flash("Eroare: Format HEX invalid! Folosiți doar 0-9 și A-F.", "error")
        except sqlalchemy.exc.IntegrityError:
            flash("Eroare: ID-ul Algoritmului nu există în baza de date!", "error")
        except Exception as e:
            flash(f"Eroare: {str(e)}", "error")
        finally:
            db.close()
        return redirect(url_for('chei'))
    items = repo.read()
    db.close()
    return render_template('chei.html', items=items)

@app.route('/chei/delete/<int:id>')
def delete_cheie(id):
    db = SessionLocal()
    CheieRepository(db).delete(id)
    db.close()
    return redirect(url_for('chei'))

@app.route('/performante')
def performante():
    db = SessionLocal()
    items = PerformantaRepository(db).read()
    db.close()
    return render_template('performante.html', items=items)

if __name__ == '__main__':
    app.run(debug=True, port=5000)