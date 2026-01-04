import random
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image as ImageWidget
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)

def get_image_path(filename):
    path = resource_path(os.path.join("codeandstuff", "Images", filename))
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    return path

def get_sound_path(filename):
    path = resource_path(os.path.join("codeandstuff", "Sounds", filename))
    if not os.path.exists(path):
        raise FileNotFoundError(f"Sound not found: {path}")
    return path

Window.size = (900, 900)
Window.minimum_size = (900, 900)
Window.maximum_size = (900, 900)
Window.resizable = False
Window.borderless = False

class Player:
    def __init__(self, color, image_path):
        self.color = color
        self.position = 0
        self.image_path = image_path

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = FloatLayout()

        self.background = Image(source=get_image_path('home screen.png'),
                                allow_stretch=True, keep_ratio=False)
        layout.add_widget(self.background)

        self.start_button = Button(text='Start Game', size_hint=(0.6, 0.3),
                                   pos_hint={'x': 0.20, 'y': 0.43},
                                   background_color=(1, 1, 1, 0), color=(0, 0, 0, 1))
        self.start_button.bind(on_press=self.start_game)
        layout.add_widget(self.start_button)

        self.exit_button = Button(text='Exit', size_hint=(0.5, 0.2),
                                  pos_hint={'x': 0.24, 'y': 0.31},
                                  background_color=(1, 1, 1, 0), color=(0, 0, 0, 1))
        self.exit_button.bind(on_press=App.get_running_app().stop)
        layout.add_widget(self.exit_button)

        self.about_button = Button(text='About Developer', size_hint=(0.3, 0.1),
                                   pos_hint={'x': 0.33, 'y': 0.21},
                                   background_color=(1, 1, 1, 0), color=(0, 0, 0, 1))
        self.about_button.bind(on_press=self.show_about_popup)
        layout.add_widget(self.about_button)

        self.add_widget(layout)

    def start_game(self, instance):
        self.manager.current = 'game_screen'

    def show_about_popup(self, instance):
        school_logo = Image(source=get_image_path('school_logo.jpeg'),
                            size_hint=(None, None), size=(200, 200))
        developer_info = Label(text="Developer: Ishant\nClass: 11th PCM\nSchool: The Avenue Public School",
                               color=(1, 1, 1, 1))
        content = FloatLayout()
        content.add_widget(school_logo)
        content.add_widget(developer_info)
        school_logo.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
        developer_info.pos_hint = {'center_x': 0.5, 'center_y': 0.2}
        popup = Popup(title="About Developer", content=content,
                      size_hint=(None, None), size=(400, 400))
        popup.open()

