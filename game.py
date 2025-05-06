import random
import json
from collections import defaultdict
from collections import Counter
from muestra_ejercitos import actualizar_tablero
from clases import Player

# Inicialización del juego
def initialize_game(aleatorio=0):
    # Solicitar cantidad de jugadores
    num_players = int(input("¿Cuántos jugadores (2-6)? "))
    while num_players < 2 or num_players > 6:
        print("Número de jugadores inválido. Deben ser entre 2 y 6.")
        num_players = int(input("¿Cuántos jugadores (2-6)? "))

    # Crear jugadores
    players = []
    colors = ["red", "blue", "green", "purple", "orange", "brown"]
    for i in range(num_players):
        while True:
            name = input(f"Nombre del jugador {i+1}: ").strip()
            if name:
                break
            print("El nombre no puede estar vacío. Intenta de nuevo.")
        color = colors[i]  # Asignar color automáticamente según el índice
        print(f"Se ha asignado el color {color} al jugador {name}.")
        players.append(Player(name, color))

    # Leer los países desde el archivo JSON
    with open("data/regiones_teg.json", "r", encoding="utf-8") as f:
        countries_data = json.load(f)

    # Crear lista de países a partir de las regiones
    countries = [country for continent in countries_data.values() for country in continent]
    random.shuffle(countries)  # Barajar los países

    # Repartir los países
    # Inicializar
    for player in players:
        player.countries = {}

    # Reparto base
    num_players = len(players)
    base_count = len(countries) // num_players

    for i, player in enumerate(players):
        for _ in range(base_count):
            country = countries.pop(0)  # Quitar de la lista principal
            player.countries[country] = 0  # Asignar

    # Repartir sobrantes uno por uno
    if countries:  # Si quedaron sobrantes
        print(f"Cartas sobrantes: {countries}")
        for i, country in enumerate(countries):
            players[i % num_players].countries[country] = 0
        countries.clear()  # Vaciar completamente la lista para evitar uso posterior indebido
    
    # Devolver Cartas al mazo
    for player in players:
        countries.extend(player.countries.keys())
    print(f"Cartas devueltas al mazo")

    # Definir orden de juego
    dice_rolls = {player.name: random.randint(1, 6) for player in players}
    print("Resultados de los dados:")
    for player_name, roll in dice_rolls.items():
        print(f"{player_name} obtuvo: {roll}")

    # Repetir lanzamientos solo entre quienes empataron
    while True:
        # Agrupar jugadores por tirada
        roll_to_players = defaultdict(list)
        for player_name, roll in dice_rolls.items():
            roll_to_players[roll].append(player_name)

        # Detectar empates
        tie_values = [roll for roll, names in roll_to_players.items() if len(names) > 1]

        if not tie_values:
            break  # No hay empates, se termina

        print("\nEmpate detectado. Lanzando nuevamente para los empatados...")

        # Relanzar solo para jugadores empatados
        for tie_val in tie_values:
            for name in roll_to_players[tie_val]:
                dice_rolls[name] = random.randint(1, 6)

        # Mostrar nuevos resultados
        for name in sorted(dice_rolls):  # Orden alfabético para claridad
            print(f"{name} obtuvo: {dice_rolls[name]}")

    # Ordenar jugadores según el resultado de los dados
    players.sort(key=lambda p: dice_rolls[p.name], reverse=True)
    print("\nOrden de juego definido:")
    for i, player in enumerate(players, 1):
        print(f"{i}. {player.name} ({dice_rolls[player.name]})")
    
    # Asignar ejércitos iniciales
    for player in players:
        for country in player.countries:
            player.countries[country] = 1  # Asignar 1 ejércitos a cada país
        player.remaining_armies = 30 - len(player.countries)

    actualizar_tablero(players)

    for player in players:
        if player.remaining_armies >= 5:
            print(f"\n{player.name}, es tu turno para colocar 5 ejércitos.")
            add_armies(player, 5, aleatorio)

    actualizar_tablero(players)

    # Luego: rondas de 3 ejércitos
    while any(player.remaining_armies > 0 for player in players):
        for player in players:
            if player.remaining_armies > 0:
                to_place = min(3, player.remaining_armies)
                print(f"\n{player.name}, es tu turno para colocar {to_place} ejércitos.")
                add_armies(player, to_place, aleatorio)
    
    actualizar_tablero(players)

    return players, countries

