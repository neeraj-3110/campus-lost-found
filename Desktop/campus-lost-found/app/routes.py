from flask import Blueprint, render_template, redirect, url_for, request
from .models import User, Item
from .forms import RegisterForm, LoginForm, ItemForm
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/items')
def items():
    items = Item.query.all()
    return render_template('items.html', items=items)

# 🔥 DASHBOARD ROUTE
@main.route('/dashboard')
@login_required
def dashboard():
    all_items = Item.query.all()
    sample_listings = [
        {
            "id": None,
            "title": "MacBook Air",
            "category": "Electronics",
            "description": "Silver 13-inch laptop reported near Classroom B-204 after the morning lecture.",
            "location": "Engineering Block, Classroom B-204",
            "item_type": "found",
            "status": "open",
            "date_label": "Mar 23, 2026",
            "image_url": "https://images.unsplash.com/photo-1517336714739-489689fd1ca8?auto=format&fit=crop&w=900&q=80",
            "is_sample": True
        },
        {
            "id": None,
            "title": "Laptop Backpack",
            "category": "Accessories",
            "description": "Dark grey backpack with notebooks and charger pocket, seen outside the central library.",
            "location": "Central Library Entrance",
            "item_type": "lost",
            "status": "open",
            "date_label": "Mar 22, 2026",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
            "is_sample": True
        }
    ]
    sample_claims = [
        {
            "id": None,
            "title": "Wireless Earbuds",
            "category": "Electronics",
            "description": "Claim submitted for white earbuds matched with a listing from the student center.",
            "location": "Student Center",
            "item_type": "found",
            "status": "claimed",
            "date_label": "Mar 20, 2026",
            "image_url": "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?auto=format&fit=crop&w=900&q=80",
            "is_sample": True
        }
    ]

    listings = []
    claimed_items = []

    for item in all_items:
        image_url = url_for('static', filename=f"uploads/{item.image}") if item.image else "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=900&q=80"
        item_data = {
            "id": item.id,
            "title": item.title,
            "category": item.category or "General",
            "description": item.description,
            "location": item.location or "Campus",
            "item_type": item.item_type or "lost",
            "status": item.status or "open",
            "date_label": "Recently reported",
            "image_url": image_url,
            "is_sample": False
        }

        listings.append(item_data)
        if (item.status or "").lower() == "claimed":
            claimed_items.append(item_data)

    dashboard_listings = listings if listings else sample_listings
    dashboard_claims = claimed_items if claimed_items else sample_claims
    open_reports = len([item for item in dashboard_listings if item["status"].lower() == "open"])
    claimed_count = len([item for item in dashboard_listings if item["status"].lower() == "claimed"])

    return render_template(
        'dashboard.html',
        user=current_user,
        listings=dashboard_listings,
        claims=dashboard_claims,
        my_listings_count=len(dashboard_listings),
        open_reports_count=open_reports,
        items_claimed_count=claimed_count,
        avatar_initial=(current_user.username[:1].upper() if current_user.username else "U")
    )

@main.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            return "Email already registered ❌"

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            return "Invalid email or password ❌"

    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@main.route('/post', methods=['GET','POST'])
@login_required
def post_item():
    form = ItemForm()

    if form.validate_on_submit():
        image_file = form.image.data

        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join('app/static/uploads', filename))

        item = Item(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            location=form.location.data,
            item_type=form.item_type.data,
            image=filename
        )

        db.session.add(item)
        db.session.commit()

        return redirect(url_for('main.items'))

    return render_template('post_item.html', form=form)

@main.route('/claim/<int:id>')
@login_required
def claim(id):
    item = Item.query.get(id)
    if item and item.status == 'open':
        item.status = 'claimed'
        db.session.commit()
    return redirect(url_for('main.items'))
