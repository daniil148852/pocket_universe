"""
POCKET UNIVERSE — Симулятор Вселенной
Создай планету. Развивай жизнь. Стань богом.
"""

import json
import random
import math
import time
import os
import hashlib

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line, Triangle, PushMatrix, PopMatrix, Rotate
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty, ListProperty


# ==================== КОНФИГУРАЦИЯ ====================

LIFE_STAGES = [
    {'name': 'Lifeless', 'icon': '.', 'min_conditions': {}},
    {'name': 'Bacteria', 'icon': '*', 'min_conditions': {'water': 10, 'temperature': 20}},
    {'name': 'Algae', 'icon': '~', 'min_conditions': {'water': 25, 'oxygen': 5, 'temperature': 25}},
    {'name': 'Plants', 'icon': 'Y', 'min_conditions': {'water': 35, 'oxygen': 15, 'temperature': 30}},
    {'name': 'Insects', 'icon': 'x', 'min_conditions': {'water': 40, 'oxygen': 25, 'biomass': 20}},
    {'name': 'Fish', 'icon': '>', 'min_conditions': {'water': 50, 'oxygen': 30, 'biomass': 30}},
    {'name': 'Reptiles', 'icon': 'S', 'min_conditions': {'water': 45, 'oxygen': 40, 'biomass': 40}},
    {'name': 'Mammals', 'icon': 'M', 'min_conditions': {'water': 50, 'oxygen': 50, 'biomass': 50}},
    {'name': 'Primates', 'icon': 'P', 'min_conditions': {'water': 55, 'oxygen': 55, 'biomass': 60}},
    {'name': 'Civilization', 'icon': 'A', 'min_conditions': {'water': 50, 'oxygen': 60, 'biomass': 70}},
    {'name': 'Industrial', 'icon': 'I', 'min_conditions': {'water': 45, 'oxygen': 55, 'biomass': 65}},
    {'name': 'Space Age', 'icon': 'V', 'min_conditions': {'water': 40, 'oxygen': 50, 'biomass': 60}},
    {'name': 'Galactic', 'icon': '@', 'min_conditions': {'water': 40, 'oxygen': 50, 'biomass': 55}},
]

EVENTS = {
    'meteor_small': {
        'name': 'Small Meteor',
        'desc': 'A small meteor strikes!',
        'effects': {'biomass': -5, 'temperature': 2},
        'chance': 0.03
    },
    'meteor_large': {
        'name': 'EXTINCTION EVENT',
        'desc': 'Massive asteroid impact!',
        'effects': {'biomass': -40, 'temperature': -15, 'oxygen': -10},
        'chance': 0.005
    },
    'volcano': {
        'name': 'Volcanic Eruption',
        'desc': 'Volcanoes release gases',
        'effects': {'temperature': 3, 'oxygen': -2, 'biomass': -3},
        'chance': 0.02
    },
    'ice_age': {
        'name': 'Ice Age Begins',
        'desc': 'Global cooling event',
        'effects': {'temperature': -20, 'water': -10, 'biomass': -15},
        'chance': 0.008
    },
    'solar_flare': {
        'name': 'Solar Flare',
        'desc': 'Intense radiation!',
        'effects': {'temperature': 10, 'biomass': -8},
        'chance': 0.015
    },
    'evolution_boost': {
        'name': 'Evolution Leap!',
        'desc': 'Rapid mutation event',
        'effects': {'biomass': 15},
        'chance': 0.02
    },
    'ocean_bloom': {
        'name': 'Ocean Bloom',
        'desc': 'Algae explosion!',
        'effects': {'oxygen': 8, 'biomass': 5},
        'chance': 0.025
    },
    'magnetic_shift': {
        'name': 'Magnetic Reversal',
        'desc': 'Poles are shifting',
        'effects': {'biomass': -5},
        'chance': 0.01
    },
}

DIVINE_POWERS = {
    'rain': {
        'name': 'Divine Rain',
        'desc': '+15 Water',
        'cost': 20,
        'effects': {'water': 15}
    },
    'sunlight': {
        'name': 'Blessed Sun',
        'desc': '+10 Temperature',
        'cost': 15,
        'effects': {'temperature': 10}
    },
    'breath': {
        'name': 'Breath of Life',
        'desc': '+20 Oxygen',
        'cost': 30,
        'effects': {'oxygen': 20}
    },
    'seed': {
        'name': 'Genesis Seed',
        'desc': '+25 Biomass',
        'cost': 40,
        'effects': {'biomass': 25}
    },
    'shield': {
        'name': 'Divine Shield',
        'desc': 'Block next disaster',
        'cost': 50,
        'effects': {'shield': 1}
    },
    'miracle': {
        'name': 'Miracle',
        'desc': '+10 to all stats',
        'cost': 100,
        'effects': {'water': 10, 'oxygen': 10, 'temperature': 5, 'biomass': 10}
    },
}