# Asigna ejércitos iniciales
def add_armies(player, num_armies,aleatorio = 0):
    """
    Permite a un jugador agregar un número de ejércitos (fichas) a sus países ocupados.
    """
    for _ in range(num_armies):
        print(f"\n{player.name}, te quedan {player.remaining_armies} ejércitos por colocar.")
        print("¿Dónde colocar tu ejército? Elige un país de la siguiente lista:")

        # Muestra la lista numerada de países del jugador con la cantidad de ejércitos en cada uno
        for idx, country in enumerate(player.countries, 1):
            armies_in_country = player.countries[country]
            print(f"{idx}. {country} ({armies_in_country} ejército{'s' if armies_in_country != 1 else ''})")


        # Espera un número válido del usuario
        while True:
            if aleatorio == 1:
                choice = random.randint(1, len(player.countries))
                print(f"Selección aleatoria: {choice}")
            else:
                try:
                    choice = int(input("Número del país elegido: "))
                except ValueError:
                    print("Entrada inválida. Por favor ingresa un número.")
                    continue

            if 1 <= choice <= len(player.countries):
                country_list = list(player.countries.keys())
                selected_country = country_list[choice - 1]
                player.countries[selected_country] += 1
                player.remaining_armies -= 1
                break
            else:
                if aleatorio == 0:
                    print("Número fuera de rango. Intenta de nuevo.")

# Turno de cada jugador
def player_turn(player, opponents, borders, mazo, aleatorio):
    player.canjes_realizados = 0
    conquered = False
    ya_ataco = False
    ya_reagrupo = False
    ya_solicito_carta = False

    while True:
        try:
            if aleatorio == 0:
                print("\nOpciones:")
                if not ya_reagrupo:
                    print("1. Atacar")
                if not ya_solicito_carta:
                    print("2. Reagrupar")
                if not ya_solicito_carta:
                    print("3. Solicitar carta / Canjear")
                print("4. Terminar turno")

                choice = int(input("Ingresa el número de tu elección: "))
            else:
                # Modo automático
                if not ya_ataco:
                    choice = 1
                elif not ya_solicito_carta:
                    choice = 3
                else:
                    choice = 4

            if choice == 1 and not ya_reagrupo:
                if aleatorio == 1:
                    print(f"\n{player.name} atacará automáticamente hasta que no sea posible.")
                    while puede_atacar(player, opponents, borders):
                        conquered |= attack(player, opponents, borders, mazo, aleatorio)
                        actualizar_tablero([player] + opponents)
                    print(f"\n{player.name} no puede seguir atacando.")
                    choice = 3
                else:
                    conquered |= attack(player, opponents, borders, mazo, aleatorio)
                ya_ataco = True

            elif choice == 2 and not ya_solicito_carta:
                regroup(player, borders, aleatorio)
                ya_reagrupo = True

            elif choice == 3 and not ya_solicito_carta:
                if conquered:
                    carta = mazo.robar_carta()
                    if carta:
                        print(f"\n{player.name} recibe una carta de país: {carta}")
                        if carta.nombre_pais in player.countries:
                            print(f"¡{player.name} ya controla {carta.nombre_pais}! Gana 2 ejércitos extra ahí.")
                            player.countries[carta.nombre_pais] += 2
                            player.cards.append(carta)
                        else:
                            print(f"{player.name} no controla {carta.nombre_pais}. Si lo conquista más adelante, podrá sumar 2 ejércitos allí.")
                            player.this_turn_cards.append(carta)
                verificar_y_canjear_cartas(player)
                ya_solicito_carta = True
            elif choice == 4:
                player.prev_turn_cards = player.this_turn_cards.copy()
                player.this_turn_cards.clear()
                # Agregar ejercitos segun la cantidad de paises dividido dos
                num_countries = len(player.countries)
                print(f"\n{player.name} tiene {num_countries} países.")
                player.remaining_armies += int(num_countries / 2)
                if num_countries > 0:
                    add_armies(player, player.remaining_armies , aleatorio) 
                print(f"Turno de {player.name} terminado.")
                break
            else:
                print("Opción no válida o fuera de orden.")
        except ValueError:
            print("Entrada inválida. Por favor ingresa un número.")

        actualizar_tablero([player] + opponents)

# Esto solo lo agrego para la opcion en automatico
def puede_atacar(player, opponents, borders):
    for origen in player.countries:
        tropas_origen = player.countries[origen]
        if tropas_origen > 1:
            for destino in borders[origen]:
                for opponent in opponents:
                    if destino in opponent.countries:
                        tropas_defensor = opponent.countries[destino]
                        if tropas_origen > tropas_defensor + 1:
                            return True
    return False

