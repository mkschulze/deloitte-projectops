"""
Deloitte Flask App Template - Translations (DE/EN)
"""

TRANSLATIONS = {
    # Navigation
    'nav_home': {'de': 'Startseite', 'en': 'Home'},
    'nav_admin': {'de': 'Administration', 'en': 'Administration'},
    'nav_users': {'de': 'Benutzer', 'en': 'Users'},
    'nav_logout': {'de': 'Abmelden', 'en': 'Logout'},
    'nav_login': {'de': 'Anmelden', 'en': 'Login'},
    
    # Common
    'save': {'de': 'Speichern', 'en': 'Save'},
    'cancel': {'de': 'Abbrechen', 'en': 'Cancel'},
    'delete': {'de': 'Löschen', 'en': 'Delete'},
    'edit': {'de': 'Bearbeiten', 'en': 'Edit'},
    'create': {'de': 'Erstellen', 'en': 'Create'},
    'search': {'de': 'Suchen', 'en': 'Search'},
    'back': {'de': 'Zurück', 'en': 'Back'},
    'actions': {'de': 'Aktionen', 'en': 'Actions'},
    'yes': {'de': 'Ja', 'en': 'Yes'},
    'no': {'de': 'Nein', 'en': 'No'},
    
    # Auth
    'email': {'de': 'E-Mail', 'en': 'Email'},
    'password': {'de': 'Passwort', 'en': 'Password'},
    'login_title': {'de': 'Anmeldung', 'en': 'Login'},
    'login_button': {'de': 'Anmelden', 'en': 'Sign In'},
    'remember_me': {'de': 'Angemeldet bleiben', 'en': 'Remember me'},
    
    # Dashboard
    'dashboard': {'de': 'Dashboard', 'en': 'Dashboard'},
    'welcome': {'de': 'Willkommen', 'en': 'Welcome'},
    'statistics': {'de': 'Statistiken', 'en': 'Statistics'},
    
    # Errors
    'error_404_title': {'de': 'Seite nicht gefunden', 'en': 'Page not found'},
    'error_404_message': {'de': 'Die angeforderte Seite existiert nicht.', 'en': 'The requested page does not exist.'},
    'error_500_title': {'de': 'Serverfehler', 'en': 'Server Error'},
    'error_500_message': {'de': 'Ein interner Fehler ist aufgetreten.', 'en': 'An internal error occurred.'},
    
    # Add your translations here...
}


def get_translation(key, lang='de'):
    """Get translation for key in specified language"""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get('de', key))
    return key
