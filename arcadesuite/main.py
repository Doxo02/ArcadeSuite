from nicegui import ui, app, run
from nicegui.events import KeyEventArguments
from utils import get_games, get_json
from hackatari import HackAtari
import numpy as np
from base64 import b64encode


GAMES = get_games('../res/')
select_index = 0
select_class = 'no-shadow'
select_color = 'bg-light-blue-2'
normal_color = 'bg-grey-1'

selection_index = 0

selected_game = GAMES[0]
modif_selection = list()

selected_mode = []

cards = dict()

app.native.start_args["debug"] = True


@ui.page("/")
def main_page():
    global cards
    ui.add_head_html('<style>body {background-color: bisque;}</style>')
    with ui.grid(columns=6):
        for game in GAMES:
            cards[game] = ui.card(align_items='center')
            with cards[game]:
                ui.label(game)
                ui.image('../res/' + game + '/icon.png')
            if game == GAMES[select_index]:
                cards[game].classes(select_color)
                continue
            else:
                cards[game].classes('no-shadow ' + normal_color)

    def handle_key(e: KeyEventArguments):
        global select_index
        global selected_game
        prev_select = select_index
        update = False
        if e.action.keydown:
            if e.key.arrow_left:
                if select_index > 0:
                    select_index -= 1
                else:
                    select_index = len(GAMES) - 1
                update = True
            elif e.key.arrow_right:
                if select_index < len(GAMES) - 1:
                    select_index += 1
                else:
                    select_index = 0
                update = True
            elif e.key == 'Enter':
                ui.navigate.to("/selection")

        if update:
            selected_game = GAMES[select_index]
            cards[GAMES[select_index]]._classes.remove(select_class)
            cards[GAMES[select_index]]._classes.remove(normal_color)
            cards[GAMES[select_index]]._classes.append(select_color)

            cards[GAMES[prev_select]]._classes.append(select_class)
            cards[GAMES[prev_select]]._classes.append(normal_color)
            cards[GAMES[prev_select]]._classes.remove(select_color)

            cards[GAMES[select_index]].update()
            cards[GAMES[prev_select]].update()

    ui.keyboard(on_key=handle_key)


