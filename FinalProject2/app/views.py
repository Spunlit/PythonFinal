from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from .models import db, User, Ticket, Purchase
from .forms import RegistrationForm, LoginForm, TicketPurchaseForm
import random
from .models import db, User, Ticket, Purchase, HistoryUser
import os
from flask import request, send_from_directory


views = Blueprint('views', __name__)
UPLOAD_FOLDER = 'static/uploads'

# Убедитесь, что папка для загрузок существует
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@views.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files.get('file')  # Получаем файл из формы
    if file and file.filename != '':
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)  # Сохраняем файл на сервере
        return {'message': f'File {file.filename} uploaded successfully'}, 200
    return {'message': 'No file uploaded'}, 400
@views.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')  # Получаем файл
        if file and file.filename != '':
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            return {'message': f'File {file.filename} uploaded successfully'}, 200
        return {'message': 'No file uploaded'}, 400
    return render_template('upload.html')  # Отображаем форму

@views.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return {'message': f'File {filename} not found'}, 404

@views.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)  # Получаем список файлов
    return render_template('download.html', files=files)


@views.route('/')
def index():
    return render_template('index.html')


@views.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Имя пользователя уже занято.', 'danger')
            return redirect(url_for('views.register'))

        user = User(username=form.username.data)
        user.set_password(form.password.data)  # Hash the password
        user.token = User.generate_token()  # Generate a unique token
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('views.login'))
    return render_template('register.html', form=form)


@views.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('views.index'))
        flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html', form=form)


@views.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Пожалуйста, войдите в систему для просмотра профиля.', 'warning')
        return redirect(url_for('views.login'))

    user = User.query.get(user_id)
    purchases = Purchase.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', user=user, purchases=purchases)


@views.route('/buy_tickets', methods=['GET', 'POST'])
def buy_tickets():
    form = TicketPurchaseForm()
    user_id = session.get('user_id')

    if not user_id:
        flash('Please log in to buy tickets.', 'warning')
        return redirect(url_for('views.login'))

    user = User.query.get(user_id)
    print("User ID:", user_id, "User Balance:", user.balance)  # Debugging user info

    if form.validate_on_submit():
        ticket_type = request.form['ticket_type']
        ticket = Ticket.query.filter_by(type=ticket_type).first()

        if not ticket:
            flash('Selected ticket not found.', 'danger')
            return redirect(url_for('views.buy_tickets'))

        quantity = form.quantity.data
        total_cost = ticket.price * quantity

        print(f"Selected Ticket: {ticket_type}, Quantity: {quantity}, Total Cost: {total_cost}")

        if user.balance >= total_cost:
            # Deduct the cost from the user's balance
            user.balance -= total_cost
            # Create a new Purchase record
            purchase = Purchase(user_id=user_id, ticket_id=ticket.id, quantity=quantity)
            db.session.add(purchase)
            db.session.commit()
            print(f"Purchased {quantity} {ticket_type} ticket(s) for user {user_id}")  # Debugging purchase
            flash('Tickets successfully purchased!', 'success')
        else:
            flash('Insufficient funds.', 'danger')

        return redirect(url_for('views.profile'))

    tickets = Ticket.query.all()
    return render_template('buy_tickets.html', form=form, tickets=tickets, user=user)


@views.route('/balance', methods=['GET', 'POST'])
def balance():
    user_id = session.get('user_id')
    if not user_id:
        flash('Пожалуйста, войдите в систему для просмотра баланса.', 'warning')
        return redirect(url_for('views.login'))

    user = User.query.get(user_id)
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash('Пожалуйста, введите положительную сумму.', 'danger')
            else:
                user.balance += amount
                db.session.commit()
                flash(f'Баланс пополнен на ${amount:.2f}!', 'success')
        except ValueError:
            flash('Неверная сумма.', 'danger')

    return render_template('balance.html', user=user)


import random


