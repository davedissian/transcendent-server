from flask import Blueprint, render_template

base = Blueprint('base', 'transcendentserver', template_folder='templates/views/base')

@base.route('/')
def index():
    return render_template('index.html')