@ui.page("/selection")
def main_page():
    global selected_mode
    global selected_game
    global selection_index

    # Button states
    playerSelection = ["Player", "Agent"]
    selection_index = 0

    # Selcted Option in GUI
    selection = []

    # Single Player vs. Multiplayer
    meta = get_json(f"../res/{selected_game}/meta.json")
    singlePlayer = not meta['multiplayer']

    cards = dict()
    labels = dict()
    ui.add_head_html('<style>body {background-color: bisque;}</style>')

    def single_player_selection():
        with ui.row(align_items="center").classes("absolute-center w-full h-full items-center"):
            with ui.column(align_items="left").classes("justify-center w-[50%] q-pl-md"):
                with ui.column().classes('w-full h-screen justify-center align-center items-center'):
                    ui.label(selected_game).classes('w-full text-2xl text-center align-middle font-bold')

                    cards[selection[0]] = ui.card(align_items='center').classes(select_color + ' w-full ')
                    with cards[selection[0]]:
                        labels[selection[0]] = ui.label(playerSelection[0]).classes('text-2xl text-center align-middle font-bold')

                    cards[selection[1]] = ui.card(align_items='center').classes(select_class + ' ' + normal_color + ' w-full')
                    with cards[selection[1]]:
                        labels[selection[1]]= ui.label("Submit").classes('text-2xl text-center align-middle font-bold')

            ui.image(f"../res/{selected_game}/icon.png").props("fit='contain' width='50%'").classes("fixed-right h-full")

    def multi_player__selection():
        with ui.row(align_items="center").classes("absolute-center w-full h-full items-center"):
            with ui.column(align_items="left").classes("justify-center w-[50%] q-pl-md"):
                with ui.column().classes('w-full h-screen justify-center align-center items-center'):
                    ui.label(selected_game).classes('w-full text-2xl text-center align-middle font-bold')

                    with ui.row().classes('w-full gap-4 justify-center'):
                        cards[selection[0]] = ui.card(align_items='center').classes(select_color + ' w-1/3')
                        with cards[selection[0]]:
                            labels[selection[0]] = ui.label(playerSelection[0]).classes('text-2xl text-center align-middle font-bold')

                        cards[selection[1]] = ui.card(align_items='center').classes(select_class + ' ' + normal_color + ' w-1/3')
                        with cards[selection[1]]:
                            labels[selection[1]] = ui.label(playerSelection[0]).classes('text-2xl text-center align-middle font-bold')

                    cards[selection[2]] = ui.card(align_items='center').classes(select_class + ' ' + normal_color + ' w-full')
                    with cards[selection[2]]:
                        ui.label("Submit").classes('text-2xl text-center align-middle font-bold')
            ui.image(f"../res/{selected_game}/icon.png").props("fit='contain' width='50%'").classes("fixed-right h-full")

    def updateStatus(name):
        current_label = labels[name]

        previous_index = playerSelection.index(current_label.text)
        new_index = (previous_index + 1) % len(playerSelection)

        current_label.text = playerSelection[new_index]
        current_label.update()

    def returnStatus():
        for name in selection:
            if name != 'Submit':
                selected_mode.append(labels[name].text)

    def handle_key(e: KeyEventArguments):
        global selection_index
        prev_index = selection_index
        update = False

        if singlePlayer:
            if e.action.keydown:
                if e.key == 'Escape':
                    ui.navigate.to("/")
                elif e.key.arrow_up:
                    if selection_index > 0:
                        selection_index -= 1
                    else:
                        selection_index = len(selection)-1
                    update = True
                elif e.key.arrow_down:
                    if selection_index < len(selection)-1:
                        selection_index += 1
                    else:
                        selection_index = 0
                    update = True
                elif e.key == 'Enter':
                    if selection_index != len(selection)-1:
                        updateStatus(selection[selection_index])
                    else:
                        returnStatus()
                        ui.navigate.to("/menu")
        else:
            if e.action.keydown:
                if e.key == 'Escape':
                    ui.navigate.to("/")
                elif e.key.arrow_up:
                    if selection_index < len(selection)-1:
                        selection_index = len(selection)-1
                    else:
                        selection_index = 0
                    update = True
                elif e.key.arrow_down:
                    if selection_index < len(selection)-1:
                        selection_index = len(selection)-1
                    else:
                        selection_index = 0
                    update = True
                elif e.key.arrow_right or e.key.arrow_left:
                    if selection_index < len(selection)-1:
                        selection_index = (selection_index + 1) % 2
                        update = True
                elif e.key == 'Enter':
                    if selection_index != len(selection)-1:
                        updateStatus(selection[selection_index])
                    else:
                        returnStatus()
                        ui.navigate.to("/menu")

        if update:
            select = selection[selection_index]
            print(select)

            cards[selection[selection_index]]._classes.remove(select_class)
            cards[selection[selection_index]]._classes.remove(normal_color)
            cards[selection[selection_index]]._classes.append(select_color)

            cards[selection[prev_index]]._classes.append(select_class)
            cards[selection[prev_index]]._classes.append(normal_color)
            cards[selection[prev_index]]._classes.remove(select_color)

            cards[selection[selection_index]].update()
            cards[selection[prev_index]].update()

    if singlePlayer:
        selection.extend(['PlayerA', 'Submit'])
        single_player_selection()

    else:
        selection.extend(['PlayerA', 'PlayerB', 'Submit'])
        multi_player__selection()

    ui.keyboard(on_key=handle_key)