@views.route('/results', methods=['GET', 'POST'])
def results():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view results.', 'warning')
        return redirect(url_for('views.login'))

    user = User.query.get(user_id)

    # Define winnings and probabilities for each ticket type
    ticket_rewards = {
        "Standard": {
            "rewards": [1, 2.5, 5, 7.5, 10, 50, 75, 100],
            "probabilities": [0.40, 0.20, 0.15, 0.10, 0.05, 0.05, 0.04, 0.01],
        },
        "Premium": {
            "rewards": [5, 10, 25, 50, 100, 250, 500, 1000],
            "probabilities": [0.40, 0.20, 0.15, 0.10, 0.05, 0.05, 0.04, 0.01],
        },
        "VIP": {
            "rewards": [50, 100, 200, 500, 1000, 2500, 5000, 10000],
            "probabilities": [0.40, 0.20, 0.15, 0.10, 0.05, 0.05, 0.04, 0.01],
        },
    }

    if request.method == 'POST':
        if 'purchase_id' not in request.form:
            flash('No ticket selected to try your luck.', 'danger')
            return redirect(url_for('views.results'))

        try:
            purchase_id = int(request.form['purchase_id'])
            purchase = Purchase.query.get(purchase_id)

            if purchase and purchase.user_id == user_id and purchase.quantity > 0:
                ticket = Ticket.query.get(purchase.ticket_id)
                rewards = ticket_rewards[ticket.type]["rewards"]
                probabilities = ticket_rewards[ticket.type]["probabilities"]

                previous_balance = user.balance
                winning_amount = random.choices(rewards, probabilities)[0]
                ticket_cost = ticket.price

                # Update user's balance
                user.balance += winning_amount
                purchase.quantity -= 1
                if purchase.quantity == 0:
                    db.session.delete(purchase)

                # Determine the result type
                if winning_amount < ticket_cost:
                    result_type = "loss"
                elif winning_amount == ticket_cost:
                    result_type = "break_even"
                else:
                    result_type = "win"

                # Insert history record
                history_record = HistoryUser(
                    user_id=user_id,
                    ticket_type=ticket.type,
                    win_amount=winning_amount,
                    previous_balance=previous_balance,
                    current_balance=user.balance,
                    result_type=result_type,
                    ticket_cost=ticket_cost
                )
                db.session.add(history_record)
                db.session.commit()

                flash(f'You won ${winning_amount:.2f}!', 'success')
            else:
                flash('No valid ticket found or the ticket is already used.', 'danger')
        except ValueError:
            flash('Invalid ticket ID.', 'danger')

    purchases = Purchase.query.filter_by(user_id=user_id).all()
    if not purchases:
        flash('You do not have any tickets to use.', 'warning')

    return render_template('results.html', purchases=purchases, user=user)


@views.route('/history')
def history():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your history.', 'warning')
        return redirect(url_for('views.login'))

    user = User.query.get(user_id)
    history_records = HistoryUser.query.filter_by(user_id=user_id).all()

    # Calculate statistics
    total_spent = sum(record.ticket_cost for record in history_records)
    total_won = sum(record.win_amount for record in history_records)
    losses = sum(1 for record in history_records if record.result_type == "loss")
    break_even = sum(1 for record in history_records if record.result_type == "break_even")
    wins = sum(1 for record in history_records if record.result_type == "win")

    return render_template(
        'history.html',
        user=user,
        history_records=history_records,
        total_spent=total_spent,
        total_won=total_won,
        losses=losses,
        break_even=break_even,
        wins=wins
    )



@views.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('views.index'))

@views.route('/leaderboard')
def leaderboard():
    # Получаем данные из базы
    leaderboard_data = db.session.query(
        User.username,
        db.func.sum(HistoryUser.win_amount).label('total_win'),
        db.func.sum(HistoryUser.ticket_cost).label('total_loss'),
        db.func.count(HistoryUser.ticket_type).label('ticket_count')
    ).join(HistoryUser, User.id == HistoryUser.user_id).group_by(User.username).all()

    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)

