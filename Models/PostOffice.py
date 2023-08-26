from enum import Enum

class PostType(Enum):
    POST_POINT = "Punto Poste"
    POST_LOCKER = "Poste Locker"
    POST_OFFICE = "Ufficio Postale"

class PostOffice:
    def __init__(self):
        self.nome: str = ""
        self.tipo_punto: PostType = None
        self.indirizzo: str = ""
        self.telefono: str = ""
        self.fax: str = ""
        self.servizi: list = []
        self.orari: dict = {
            'lunedì' : 'CHIUSO',
            'martedì' : 'CHIUSO',
            'mercoledì' : 'CHIUSO',
            'giovedì' : 'CHIUSO',
            'venerdì' : 'CHIUSO',
            'sabato': 'CHIUSO',
            'domenica':'CHIUSO'
        }
        self.citta: str = ""