ACHIEVEMENTS = {
    'creator': {'name': 'Creator', 'desc': 'Create your first planet', 'reward': 50},
    'life_giver': {'name': 'Life Giver', 'desc': 'Evolve to Bacteria', 'reward': 30},
    'gardener': {'name': 'Gardener', 'desc': 'Evolve to Plants', 'reward': 50},
    'shepherd': {'name': 'Shepherd', 'desc': 'Evolve to Mammals', 'reward': 100},
    'civilization': {'name': 'Civilization', 'desc': 'Reach Civilization', 'reward': 200},
    'space_age': {'name': 'Space Age', 'desc': 'Reach Space Age', 'reward': 500},
    'galactic': {'name': 'Galactic Empire', 'desc': 'Reach Galactic stage', 'reward': 1000},
    'survivor': {'name': 'Survivor', 'desc': 'Survive an extinction event', 'reward': 150},
    'balance': {'name': 'Balance', 'desc': 'All stats above 50', 'reward': 100},
    'ancient': {'name': 'Ancient World', 'desc': 'Planet age > 1000 years', 'reward': 200},
    'multiverse': {'name': 'Multiverse', 'desc': 'Create 3 planets', 'reward': 300},
    'divine_10': {'name': 'Minor God', 'desc': 'Use 10 divine powers', 'reward': 100},
    'divine_50': {'name': 'Major God', 'desc': 'Use 50 divine powers', 'reward': 300},
}

PLANET_TYPES = {
    'terra': {'name': 'Terra', 'color': (0.2, 0.5, 0.3), 'water': 50, 'temp': 50},
    'ocean': {'name': 'Ocean World', 'color': (0.1, 0.3, 0.7), 'water': 80, 'temp': 40},
    'desert': {'name': 'Desert World', 'color': (0.7, 0.5, 0.2), 'water': 20, 'temp': 70},
    'ice': {'name': 'Ice World', 'color': (0.7, 0.8, 0.9), 'water': 60, 'temp': 10},
    'volcanic': {'name': 'Volcanic World', 'color': (0.5, 0.2, 0.1), 'water': 15, 'temp': 85},
}


# ==================== УТИЛИТЫ ====================

def get_data_path():
    if platform == 'android':
        try:
            from android.storage import app_storage_path
            return app_storage_path()
        except:
            pass
    return os.path.expanduser('~')


def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()[:16]


# ==================== МЕНЕДЖЕР ДАННЫХ ====================

class DataManager:
    def __init__(self):
        self.data_path = get_data_path()
        self.users_file = os.path.join(self.data_path, 'pu_users.json')
        self.current_user = None
        self.user_data = None
    
    def load_users(self):
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'users': {}}
    
    def save_users(self, data):
        try:
            with open(self.users_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def register(self, username, pin):
        users = self.load_users()
        if username.lower() in [u.lower() for u in users['users']]:
            return False, "Username already exists"
        if len(username) < 3:
            return False, "Username too short"
        if len(pin) < 4:
            return False, "PIN must be 4+ digits"
        
        users['users'][username] = {
            'pin_hash': hash_pin(pin),
            'created': time.time(),
            'divine_energy': 100,
            'total_planets': 0,
            'achievements': [],
            'divine_uses': 0,
            'planets': {},
            'current_planet': None,
            'stats': {
                'total_years': 0,
                'max_life_stage': 0,
                'disasters_survived': 0
            }
        }
        self.save_users(users)
        return True, "Account created!"
    
    def login(self, username, pin):
        users = self.load_users()
        if username not in users['users']:
            return False, "User not found"
        if users['users'][username]['pin_hash'] != hash_pin(pin):
            return False, "Wrong PIN"
        
        self.current_user = username
        self.user_data = users['users'][username]
        return True, "Welcome back!"
    
    def save_current_user(self):
        if not self.current_user:
            return
        users = self.load_users()
        users['users'][self.current_user] = self.user_data
        self.save_users(users)
    
    def logout(self):
        self.save_current_user()
        self.current_user = None
        self.user_data = None


# ==================== ПЛАНЕТА ====================

class Planet:
    def __init__(self, name, planet_type='terra'):
        self.name = name
        self.type = planet_type
        self.type_data = PLANET_TYPES.get(planet_type, PLANET_TYPES['terra'])
        
        self.water = self.type_data['water']
        self.oxygen = 5
        self.temperature = self.type_data['temp']
        self.biomass = 0
        
        self.age = 0
        self.life_stage = 0
        self.population = 0
        self.shield = 0
        
        self.history = []
        self.created = time.time()
    
    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'water': self.water,
            'oxygen': self.oxygen,
            'temperature': self.temperature,
            'biomass': self.biomass,
            'age': self.age,
            'life_stage': self.life_stage,
            'population': self.population,
            'shield': self.shield,
            'history': self.history[-50:],
            'created': self.created
        }
    
    @classmethod
    def from_dict(cls, data):
        p = cls(data['name'], data.get('type', 'terra'))
        p.water = data.get('water', 50)
        p.oxygen = data.get('oxygen', 5)
        p.temperature = data.get('temperature', 50)
        p.biomass = data.get('biomass', 0)
        p.age = data.get('age', 0)
        p.life_stage = data.get('life_stage', 0)
        p.population = data.get('population', 0)
        p.shield = data.get('shield', 0)
        p.history = data.get('history', [])
        p.created = data.get('created', time.time())
        return p
    
    def clamp_stats(self):
        self.water = max(0, min(100, self.water))
        self.oxygen = max(0, min(100, self.oxygen))
        self.temperature = max(-50, min(150, self.temperature))
        self.biomass = max(0, min(100, self.biomass))
    
    def simulate_tick(self):
        self.age += 1
        event_happened = None
        
        # Естественные процессы
        if self.biomass > 10:
            self.oxygen += self.biomass * 0.02
        if self.water > 30 and self.temperature > 20 and self.temperature < 80:
            self.biomass += 0.1
        if self.temperature > 100:
            self.biomass -= 0.5
            self.water -= 0.3
        if self.temperature < 0:
            self.biomass -= 0.2
        
        # Случайные события
        for event_id, event in EVENTS.items():
            if random.random() < event['chance']:
                if self.shield > 0 and event['effects'].get('biomass', 0) < -10:
                    self.shield -= 1
                    event_happened = {'id': 'shield_block', 'name': 'Shield Blocked!', 
                                     'desc': f"Blocked: {event['name']}"}
                else:
                    for stat, value in event['effects'].items():
                        if stat == 'shield':
                            continue
                        current = getattr(self, stat, 0)
                        setattr(self, stat, current + value)
                    event_happened = event
                    self.history.append({
                        'year': self.age,
                        'event': event['name']
                    })
                break
        
        # Обновление стадии жизни
        self.update_life_stage()
        
        # Популяция
        if self.life_stage >= 9:  # Civilization+
            self.population = int(self.biomass * 1000000 * (self.life_stage - 8))
        elif self.life_stage >= 5:
            self.population = int(self.biomass * 10000)
        else:
            self.population = int(self.biomass * 100)
        
        self.clamp_stats()
        return event_happened
    
    def update_life_stage(self):
        for i in range(len(LIFE_STAGES) - 1, -1, -1):
            stage = LIFE_STAGES[i]
            conditions_met = True
            for stat, min_val in stage['min_conditions'].items():
                current = getattr(self, stat, 0)
                if current < min_val:
                    conditions_met = False
                    break
            if conditions_met:
                if i > self.life_stage:
                    self.history.append({
                        'year': self.age,
                        'event': f"Evolved to {stage['name']}!"
                    })
                self.life_stage = i
                break
    
    def get_life_stage_name(self):
        return LIFE_STAGES[self.life_stage]['name']
    
    def apply_divine_power(self, power_id):
        if power_id not in DIVINE_POWERS:
            return False
        power = DIVINE_POWERS[power_id]
        for stat, value in power['effects'].items():
            if stat == 'shield':
                self.shield += value
            else:
                current = getattr(self, stat, 0)
                setattr(self, stat, current + value)
        self.clamp_stats()
        self.history.append({
            'year': self.age,
            'event': f"Divine: {power['name']}"
        })
        return True


