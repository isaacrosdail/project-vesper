# Quick mock up to directly see theme mappings, may use for other stuff in future

from flask import Blueprint, render_template

tooling_bp = Blueprint('tooling', __name__, url_prefix='/tooling', template_folder='templates')

@tooling_bp.route('/theme-demo')
def theme_demo():
    return render_template('theme-demo.html')