def attack(player, opponents, borders, mazo, aleatorio):

    # === SELECCIÓN DE PAÍS ATACANTE ===
    attacking_countries = [c for c in player.countries if player.countries[c] > 1]
    conquered = False
    if not attacking_countries:
        print("No tenés países con suficientes ejércitos para atacar.")
        return None

    print("¿Desde qué país querés atacar?")
    for idx, c in enumerate(attacking_countries, 1):
        print(f"{idx}. {c} ({player.countries[c]} ejércitos)")

    while True:
        try:
            if aleatorio == 0:
                i = int(input("Número del país atacante: ")) - 1
            else:
                i = random.randint(0, len(attacking_countries) - 1)
                print(f"Selección aleatoria: {i + 1}")

            if 0 <= i < len(attacking_countries):
                origin = attacking_countries[i]
                break
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida.")

    # === BUSCAR PAÍSES ENEMIGOS VECINOS ===
    vecinos = borders.get(origin, [])
    posibles = []
    for v in vecinos:
        for opp in opponents:
            if v in opp.countries:
                posibles.append((v, opp))
                break

    if not posibles:
        print(f"No hay países enemigos vecinos a {origin}.")
        return conquered

    print(f"¿A qué país querés atacar desde {origin}?")
    for idx, (dest, opp) in enumerate(posibles, 1):
        print(f"{idx}. {dest} ({opp.countries[dest]} ejércitos, {opp.name})")

    while True:
        try:
            if aleatorio == 0:
                j = int(input("Número del país objetivo: ")) - 1
            else:
                j = random.randint(0, len(posibles) - 1)
                print(f"Selección aleatoria: {j + 1}")

            if 0 <= j < len(posibles):
                destination, defender = posibles[j]
                break
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida.")

    # === CHEQUEO DE CONDICIONES ===
    na = player.countries[origin]
    nd = defender.countries[destination]
    
    print(f"Ejércitos atacante: {na}")
    print(f"Ejércitos defensores: {nd}")

    if na <= 1:
        print("No podés atacar desde un país con un solo ejército.")
        return conquered

    if na + 1 < nd:
        print("No podés atacar: necesitás tener más ejércitos atacantes mas 1 debe ser mayor o igual a los ejercitos del pais en defensa.")
        return conquered

    # === TIRADA DE DADOS ===
    da = min(3, na)
    dd = min(3, nd)

    attacker_dice = sorted([random.randint(1, 6) for _ in range(da)], reverse=True)
    defender_dice = sorted([random.randint(1, 6) for _ in range(dd)], reverse=True)

    print(f"\n{player.name} tira:     {attacker_dice}")
    print(f"{defender.name} tira: {defender_dice}")

    # === COMPARACIÓN Y PÉRDIDAS ===
    rounds = min(len(attacker_dice), len(defender_dice))
    attacker_losses = 0
    defender_losses = 0

    for k in range(rounds):
        if attacker_dice[k] > defender_dice[k]:
            defender_losses += 1
        else:
            attacker_losses += 1

    player.countries[origin] -= attacker_losses
    defender.countries[destination] -= defender_losses

    print(f"\nResultado del combate:")
    print(f"- {player.name} pierde {attacker_losses} ejército(s).")
    print(f"- {defender.name} pierde {defender_losses} ejército(s).")

    conquered = False  # Bandera para saber si conquistó

    # === CONQUISTA ===
    if defender.countries[destination] <= 0:
        print(f"{player.name} conquistó {destination} de {defender.name}!")
        defender.remove_country(destination)
        player.countries[destination] = 1
        while True:
            try:
                if aleatorio == 0:
                    move = int(input(f"¿Cuántos ejércitos querés mover a {destination}? (mínimo 1, máximo {na - 1}): ")) -1
                else:
                    move = random.randint(1, na - 2)
                    print(f"Selección aleatoria: {move}")
                if 1 <= move <= na - 1:
                    player.countries[origin] -= move 
                    player.countries[destination] = move
                    break
                else:
                    print("Número fuera de rango.")
            except ValueError:
                print("Entrada inválida.")
        conquered = True
    else:
        print(f"{destination} sigue en control de {defender.name} con {defender.countries[destination]} ejércitos.")
    
    # === CARTA POR CONQUISTA ===
    if conquered:
        carta = mazo.robar_carta()
        if carta:
            print(f"\n{player.name} recibe una carta de país: {carta}")

            # ¿El país es propio?
            if carta.nombre_pais in player.countries:
                print(f"¡{player.name} ya controla {carta.nombre_pais}! Gana 2 ejércitos extra ahí.")
                player.countries[carta.nombre_pais] += 2
                player.cards.append(carta)
            elif any(carta.nombre_pais == destination for carta in player.prev_turn_cards):
                player.countries[destination] += 2
                player.prev_turn_cards.remove(carta)
                player.cards.append(carta)
                print(f"{player.name} ya tiene la carta de {carta.nombre_pais} y gana 2 ejércitos extra ahí.")
            else:
                print(f"{player.name} no controla {carta.nombre_pais}. Si lo conquista más adelante, podrá sumar 2 ejércitos allí.")
                player.this_turn_cards.append(carta)
    return conquered

