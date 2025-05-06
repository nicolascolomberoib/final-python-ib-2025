import game
import json
import os
from plot_map_with_coords import plot_map_with_coords  # Importamos la función de visualización
from muestra_ejercitos import actualizar_tablero
from clases import Carta, Mazo, Player

global aleatorio
aleatorio = 1  # Variable global para el modo de juego

def main():
    players, countries_deck = game.initialize_game(aleatorio)

    with open("data/limites.json", "r", encoding="utf-8") as f:
        borders = json.load(f)

    actualizar_tablero(players)

    ruta = os.path.join(os.path.dirname(__file__), "data", "cartas.json")
    mazo = Mazo(ruta)

    while True:
        jugadores_con_paises = [p for p in players if len(p.countries) > 0]
        if len(jugadores_con_paises) <= 1:
            break  # Solo queda un jugador con países, termina el juego

        for i, player in enumerate(players):
            if len(player.countries) == 0:
                continue  # Saltearse jugador eliminado

            opponents = players[:i] + players[i+1:]
            game.player_turn(player, opponents, borders, mazo, aleatorio)
            actualizar_tablero(players)

    print('El juego ha terminado. Gracias por jugar!')

if __name__ == "__main__":
    main()