@ui.page("/menu")
def menu_page():
    global selected_modif_index
    global selected_modif
    global modif_cards

    ui.add_head_html('<style>body {background-color: bisque;}</style>')
    meta = get_json(f"../res/{selected_game}/meta.json")
    modifs = list()
    for modif in meta["modifs"]:
        modifs.append(modif)
    modifs.append("Submit")

    selected_modif_index = 0
    selected_modif = modifs[selected_modif_index]

    modif_cards = dict()
    modif_checkboxes = dict()
    with ui.row(align_items="center").classes("absolute-center w-full h-full items-center"):
        with ui.column(align_items="left").classes("justify-center w-[50%] q-pl-md"):
            for modif in modifs:
                modif_cards[modif] = ui.card().tight()
                with modif_cards[modif] as card:
                    with ui.row():
                        if modif == "Submit":
                            card.classes("q-pa-sm")
                            ui.label(modif)
                        else:
                            card.classes("q-pr-md")
                            modif_checkboxes[modif] = ui.checkbox(modif)
                if modif == selected_modif:
                    modif_cards[modif].classes(f"{select_color}")
                else:
                    modif_cards[modif].classes(f"{normal_color} {select_class}")
        ui.image(f"../res/{selected_game}/icon.png").props("fit='contain'").classes("absolute-right h-full w-[50%]")

    def handle_key(e: KeyEventArguments):
        global selected_modif_index
        global selected_modif

        update = False

        prev_select = selected_modif_index
        if e.action.keydown:
            if e.key == 'Escape':
                ui.navigate.to("/selection")
            elif e.key.arrow_up:
                if selected_modif_index > 0:
                    selected_modif_index -= 1
                else:
                    selected_modif_index = len(modifs) - 1
                update = True
            elif e.key.arrow_down:
                if selected_modif_index < len(modifs) - 1:
                    selected_modif_index += 1
                else:
                    selected_modif_index = 0
                update = True
            elif e.key == "Enter":
                if selected_modif == "Submit":
                    global modif_selection
                    for modif in modifs:
                        if modif != "Submit" and modif_checkboxes[modif].value:
                            modif_selection.append(modif)
                    ui.navigate.to("/game_screen")
                    # TODO: route to next menu page or delete objects and rebuild for other menu options?
                else:
                    modif_checkboxes[selected_modif].set_value(not modif_checkboxes[selected_modif].value)

        if update:
            selected_modif = modifs[selected_modif_index]
            modif_cards[modifs[selected_modif_index]]._classes.remove(select_class)
            modif_cards[modifs[selected_modif_index]]._classes.remove(normal_color)
            modif_cards[modifs[selected_modif_index]]._classes.append(select_color)

            modif_cards[modifs[prev_select]]._classes.append(select_class)
            modif_cards[modifs[prev_select]]._classes.append(normal_color)
            modif_cards[modifs[prev_select]]._classes.remove(select_color)

            modif_cards[modifs[selected_modif_index]].update()
            modif_cards[modifs[prev_select]].update()

    ui.keyboard(on_key=handle_key)


@ui.page("/game_screen")
async def game_screen():
    # create HackAtari environment
    env = HackAtari(selected_game, modifs=modif_selection, render_mode="rgb_array", dopamine_pooling=False)
    obs, _ = env.reset()
    nstep = 1
    tr = 0

    async def run_game():
        nonlocal env
        nonlocal tr
        nonlocal nstep

        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        tr += reward
        if terminated or truncated:
            print(info)
            print(tr)
            tr = 0
            env.reset()
        nstep += 1

        rgb_data = env.render()
        # rgb_data = np.random.randint(0, 256, (1050, 800, 3), dtype=np.uint8)
        rgba_data = np.concatenate([rgb_data, 255 * np.ones((210, 160, 1), dtype=np.uint8)], axis=-1)  # Add alpha channel
        pixel_data = rgba_data.tobytes()  # Convert to raw bytes

        # Encode the data as Base64
        base64_pixel_data = b64encode(pixel_data).decode('utf-8')  # Convert to string for JavaScript

        # Debug: Print a snippet of the Base64 string
        # print("Sending Base64 data (truncated):", base64_pixel_data[:32])

        # Call the JavaScript update function
        ui.run_javascript(f"updateCanvas('{base64_pixel_data}')")

        # print(frame[0])
        # TODO: put data on canvas

    # thread = threading.Thread(target=run_game)
    # thread.start()
    timer = ui.timer(0.1, run_game)

    def handle_key(e: KeyEventArguments):
        nonlocal env
        if e.action.keydown:
            if e.key == 'q':
                timer.cancel()
                ui.navigate.to("/")

    canvas_script = '''
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const imageData = ctx.createImageData(160, 210);

    function updateCanvas(base64Data) {
        const binaryData = atob(base64Data);  // Decode Base64 string to binary
        var pixelData = new Uint8ClampedArray(binaryData.length);
        for (let i = 0; i < binaryData.length; i++) {
            pixelData[i] = binaryData.charCodeAt(i);  // Convert binary string to byte array
        }
        imageData.data.set(pixelData);  // Set pixel data on canvas
        ctx.putImageData(imageData, 0, 0);  // Render to canvas
    };
    '''

    ui.add_head_html('<style>body {background-color: bisque;}</style>')
    ui.add_body_html(f"<canvas id='gameCanvas' style='border: 1px solid black;' width=160px height=210px/><script>{canvas_script}</script>")
    ui.keyboard(on_key=handle_key)


ui.run(title="Arcade Suite", native=True, dark=False, window_size=(900, 600))