# Lógica de reagrupar
def regroup(player, borders, aleatorio):
    print(f"\n{player.name} está reagrupando sus ejércitos...")

    own_countries = list(player.countries.keys())

    if len(own_countries) < 2:
        print("No tenés suficientes países para reagrupar.")
        return

    print("Tus países:")
    for idx, country in enumerate(own_countries, 1):
        armies = player.countries.get(country, 0)
        print(f"{idx}. {country} ({player.countries[country]} ejércitos)")

    # Elegir país origen
    while True:
        try:
            origin_idx = int(input("Elegí el número del país del cual mover ejércitos: ")) - 1
            if 0 <= origin_idx < len(own_countries):
                origin = own_countries[origin_idx]
                if player.countries[origin] < 2:
                    print("Necesitás al menos 2 ejércitos para mover. Elegí otro país.")
                else:
                    break
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida.")

    # Mostrar posibles destinos limítrofes propios
    possible_destinations = [c for c in borders[origin] if c in own_countries and c != origin]

    if not possible_destinations:
        print("No hay países propios limítrofes a donde reagrupar desde este país.")
        return

    print("Países limítrofes tuyos a los que podés mover ejércitos:")
    for idx, country in enumerate(possible_destinations, 1):
        print(f"{idx}. {country} ({player.countries[country]} ejércitos)")

    # Elegir destino
    while True:
        try:
            dest_idx = int(input("Elegí el número del país destino: ")) - 1
            if 0 <= dest_idx < len(possible_destinations):
                destination = possible_destinations[dest_idx]
                break
            else:
                print("Número inválido.")
        except ValueError:
            print("Entrada inválida.")

    max_movable = player.countries[origin] - 1
    while True:
        try:
            num = int(input(f"¿Cuántos ejércitos querés mover? (1 a {max_movable}): "))
            if 1 <= num <= max_movable:
                break
            else:
                print("Cantidad inválida.")
        except ValueError:
            print("Entrada inválida.")

    player.countries[origin] -= num
    player.countries[destination] += num
    print(f"Moviste {num} ejércitos de {origin} a {destination}.")

# Solicitar carta de país
def request_card(player, conquered_country):
    print(f"{player.name}, solicitaste la carta de {conquered_country}. ¡Felicidades!")

def verificar_y_canjear_cartas(player):
    # Contar tipos de figuras
    tipo_figuras = [carta.tipo for carta in player.cards]  # corregido: 'figura' en vez de 'tipo'
    conteo = Counter(tipo_figuras)

    if len(player.cards) < 3:
        return  # No puede canjear aún

    # Verificar combinaciones posibles
    hay_tres_iguales = any(v >= 3 for v in conteo.values())
    hay_tres_distintas = len(set(tipo_figuras)) >= 3

    if not (hay_tres_iguales or hay_tres_distintas):
        return  # No cumple condiciones de canje

    # Seleccionar cartas para canjear
    if hay_tres_iguales:
        figura = next(k for k, v in conteo.items() if v >= 3)
        cartas_canjeadas = [c for c in player.cards if c.tipo == figura][:3]
    else:
        figuras_usadas = set()
        cartas_canjeadas = []
        for c in player.cards:
            if c.tipo not in figuras_usadas:
                figuras_usadas.add(c.tipo)
                cartas_canjeadas.append(c)
            if len(cartas_canjeadas) == 3:
                break

    # Eliminar cartas del jugador
    for c in cartas_canjeadas:
        player.cards.remove(c)

    # Asignar bonus
    bonus = [4, 7, 10]
    if player.canjes_realizados < len(bonus):
        ejercitos_extra = bonus[player.canjes_realizados]
    else:
        ejercitos_extra = bonus[-1]  # Repetir el último valor

    player.remaining_armies += ejercitos_extra
    player.canjes_realizados += 1

    print(f"\n{player.name} canjeó cartas y recibió {ejercitos_extra} ejércitos adicionales.")