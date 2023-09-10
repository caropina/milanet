class TransportationStop:

    """
        TransportationStop constructor.

        Initialize the following set of attributes to identify each stop:
            - ubicazione: the stop's address
            - mezzo: the type of transportation using the stop
            - percorso: an identifier for each potential public transportation route
            - num: the stop's sequence within the transportation route
            - long: the longitude of the stop
            - lat: the latitude of the stop
            - id_ferm: a unique identifier for the stop
            - linea: the transportation line serving the stop
    """

    def __init__(self):
        self.ubicazione: str = ""
        self.mezzo: str = ""
        self.percorso: int = 0
        self.num: int = 0
        self.long: str = ""
        self.lat: str = ""
        self.id_ferm: int = 0
        self.linea: str = ""

    def __str__(self):
        return f"{{'ubicazione': '{self.ubicazione}', 'mezzo': '{self.mezzo}', 'percorso': '{self.percorso}', 'num': '{self.num}', 'long': '{self.long}', 'lat': '{self.lat}', 'id_ferm': '{self.id_ferm}', 'linea': {self.linea}}}"

    def __hash__(self):
        return hash(self.id_ferm)

    def __eq__(self, other):
        if(not other):
            return False
        return (
            self.id_ferm == other.id_ferm
        )

