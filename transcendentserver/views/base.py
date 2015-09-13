from flask import Blueprint, render_template


base = Blueprint('base', 'transcendentserver')


@base.route('/')
def index():
    return render_template('index.html')