# ==================== ВИДЖЕТ ПЛАНЕТЫ ====================

class PlanetWidget(Widget):
    def __init__(self, planet=None, **kwargs):
        super().__init__(**kwargs)
        self.planet = planet
        self.rotation = 0
        self.stars = []
        self.bind(size=self.setup_stars, pos=self.redraw)
        Clock.schedule_interval(self.animate, 1/30)
    
    def setup_stars(self, *args):
        self.stars = []
        for _ in range(50):
            self.stars.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'size': random.uniform(1, 3),
                'brightness': random.uniform(0.3, 1.0)
            })
        self.redraw()
    
    def animate(self, dt):
        self.rotation += dt * 10
        if self.rotation > 360:
            self.rotation -= 360
        self.redraw()
    
    def redraw(self, *args):
        self.canvas.clear()
        
        with self.canvas:
            # Фон космоса
            Color(0.02, 0.02, 0.08, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Звёзды
            for star in self.stars:
                b = star['brightness'] * (0.7 + 0.3 * math.sin(time.time() * 2 + star['x']))
                Color(b, b, b * 1.1, 1)
                Ellipse(
                    pos=(self.x + star['x'], self.y + star['y']),
                    size=(star['size'], star['size'])
                )
            
            if self.planet:
                # Планета
                cx = self.x + self.width / 2
                cy = self.y + self.height / 2
                radius = min(self.width, self.height) * 0.3
                
                # Свечение
                pc = self.planet.type_data['color']
                Color(pc[0], pc[1], pc[2], 0.2)
                Ellipse(pos=(cx - radius * 1.3, cy - radius * 1.3), 
                       size=(radius * 2.6, radius * 2.6))
                
                # Основа планеты
                Color(pc[0], pc[1], pc[2], 1)
                Ellipse(pos=(cx - radius, cy - radius), 
                       size=(radius * 2, radius * 2))
                
                # Детали на планете
                self.draw_planet_details(cx, cy, radius)
                
                # Атмосфера (если есть кислород)
                if self.planet.oxygen > 20:
                    alpha = min(0.3, self.planet.oxygen / 200)
                    Color(0.5, 0.7, 1.0, alpha)
                    Ellipse(pos=(cx - radius * 1.1, cy - radius * 1.1), 
                           size=(radius * 2.2, radius * 2.2))
                
                # Щит
                if self.planet.shield > 0:
                    Color(0.3, 0.8, 1.0, 0.3)
                    Line(circle=(cx, cy, radius * 1.2), width=2)
    
    def draw_planet_details(self, cx, cy, radius):
        if not self.planet:
            return
        
        # Вода (синие пятна)
        if self.planet.water > 20:
            Color(0.1, 0.3, 0.7, 0.6)
            for i in range(int(self.planet.water / 20)):
                angle = (self.rotation + i * 72) * math.pi / 180
                dist = radius * 0.5
                x = cx + math.cos(angle) * dist - radius * 0.2
                y = cy + math.sin(angle) * dist - radius * 0.15
                Ellipse(pos=(x, y), size=(radius * 0.4, radius * 0.3))
        
        # Биомасса (зелёные пятна)
        if self.planet.biomass > 10:
            Color(0.2, 0.6, 0.2, 0.5)
            for i in range(int(self.planet.biomass / 15)):
                angle = (self.rotation * 0.5 + i * 51) * math.pi / 180
                dist = radius * 0.4
                x = cx + math.cos(angle) * dist - radius * 0.15
                y = cy + math.sin(angle) * dist - radius * 0.15
                Ellipse(pos=(x, y), size=(radius * 0.3, radius * 0.3))
        
        # Облака
        if self.planet.water > 30:
            Color(1, 1, 1, 0.3)
            for i in range(3):
                angle = (self.rotation * 1.5 + i * 120) * math.pi / 180
                dist = radius * 0.6
                x = cx + math.cos(angle) * dist - radius * 0.25
                y = cy + math.sin(angle) * dist * 0.5
                Ellipse(pos=(x, y), size=(radius * 0.5, radius * 0.15))


# ==================== ЭКРАНЫ ====================

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


# ==================== ЭКРАН ВХОДА ====================

class LoginScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
        
        # Заголовок
        layout.add_widget(Label(
            text='POCKET UNIVERSE',
            font_size=sp(32),
            size_hint=(1, 0.12),
            bold=True,
            color=(0.7, 0.5, 1, 1)
        ))
        
        layout.add_widget(Label(
            text='Create worlds. Evolve life. Become God.',
            font_size=sp(14),
            size_hint=(1, 0.05),
            color=(0.5, 0.5, 0.6, 1)
        ))
        
        # Космическая анимация
        self.planet_preview = PlanetWidget(size_hint=(1, 0.25))
        preview_planet = Planet("Preview", "terra")
        preview_planet.water = 60
        preview_planet.oxygen = 40
        preview_planet.biomass = 30
        self.planet_preview.planet = preview_planet
        layout.add_widget(self.planet_preview)
        
        # Форма входа
        form = BoxLayout(orientation='vertical', size_hint=(1, 0.35), spacing=dp(10))
        
        form.add_widget(Label(text='Username', font_size=sp(14), size_hint=(1, 0.15), 
                             halign='left', color=(0.7, 0.7, 0.8, 1)))
        self.username_input = TextInput(
            hint_text='Enter username',
            multiline=False,
            size_hint=(1, 0.2),
            font_size=sp(16),
            background_color=(0.15, 0.15, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.7, 0.5, 1, 1)
        )
        form.add_widget(self.username_input)
        
        form.add_widget(Label(text='PIN Code', font_size=sp(14), size_hint=(1, 0.15),
                             halign='left', color=(0.7, 0.7, 0.8, 1)))
        self.pin_input = TextInput(
            hint_text='Enter 4+ digit PIN',
            multiline=False,
            password=True,
            size_hint=(1, 0.2),
            font_size=sp(16),
            background_color=(0.15, 0.15, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.7, 0.5, 1, 1),
            input_filter='int'
        )
        form.add_widget(self.pin_input)
        
        layout.add_widget(form)
        
        # Статус
        self.status_label = Label(
            text='',
            font_size=sp(13),
            size_hint=(1, 0.05),
            color=(1, 0.5, 0.5, 1)
        )
        layout.add_widget(self.status_label)
        
        # Кнопки
        buttons = BoxLayout(size_hint=(1, 0.1), spacing=dp(15))
        
        login_btn = Button(
            text='LOGIN',
            font_size=sp(16),
            background_color=(0.3, 0.5, 0.3, 1),
            background_normal=''
        )
        login_btn.bind(on_release=lambda x: self.do_login())
        
        register_btn = Button(
            text='REGISTER',
            font_size=sp(16),
            background_color=(0.3, 0.3, 0.5, 1),
            background_normal=''
        )
        register_btn.bind(on_release=lambda x: self.do_register())
        
        buttons.add_widget(login_btn)
        buttons.add_widget(register_btn)
        layout.add_widget(buttons)
        
        self.add_widget(layout)
    
    def do_login(self):
        username = self.username_input.text.strip()
        pin = self.pin_input.text.strip()
        
        if not username or not pin:
            self.status_label.text = "Please fill all fields"
            self.status_label.color = (1, 0.5, 0.5, 1)
            return
        
        success, msg = self.app.data_manager.login(username, pin)
        if success:
            self.status_label.text = msg
            self.status_label.color = (0.5, 1, 0.5, 1)
            self.username_input.text = ''
            self.pin_input.text = ''
            Clock.schedule_once(lambda dt: self.app.go_to_menu(), 0.5)
        else:
            self.status_label.text = msg
            self.status_label.color = (1, 0.5, 0.5, 1)
    
    def do_register(self):
        username = self.username_input.text.strip()
        pin = self.pin_input.text.strip()
        
        if not username or not pin:
            self.status_label.text = "Please fill all fields"
            self.status_label.color = (1, 0.5, 0.5, 1)
            return
        
        success, msg = self.app.data_manager.register(username, pin)
        if success:
            self.status_label.text = msg + " Please login."
            self.status_label.color = (0.5, 1, 0.5, 1)
        else:
            self.status_label.text = msg
            self.status_label.color = (1, 0.5, 0.5, 1)


# ==================== ГЛАВНОЕ МЕНЮ ====================

class MenuScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Заголовок
        self.welcome_label = Label(
            text='Welcome, Player!',
            font_size=sp(24),
            size_hint=(1, 0.08),
            color=(0.7, 0.5, 1, 1)
        )
        layout.add_widget(self.welcome_label)
        
        # Энергия
        self.energy_label = Label(
            text='Divine Energy: 100',
            font_size=sp(16),
            size_hint=(1, 0.05),
            color=(1, 0.9, 0.3, 1)
        )
        layout.add_widget(self.energy_label)
        
        # Превью планеты
        self.planet_widget = PlanetWidget(size_hint=(1, 0.3))
        layout.add_widget(self.planet_widget)
        
        self.planet_name_label = Label(
            text='No planet selected',
            font_size=sp(18),
            size_hint=(1, 0.05),
            color=(0.8, 0.8, 0.9, 1)
        )
        layout.add_widget(self.planet_name_label)
        
        # Кнопки
        buttons_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.35), spacing=dp(8))
        
        btn_config = [
            ('CONTINUE PLANET', (0.2, 0.5, 0.3, 1), self.continue_planet),
            ('CREATE NEW PLANET', (0.3, 0.3, 0.6, 1), self.create_planet),
            ('MY PLANETS', (0.4, 0.3, 0.4, 1), self.my_planets),
            ('ACHIEVEMENTS', (0.5, 0.4, 0.2, 1), self.achievements),
        ]
        
        for text, color, callback in btn_config:
            btn = Button(
                text=text,
                font_size=sp(16),
                size_hint=(1, 0.23),
                background_color=color,
                background_normal=''
            )
            btn.bind(on_release=lambda x, cb=callback: cb())
            buttons_layout.add_widget(btn)
        
        layout.add_widget(buttons_layout)
        
        # Logout
        logout_btn = Button(
            text='LOGOUT',
            font_size=sp(14),
            size_hint=(1, 0.06),
            background_color=(0.4, 0.2, 0.2, 1),
            background_normal=''
        )
        logout_btn.bind(on_release=lambda x: self.logout())
        layout.add_widget(logout_btn)
        
        self.add_widget(layout)
    
    def on_pre_enter(self):
        self.update_display()
    
    def update_display(self):
        data = self.app.data_manager.user_data
        if not data:
            return
        
        self.welcome_label.text = f"Welcome, {self.app.data_manager.current_user}!"
        self.energy_label.text = f"Divine Energy: {data.get('divine_energy', 100)}"
        
        current = data.get('current_planet')
        if current and current in data.get('planets', {}):
            planet = Planet.from_dict(data['planets'][current])
            self.planet_widget.planet = planet
            self.planet_name_label.text = f"{planet.name} - {planet.get_life_stage_name()}"
        else:
            self.planet_widget.planet = None
            self.planet_name_label.text = "No planet - Create one!"
    
    def continue_planet(self):
        data = self.app.data_manager.user_data
        current = data.get('current_planet')
        if current and current in data.get('planets', {}):
            self.app.load_planet(current)
            self.manager.transition = SlideTransition(direction='left')
            self.manager.current = 'game'
        else:
            self.planet_name_label.text = "Create a planet first!"
    
    def create_planet(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'create'
    
    def my_planets(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'planets'
    
    def achievements(self):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'achievements'
    
    def logout(self):
        self.app.data_manager.logout()
        self.manager.transition = FadeTransition()
        self.manager.current = 'login'


# ==================== СОЗДАНИЕ ПЛАНЕТЫ ====================

class CreatePlanetScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.selected_type = 'terra'
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        layout.add_widget(Label(
            text='CREATE NEW WORLD',
            font_size=sp(24),
            size_hint=(1, 0.08),
            color=(0.5, 0.7, 1, 1)
        ))
        
        # Имя
        name_box = BoxLayout(size_hint=(1, 0.08), spacing=dp(10))
        name_box.add_widget(Label(text='Name:', font_size=sp(14), size_hint=(0.25, 1)))
        self.name_input = TextInput(
            hint_text='Planet name',
            multiline=False,
            font_size=sp(16),
            size_hint=(0.75, 1),
            background_color=(0.15, 0.15, 0.2, 1),
            foreground_color=(1, 1, 1, 1)
        )
        name_box.add_widget(self.name_input)
        layout.add_widget(name_box)
        
        # Превью
        self.preview = PlanetWidget(size_hint=(1, 0.25))
        preview_planet = Planet("New", "terra")
        preview_planet.water = PLANET_TYPES['terra']['water']
        preview_planet.temperature = PLANET_TYPES['terra']['temp']
        self.preview.planet = preview_planet
        layout.add_widget(self.preview)
        
        # Тип планеты
        layout.add_widget(Label(
            text='Select Planet Type:',
            font_size=sp(14),
            size_hint=(1, 0.04),
            color=(0.7, 0.7, 0.8, 1)
        ))
        
        types_scroll = ScrollView(size_hint=(1, 0.25))
        types_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        types_grid.bind(minimum_height=types_grid.setter('height'))
        
        self.type_buttons = {}
        for type_id, type_data in PLANET_TYPES.items():
            btn = Button(
                text=f"{type_data['name']}\nWater: {type_data['water']} | Temp: {type_data['temp']}",
                font_size=sp(13),
                size_hint_y=None,
                height=dp(55),
                background_color=(0.2, 0.2, 0.25, 1),
                background_normal=''
            )
            btn.bind(on_release=lambda x, t=type_id: self.select_type(t))
            self.type_buttons[type_id] = btn
            types_grid.add_widget(btn)
        
        types_scroll.add_widget(types_grid)
        layout.add_widget(types_scroll)
        
        self.select_type('terra')
        
        # Кнопки
        buttons = BoxLayout(size_hint=(1, 0.1), spacing=dp(15))
        
        back_btn = Button(
            text='< BACK',
            font_size=sp(16),
            background_color=(0.3, 0.3, 0.35, 1),
            background_normal=''
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        
        create_btn = Button(
            text='CREATE',
            font_size=sp(16),
            background_color=(0.3, 0.5, 0.3, 1),
            background_normal=''
        )
        create_btn.bind(on_release=lambda x: self.create())
        
        buttons.add_widget(back_btn)
        buttons.add_widget(create_btn)
        layout.add_widget(buttons)
        
        self.add_widget(layout)
    
    def select_type(self, type_id):
        self.selected_type = type_id
        for tid, btn in self.type_buttons.items():
            if tid == type_id:
                btn.background_color = (0.3, 0.5, 0.4, 1)
            else:
                btn.background_color = (0.2, 0.2, 0.25, 1)
        
        type_data = PLANET_TYPES[type_id]
        self.preview.planet.type = type_id
        self.preview.planet.type_data = type_data
        self.preview.planet.water = type_data['water']
        self.preview.planet.temperature = type_data['temp']
    
    def create(self):
        name = self.name_input.text.strip()
        if not name:
            name = f"Planet-{random.randint(1000, 9999)}"
        
        planet = Planet(name, self.selected_type)
        planet_id = f"planet_{int(time.time())}"
        
        data = self.app.data_manager.user_data
        if 'planets' not in data:
            data['planets'] = {}
        
        data['planets'][planet_id] = planet.to_dict()
        data['current_planet'] = planet_id
        data['total_planets'] = data.get('total_planets', 0) + 1
        
        # Достижение
        self.app.check_achievement('creator')
        if data['total_planets'] >= 3:
            self.app.check_achievement('multiverse')
        
        self.app.data_manager.save_current_user()
        
        self.name_input.text = ''
        self.app.load_planet(planet_id)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'game'
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu'


# ==================== ИГРОВОЙ ЭКРАН ====================

class GameScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.planet = None
        self.paused = False
        self.tick_speed = 1.0
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        # Верхняя панель
        top = BoxLayout(size_hint=(1, 0.08), spacing=dp(5))
        
        self.back_btn = Button(
            text='<',
            font_size=sp(18),
            size_hint=(0.12, 1),
            background_color=(0.3, 0.3, 0.35, 1),
            background_normal=''
        )
        self.back_btn.bind(on_release=lambda x: self.go_back())
        top.add_widget(self.back_btn)
        
        self.planet_label = Label(
            text='Planet Name',
            font_size=sp(16),
            size_hint=(0.55, 1),
            color=(0.8, 0.8, 1, 1)
        )
        top.add_widget(self.planet_label)
        
        self.energy_label = Label(
            text='E: 100',
            font_size=sp(14),
            size_hint=(0.33, 1),
            color=(1, 0.9, 0.3, 1)
        )
        top.add_widget(self.energy_label)
        
        layout.add_widget(top)
        
        # Планета
        self.planet_widget = PlanetWidget(size_hint=(1, 0.28))
        layout.add_widget(self.planet_widget)
        
        # Стадия жизни
        self.life_label = Label(
            text='Lifeless',
            font_size=sp(20),
            size_hint=(1, 0.05),
            color=(0.5, 1, 0.5, 1)
        )
        layout.add_widget(self.life_label)
        
        # Возраст и популяция
        self.age_label = Label(
            text='Age: 0 years | Pop: 0',
            font_size=sp(12),
            size_hint=(1, 0.03),
            color=(0.6, 0.6, 0.7, 1)
        )
        layout.add_widget(self.age_label)
        
        # Ресурсы
        stats_grid = GridLayout(cols=2, size_hint=(1, 0.14), spacing=dp(5), padding=dp(5))
        
        self.water_bar = self.create_stat_bar('Water', (0.2, 0.5, 0.9, 1))
        self.oxygen_bar = self.create_stat_bar('Oxygen', (0.5, 0.8, 0.5, 1))
        self.temp_bar = self.create_stat_bar('Temp', (0.9, 0.5, 0.2, 1))
        self.bio_bar = self.create_stat_bar('Biomass', (0.2, 0.8, 0.3, 1))
        
        stats_grid.add_widget(self.water_bar)
        stats_grid.add_widget(self.oxygen_bar)
        stats_grid.add_widget(self.temp_bar)
        stats_grid.add_widget(self.bio_bar)
        
        layout.add_widget(stats_grid)
        
        # События
        self.event_label = Label(
            text='',
            font_size=sp(13),
            size_hint=(1, 0.05),
            color=(1, 1, 0.5, 1)
        )
        layout.add_widget(self.event_label)
        
        # Божественные силы
        layout.add_widget(Label(
            text='Divine Powers:',
            font_size=sp(12),
            size_hint=(1, 0.03),
            color=(0.6, 0.6, 0.7, 1)
        ))
        
        powers_scroll = ScrollView(size_hint=(1, 0.18))
        self.powers_grid = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, padding=dp(3))
        self.powers_grid.bind(minimum_height=self.powers_grid.setter('height'))
        
        self.power_buttons = {}
        for power_id, power in DIVINE_POWERS.items():
            btn = Button(
                text=f"{power['name']}\n({power['cost']})",
                font_size=sp(10),
                size_hint_y=None,
                height=dp(50),
                background_color=(0.25, 0.25, 0.35, 1),
                background_normal=''
            )
            btn.bind(on_release=lambda x, pid=power_id: self.use_power(pid))
            self.power_buttons[power_id] = btn
            self.powers_grid.add_widget(btn)
        
        powers_scroll.add_widget(self.powers_grid)
        layout.add_widget(powers_scroll)
        
        # Контроль скорости
        speed_box = BoxLayout(size_hint=(1, 0.06), spacing=dp(5))
        
        self.pause_btn = Button(
            text='||',
            font_size=sp(16),
            size_hint=(0.15, 1),
            background_color=(0.5, 0.3, 0.3, 1),
            background_normal=''
        )
        self.pause_btn.bind(on_release=lambda x: self.toggle_pause())
        speed_box.add_widget(self.pause_btn)
        
        speed_box.add_widget(Label(text='Speed:', font_size=sp(12), size_hint=(0.2, 1)))
        
        for speed, text in [(0.5, '0.5x'), (1, '1x'), (2, '2x'), (5, '5x')]:
            btn = Button(
                text=text,
                font_size=sp(12),
                size_hint=(0.16, 1),
                background_color=(0.3, 0.3, 0.4, 1),
                background_normal=''
            )
            btn.bind(on_release=lambda x, s=speed: self.set_speed(s))
            speed_box.add_widget(btn)
        
        layout.add_widget(speed_box)
        
        self.add_widget(layout)
        
        Clock.schedule_interval(self.game_tick, 1.0)
    
    def create_stat_bar(self, name, color):
        box = BoxLayout(orientation='vertical', spacing=dp(2))
        label = Label(text=f'{name}: 0', font_size=sp(11), size_hint=(1, 0.4), color=color)
        bar = ProgressBar(max=100, value=0, size_hint=(1, 0.6))
        box.add_widget(label)
        box.add_widget(bar)
        box.label = label
        box.bar = bar
        box.color = color
        return box
    
    def on_pre_enter(self):
        self.update_display()
    
    def set_planet(self, planet):
        self.planet = planet
        self.planet_widget.planet = planet
        self.update_display()
    
    def update_display(self):
        if not self.planet:
            return
        
        p = self.planet
        data = self.app.data_manager.user_data
        
        self.planet_label.text = p.name
        self.energy_label.text = f"E: {data.get('divine_energy', 0)}"
        self.life_label.text = p.get_life_stage_name()
        
        pop_str = self.format_population(p.population)
        self.age_label.text = f"Age: {p.age} years | Pop: {pop_str}"
        
        if p.shield > 0:
            self.age_label.text += f" | Shield: {p.shield}"
        
        self.update_stat_bar(self.water_bar, 'Water', p.water)
        self.update_stat_bar(self.oxygen_bar, 'O2', p.oxygen)
        self.update_stat_bar(self.temp_bar, 'Temp', max(0, min(100, (p.temperature + 50) / 2)))
        self.update_stat_bar(self.bio_bar, 'Bio', p.biomass)
        
        # Обновить кнопки сил
        energy = data.get('divine_energy', 0)
        for power_id, power in DIVINE_POWERS.items():
            btn = self.power_buttons[power_id]
            if energy >= power['cost']:
                btn.background_color = (0.3, 0.45, 0.3, 1)
            else:
                btn.background_color = (0.25, 0.25, 0.3, 1)
    
    def update_stat_bar(self, stat_box, name, value):
        stat_box.label.text = f"{name}: {int(value)}"
        stat_box.bar.value = max(0, min(100, value))
    
    def format_population(self, pop):
        if pop >= 1000000000:
            return f"{pop/1000000000:.1f}B"
        if pop >= 1000000:
            return f"{pop/1000000:.1f}M"
        if pop >= 1000:
            return f"{pop/1000:.1f}K"
        return str(pop)
    
    def game_tick(self, dt):
        if not self.planet or self.paused:
            return
        
        for _ in range(int(self.tick_speed)):
            event = self.planet.simulate_tick()
            
            if event:
                self.event_label.text = f"{event.get('name', 'Event')}: {event.get('desc', '')}"
                # Проверка достижения
                if 'EXTINCTION' in event.get('name', ''):
                    if self.planet.biomass > 5:
                        self.app.check_achievement('survivor')
        
        # Генерация энергии
        data = self.app.data_manager.user_data
        energy_gen = 0.1 + (self.planet.life_stage * 0.05)
        data['divine_energy'] = min(1000, data.get('divine_energy', 0) + energy_gen * self.tick_speed)
        
        # Проверка достижений
        self.check_game_achievements()
        
        # Сохранение
        if self.planet.age % 100 == 0:
            self.save_planet()
        
        self.update_display()
    
    def check_game_achievements(self):
        p = self.planet
        if p.life_stage >= 1:
            self.app.check_achievement('life_giver')
        if p.life_stage >= 3:
            self.app.check_achievement('gardener')
        if p.life_stage >= 7:
            self.app.check_achievement('shepherd')
        if p.life_stage >= 9:
            self.app.check_achievement('civilization')
        if p.life_stage >= 11:
            self.app.check_achievement('space_age')
        if p.life_stage >= 12:
            self.app.check_achievement('galactic')
        if p.water > 50 and p.oxygen > 50 and p.biomass > 50:
            self.app.check_achievement('balance')
        if p.age > 1000:
            self.app.check_achievement('ancient')
    
    def use_power(self, power_id):
        if not self.planet:
            return
        
        data = self.app.data_manager.user_data
        power = DIVINE_POWERS.get(power_id)
        if not power:
            return
        
        if data.get('divine_energy', 0) < power['cost']:
            self.event_label.text = "Not enough Divine Energy!"
            return
        
        data['divine_energy'] -= power['cost']
        data['divine_uses'] = data.get('divine_uses', 0) + 1
        
        self.planet.apply_divine_power(power_id)
        self.event_label.text = f"Used: {power['name']}"
        
        # Достижения
        if data['divine_uses'] >= 10:
            self.app.check_achievement('divine_10')
        if data['divine_uses'] >= 50:
            self.app.check_achievement('divine_50')
        
        self.update_display()
    
    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.text = '>' if self.paused else '||'
        self.pause_btn.background_color = (0.3, 0.5, 0.3, 1) if self.paused else (0.5, 0.3, 0.3, 1)
    
    def set_speed(self, speed):
        self.tick_speed = speed
    
    def save_planet(self):
        if not self.planet:
            return
        data = self.app.data_manager.user_data
        current = data.get('current_planet')
        if current:
            data['planets'][current] = self.planet.to_dict()
        self.app.data_manager.save_current_user()
    
    def go_back(self):
        self.save_planet()
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu'


# ==================== МОИ ПЛАНЕТЫ ====================

class PlanetsScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        layout.add_widget(Label(
            text='MY PLANETS',
            font_size=sp(24),
            size_hint=(1, 0.08),
            color=(0.5, 0.7, 1, 1)
        ))
        
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(5))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        back_btn = Button(
            text='< BACK',
            font_size=sp(16),
            size_hint=(1, 0.08),
            background_color=(0.3, 0.3, 0.35, 1),
            background_normal=''
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_pre_enter(self):
        self.refresh_list()
    
    def refresh_list(self):
        self.grid.clear_widgets()
        data = self.app.data_manager.user_data
        planets = data.get('planets', {})
        current = data.get('current_planet')
        
        if not planets:
            self.grid.add_widget(Label(
                text='No planets yet!\nCreate your first world.',
                font_size=sp(16),
                size_hint_y=None,
                height=dp(80)
            ))
            return
        
        for planet_id, planet_data in planets.items():
            planet = Planet.from_dict(planet_data)
            
            is_current = planet_id == current
            bg_color = (0.25, 0.35, 0.25, 1) if is_current else (0.2, 0.2, 0.25, 1)
            
            btn = Button(
                text=f"{planet.name}\n{planet.get_life_stage_name()} | Age: {planet.age}\nPop: {planet.population:,}",
                font_size=sp(13),
                size_hint_y=None,
                height=dp(70),
                background_color=bg_color,
                background_normal='',
                halign='left',
                valign='middle'
            )
            btn.bind(on_release=lambda x, pid=planet_id: self.select_planet(pid))
            self.grid.add_widget(btn)
    
    def select_planet(self, planet_id):
        data = self.app.data_manager.user_data
        data['current_planet'] = planet_id
        self.app.data_manager.save_current_user()
        self.app.load_planet(planet_id)
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'game'
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu'


# ==================== ДОСТИЖЕНИЯ ====================

class AchievementsScreen(BaseScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        layout.add_widget(Label(
            text='ACHIEVEMENTS',
            font_size=sp(24),
            size_hint=(1, 0.08),
            color=(1, 0.8, 0.3, 1)
        ))
        
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, padding=dp(5))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        
        back_btn = Button(
            text='< BACK',
            font_size=sp(16),
            size_hint=(1, 0.08),
            background_color=(0.3, 0.3, 0.35, 1),
            background_normal=''
        )
        back_btn.bind(on_release=lambda x: self.go_back())
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_pre_enter(self):
        self.refresh_list()
    
    def refresh_list(self):
        self.grid.clear_widgets()
        data = self.app.data_manager.user_data
        unlocked = data.get('achievements', [])
        
        for ach_id, ach in ACHIEVEMENTS.items():
            is_unlocked = ach_id in unlocked
            
            if is_unlocked:
                text = f"[OK] {ach['name']}\n{ach['desc']}"
                color = (0.2, 0.35, 0.2, 1)
            else:
                text = f"[??] {ach['name']}\n{ach['desc']} | +{ach['reward']} Energy"
                color = (0.2, 0.2, 0.25, 1)
            
            lbl = Button(
                text=text,
                font_size=sp(12),
                size_hint_y=None,
                height=dp(55),
                background_color=color,
                background_normal='',
                halign='left'
            )
            self.grid.add_widget(lbl)
    
    def go_back(self):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'menu'


# ==================== ПРИЛОЖЕНИЕ ====================

class PocketUniverseApp(App):
    def build(self):
        self.title = 'Pocket Universe'
        self.data_manager = DataManager()
        
        self.sm = ScreenManager(transition=FadeTransition())
        
        self.login_screen = LoginScreen(self, name='login')
        self.menu_screen = MenuScreen(self, name='menu')
        self.create_screen = CreatePlanetScreen(self, name='create')
        self.game_screen = GameScreen(self, name='game')
        self.planets_screen = PlanetsScreen(self, name='planets')
        self.achievements_screen = AchievementsScreen(self, name='achievements')
        
        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.menu_screen)
        self.sm.add_widget(self.create_screen)
        self.sm.add_widget(self.game_screen)
        self.sm.add_widget(self.planets_screen)
        self.sm.add_widget(self.achievements_screen)
        
        return self.sm
    
    def go_to_menu(self):
        self.menu_screen.update_display()
        self.sm.current = 'menu'
    
    def load_planet(self, planet_id):
        data = self.data_manager.user_data
        if planet_id in data.get('planets', {}):
            planet = Planet.from_dict(data['planets'][planet_id])
            self.game_screen.set_planet(planet)
    
    def check_achievement(self, ach_id):
        data = self.data_manager.user_data
        if ach_id not in data.get('achievements', []):
            if 'achievements' not in data:
                data['achievements'] = []
            data['achievements'].append(ach_id)
            reward = ACHIEVEMENTS.get(ach_id, {}).get('reward', 0)
            data['divine_energy'] = data.get('divine_energy', 0) + reward
            self.data_manager.save_current_user()
    
    def on_stop(self):
        if self.game_screen.planet:
            self.game_screen.save_planet()
        self.data_manager.save_current_user()


if __name__ == '__main__':
    PocketUniverseApp().run()
