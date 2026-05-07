from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import func, select

from .. import db
from ..models import *
from ..decorators import admin_required
from ..common import schedule_lrt
from .. import longRunningTasks as lrt

admin = Blueprint('admin', __name__)

def count(db, selQuery) -> int:
    return (
        db.session.execute(db.select(func.count()).select_from(selQuery.subquery()))
        .scalar_one()
    )


@admin.route('/admin/toggleDev')
@admin_required
def toggle_dev():
    current_user.is_dev = not current_user.is_dev
    db.session.merge(current_user)
    db.session.commit()
    # flash([
    #    f"You are {'now' if current_user.is_dev else 'no longer'} a developer!",
    #    "notice"
    #])
    return redirect(url_for('main.profile'))

@admin.route('/admin')
@admin_required
def dashboard():
    return render_template('admin_dash.html')

@admin.route('/admin/stats')
@admin_required
def stats():
    users = count(db, db.select(User))
    restaurants = count(db, db.select(Restaurant))
    return render_template('admin_stats.html', stats={"users":users, "restaurants":restaurants})

@admin.route('/admin/restaurants')
@admin_required
def restaurants():
    if current_user.is_dev:
        restaurants = Restaurant.query.all()
    else:
        restaurants = Restaurant.query.filter_by(is_test=False).all()
    rno = len(restaurants)
    return render_template('admin_restaurants.html', restaurants=restaurants, restno=rno, show_dev=current_user.is_dev)

@admin.route('/admin/restaurants/update')
@admin_required
def update_restaurants():
    flash("ok")

@admin.route('/admin/restaurants/<int:id>/update')
@admin_required
def update_restaurant(id):
    flash("ok")

@admin.route('/admin/restaurants/<int:db_id>/fill')
@admin_required
def fill_restaurant(db_id):
    resto = Restaurant.query.filter_by(id=db_id).first()
    if not resto:
        flash([
            "This restaurant wasn't found in the database.",
            "error"
        ])
        return redirect(url_for('admin.restaurants'))
    schedule_lrt(lrt.fill_restaurant, resto)
    flash([
        "Missing data is being loaded in the background. Refresh the page to see updates.",
        "notice"
    ])
    return redirect(url_for('admin.restaurants'))

@admin.route('/admin/restaurants/fill')
@admin_required
def fill_in_restaurants():
    schedule_lrt(lrt.fill_all_restaurants)
    flash([
        "Missing data is being loaded in the background. Refresh the page to see updates.",
        "notice"
    ])
    return redirect(url_for('admin.restaurants'))
