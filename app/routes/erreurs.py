from ..app import app
from flask import redirect, url_for

@app.errorhandler(404)
def page_non_trouvee(e):
    return redirect(url_for('recherche'))