import json
import random
from collections import defaultdict, Counter

class Carta:
    def __init__(self, nombre_pais, tipo):
        self.nombre_pais = nombre_pais
        self.tipo = tipo  # "comodín", "globo", "galeón" o "cañon"

    def __repr__(self):
        return f"{self.nombre_pais} ({self.tipo})"

class Mazo:
    def __init__(self, ruta_archivo):
        self.cartas_disponibles = []
        self.cartas_retiradas = []
        self.contador_canjes = 0

        with open(ruta_archivo, encoding='utf-8') as f:
            data = json.load(f)

        for tipo, paises in data.items():
            for pais in paises:
                self.cartas_disponibles.append(Carta(pais, tipo))

        random.shuffle(self.cartas_disponibles)

    def robar_carta(self):
        if not self.cartas_disponibles:
            print("No hay más cartas en el mazo.")
            return None
        carta = self.cartas_disponibles.pop()
        self.cartas_retiradas.append(carta)
        return carta

    def cantidad_ejercitos_por_canje(self):
        tabla = [4, 7, 10, 15, 20, 25]
        if self.contador_canjes < len(tabla):
            return tabla[self.contador_canjes]
        return tabla[-1] + (self.contador_canjes - 5) * 5

    def es_canje_valido(self, cartas):
        if len(cartas) != 3:
            return False

        tipos = [c.tipo for c in cartas if c.tipo != "comodín"]
        comodines = [c for c in cartas if c.tipo == "comodín"]

        # 3 iguales (sin contar comodines)
        if len(set(tipos)) == 1 and len(tipos) == 3:
            return True
        # 1 comodín + 2 iguales
        if len(set(tipos)) == 1 and len(tipos) == 2 and len(comodines) == 1:
            return True
        # 2 comodines + 1 carta
        if len(tipos) == 1 and len(comodines) == 2:
            return True
        # 3 tipos distintos
        if len(set(tipos)) == 3:
            return True
        return False

    def realizar_canje(self, jugador, cartas):
        if not self.es_canje_valido(cartas):
            print("Canje inválido.")
            return 0

        self.contador_canjes += 1
        for carta in cartas:
            if carta in jugador.cartas:
                jugador.cartas.remove(carta)

        ejércitos = self.cantidad_ejercitos_por_canje()
        print(f"{jugador.name} realizó un canje y recibió {ejércitos} ejércitos.")
        return ejércitos

class Player:
    def __init__(self, name, color):
        self.name = name            # Nombre del jugador
        self.color = color          # Color del jugador para distinguir en el mapa
        self.countries = {}         # Diccionario de países y la cantidad de ejércitos en cada país
        self.remaining_armies = 0   # Ejercitos pendientes
        self.cards = []
        self.prev_turn_cards = []
        self.this_turn_cards = []
        self.canjes_realizados = 0

    def add_country(self, country_name, armies):
        self.countries[country_name] = armies
    
    def remove_country(self, country_name):
        if country_name in self.countries:
            del self.countries[country_name]