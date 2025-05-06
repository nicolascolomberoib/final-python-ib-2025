from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
import matplotlib.patheffects as path_effects
import json

# Cargar imagen del tablero
image = Image.open("data/teg.jpg")

# Cargar coordenadas de los países
with open("data/country_coordinates.json", "r", encoding="utf-8") as f:
    country_coordinates = json.load(f)

# Crear figura para el mapa
fig_map, ax_map = plt.subplots(figsize=(10, 8))
ax_map.imshow(image)
ax_map.axis('off')

# Crear figura para la tabla
fig_table, ax_table = plt.subplots(figsize=(6, 8))
ax_table.axis('off')

def dibuja_ejercitos_en_pais(country_name, number, color="red"):
    '''
    Dibuja un círculo en el país con el número de ejércitos.
    '''
    if country_name not in country_coordinates:
        print(f"Country '{country_name}' not found in coordinates.")
        return

    x, y = country_coordinates[country_name]
    radius = 20

    circle = Circle((x, y), radius=radius, edgecolor='black', facecolor=color, linewidth=1, alpha=0.8)
    ax_map.add_patch(circle)

    ax_map.text(
        x, y, str(number), color="black", fontsize=10,
        ha="center", va="center"
    )

def actualizar_tablero(players):
    # Limpiar mapa anterior
    for patch in reversed(ax_map.patches):
        patch.remove()

    # Eliminar todos los textos anteriores
    for text in reversed(ax_map.texts):
        text.remove()

    for player in players:
        for country, n in player.countries.items():
            dibuja_ejercitos_en_pais(country, n, color=player.color)

    # Limpiar tabla anterior
    ax_table.clear()
    ax_table.axis('off')

    # Armar datos de la tabla
    column_data = []
    col_labels = []
    max_rows = 0

    for player in players:
        col_labels.append(player.name)
        entries = [f"{country} ({player.countries[country]})" for country in player.countries]
        column_data.append(entries)
        max_rows = max(max_rows, len(entries))

    # Rellenar con strings vacíos
    for col in column_data:
        while len(col) < max_rows:
            col.append("")

    table_data = list(zip(*column_data))

    # Crear tabla
    table = ax_table.table(cellText=table_data, colLabels=col_labels, loc="center", cellLoc='center')
    table.scale(1.2, 1.5)
    table.auto_set_font_size(False)
    table.set_fontsize(6)

    # Aplicar color y contorno al texto
    for (row, col), cell in table.get_celld().items():
        if col >= len(players):
            continue

        player_color = players[col].color
        text = cell.get_text()

        if row == 0:
            text.set_fontsize(14)

        text.set_color(player_color)
        text.set_path_effects([
            path_effects.Stroke(linewidth=1.5, foreground='black'),
            path_effects.Normal()
        ])

        cell.set_linewidth(0)

    # Redibujar ambas figuras
    fig_map.canvas.draw()
    fig_map.canvas.flush_events()

    fig_table.tight_layout()
    fig_table.canvas.draw()
    fig_table.canvas.flush_events()

    # Mostrar ambas figuras
    plt.figure(fig_map.number)
    plt.show(block=False)

    plt.figure(fig_table.number)
    plt.show(block=False)
    

# Para guardar si querés:
# fig_map.savefig("data/countries_map.png", dpi=300)
# fig_table.savefig("data/countries_table.png", dpi=300)
