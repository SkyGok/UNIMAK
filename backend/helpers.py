import requests

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/df/login")
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorate routes to require admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/df/login")
        if session.get("role") != "admin":
            return apology("Access denied. Admin privileges required.", 403)
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper()
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None


# Translation dictionary
translations = {
    "en": {
        "upload": "Upload",
        "history": "History",
        "settings": "Settings",
        "project_number": "Project Number",
        "project_manager": "Project Manager",
        "reason": "Reason",
        "description": "Description",
        "save": "Save",
        "choose_language": "Choose Language",
    },
    "tr": {
        "upload": "Yükle",
        "history": "Geçmiş",
        "settings": "Ayarlar",
        "project_number": "Proje Numarası",
        "project_manager": "Proje Yöneticisi",
        "reason": "Sebep",
        "description": "Açıklama",
        "save": "Kaydet",
        "choose_language": "Dil Seçiniz",
    },
    "es": {
        "upload": "Subir",
        "history": "Historial",
        "settings": "Configuración",
        "project_number": "Número de Proyecto",
        "project_manager": "Gerente del Proyecto",
        "reason": "Razón",
        "description": "Descripción",
        "save": "Guardar",
        "choose_language": "Seleccionar Idioma",
    }
}

def get_translations():
    lang = session.get("language", "en")  # default English
    return translations.get(lang, translations["en"])