class BoardGame(Screen):
    def __init__(self, **kwargs):
        super(BoardGame, self).__init__(**kwargs)
        self.layout = FloatLayout()

        # Board image fills the screen.
        self.board_image = Image(source=get_image_path('Board.jpg'),
                                 size_hint=(1, 1), allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(self.board_image)

        # Update player positions when board size changes.
        self.board_image.bind(size=lambda instance, value: self.update_player_position(animate=False))

        # Create two players.
        self.red_player = Player('RED', get_image_path('RED.png'))
        self.blue_player = Player('BLUE', get_image_path('BLUE.png'))
        # Start with red.
        self.current_player = self.red_player
        # Game state flag - prevents further actions after someone wins.
        self.game_over = False

        self.roll_button = Button(text='Roll Dice', size_hint=(0.2, 0.1),
                                  pos_hint={'x': 0.4, 'y': 0.05},
                                  background_color=(1, 1, 1, 0), color=(0, 0, 0, 1))
        self.roll_button.bind(on_press=self.roll_dice)
        self.layout.add_widget(self.roll_button)

        # Status label shows both players' positions and next turn.
        self.status_label = Label(
            text=self.get_status_text(),
            size_hint=(0.4, 0.1),
            pos_hint={'x': 0.01, 'y': 0.01},
            color=(0, 0, 0, 1)
        )
        self.layout.add_widget(self.status_label)

        # Define fixed player image size.
        self.player_size = (0.035 * 800, 0.05 * 800)
        self.red_image = ImageWidget(source=self.red_player.image_path,
                                     size_hint=(None, None), size=self.player_size)
        self.blue_image = ImageWidget(source=self.blue_player.image_path,
                                      size_hint=(None, None), size=self.player_size)
        self.layout.add_widget(self.red_image)
        self.layout.add_widget(self.blue_image)

        # Initial positioning.
        self.update_player_position(animate=False)

        # Define snakes and ladders.
        self.snakes = {39: 4, 47: 16, 51: 29, 89: 54, 94: 57, 99: 10}
        self.ladders = {7: 29, 14: 37, 20: 38, 34: 64, 69: 87, 80: 96}

        self.add_widget(self.layout)
        Window.bind(on_key_down=self.on_keyboard_down)

        # Load sound effects.
        self.dice_sound = SoundLoader.load(get_sound_path('dice_roll.mp3'))
        self.snake_sound = SoundLoader.load(get_sound_path('Accident.mp3'))
        self.ladder_sound = SoundLoader.load(get_sound_path('Bonus.mp3'))
        self.win_sound = SoundLoader.load(get_sound_path('win_sound.mp3'))

    def get_status_text(self):
        return (f"Red: {self.red_player.position}    Blue: {self.blue_player.position}\n"
                f"Next Turn: {self.current_player.color}")

    def roll_dice(self, instance=None):
        # Ignore roll attempts after game end.
        if getattr(self, 'game_over', False):
            return
        dice_value = random.randint(1, 6)
        if self.dice_sound:
            self.dice_sound.play()

        # Special rule for near-win.
        if self.current_player.position == 98 and dice_value not in [2, 6]:
            self.show_message(f"{self.current_player.color}: Roll a 2 or 6 to win!")
            self.switch_player()
            return

        new_position = self.current_player.position + dice_value
        if new_position > 100:
            self.show_message(f"{self.current_player.color}: You rolled a {dice_value}. You cannot move!")
            self.switch_player()
            return

        self.current_player.position = new_position

        # Check for snake.
        if self.current_player.position in self.snakes:
            end_position = self.snakes[self.current_player.position]
            message = random.choice([
                "You oversped. Slow down!", "Red light jump! Be careful!",
                "No helmet! Protect yourself!", "Distracted driving is dangerous!"
            ])
            self.show_message(f"{message} You slid to {end_position}!")
            self.current_player.position = end_position
            if self.snake_sound:
                self.snake_sound.play()
        # Check for ladder.
        elif self.current_player.position in self.ladders:
            end_position = self.ladders[self.current_player.position]
            message = random.choice([
                "Great safety move!", "Good job following rules!",
                "Well done!", "Traffic rules win!"
            ])
            self.show_message(f"{message} You climbed to {end_position}!")
            self.current_player.position = end_position
            if self.ladder_sound:
                self.ladder_sound.play()

        # Check for win.
        if self.current_player.position == 100:
            self.update_player_position(animate=True)
            self.show_winner(self.current_player.color)
            if self.win_sound:
                self.win_sound.play()
            return

        self.update_player_position(animate=True)
        self.switch_player()

    def switch_player(self):
        # Switch turns.
        if self.current_player == self.red_player:
            self.current_player = self.blue_player
        else:
            self.current_player = self.red_player
        self.status_label.text = self.get_status_text()

    def update_player_position(self, animate=False):
        red_x, red_y = self.calculate_position(self.red_player.position)
        blue_x, blue_y = self.calculate_position(self.blue_player.position)
        if animate:
            Animation(pos_hint={'x': red_x, 'y': red_y}, duration=0.3).start(self.red_image)
            Animation(pos_hint={'x': blue_x, 'y': blue_y}, duration=0.3).start(self.blue_image)
        else:
            self.red_image.pos_hint = {'x': red_x, 'y': red_y}
            self.blue_image.pos_hint = {'x': blue_x, 'y': blue_y}
        self.status_label.text = self.get_status_text()

    def calculate_position(self, position):
        # Original board design values.
        board_width = 1500.0
        board_height = 1200.0
        left_border = 50.0
        bottom_border = 34.0
        tile_width = 141.0
        tile_height = 105.0

        row = (position - 1) // 10
        col = (position - 1) % 10

        if row % 2 == 0:
            x = left_border + col * tile_width + (tile_width - (0.035 * 800)) / 2
        else:
            x = board_width - left_border - (col + 1) * tile_width + (tile_width - (0.035 * 800)) / 2

        y = bottom_border + row * tile_height + (tile_height - (0.05 * 800)) / 2

        # Return as fraction of board dimensions for pos_hint.
        return x / board_width, y / board_height

    def show_winner(self, color):
        # Mark game over and disable further rolls.
        self.game_over = True
        self.roll_button.disabled = True

        content = FloatLayout()
        msg = Label(text=f"Welcome home, {color}! You've made it to the finish line!",
                    pos_hint={'center_x': 0.5, 'center_y': 0.65}, color=(1, 1, 1, 1))
        play_btn = Button(text='Play Again', size_hint=(0.4, 0.18), pos_hint={'x': 0.05, 'y': 0.12})
        exit_btn = Button(text='Exit to Home', size_hint=(0.4, 0.18), pos_hint={'x': 0.55, 'y': 0.12})
        content.add_widget(msg)
        content.add_widget(play_btn)
        content.add_widget(exit_btn)

        popup = Popup(title='Game Over', content=content,
                      size_hint=(None, None), size=(420, 300))

        def on_play(instance):
            popup.dismiss()
            self.reset_game()

        def on_exit(instance):
            popup.dismiss()
            if self.manager:
                self.manager.current = 'home_screen'

        play_btn.bind(on_press=on_play)
        exit_btn.bind(on_press=on_exit)
        popup.open()

    def reset_game(self):
        # Reset positions and UI to start a new game.
        self.red_player.position = 0
        self.blue_player.position = 0
        self.current_player = self.red_player
        self.game_over = False
        self.roll_button.disabled = False
        self.update_player_position(animate=True)
        self.status_label.text = self.get_status_text()

    def show_message(self, message):
        # Split message into lines where needed.
        message = message.replace('!', '!\n')
        popup_content = Label(text=message,
                              size_hint=(None, None),
                              size=(380, 150),
                              color=(1, 1, 1, 1),
                              text_size=(370, None),
                              halign='center',
                              valign='middle')
        popup = Popup(title="Event", content=popup_content,
                      size_hint=(None, None), size=(400, 200))
        popup.open()

    def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if text == " ":
            self.roll_dice()
        elif keycode == 27:
            self.handle_escape()

    def handle_escape(self):
        if self.manager.current == 'game_screen':
            self.manager.current = 'home_screen'
        else:
            App.get_running_app().stop()

class SnakesLaddersApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(HomeScreen(name='home_screen'))
        self.sm.add_widget(BoardGame(name='game_screen'))
        Window.bind(on_resize=self.on_window_resize)
        return self.sm

    def on_window_resize(self, window, width, height):
        current_screen = self.sm.current_screen
        if hasattr(current_screen, 'update_player_position'):
            current_screen.update_player_position()

if __name__ == '__main__':
    SnakesLaddersApp().run()
