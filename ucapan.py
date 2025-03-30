import pygame
import sys
import random
import math
import requests
from itertools import cycle
from pygame import gfxdraw

# Inisialisasi Pygame
pygame.init()

# Ukuran layar
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ucapan Hari Raya Idul Fitri")

# Warna
GOLD = (255, 215, 0)
GREEN = (0, 128, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (0, 128, 128)
PURPLE = (128, 0, 128)

# Font
title_font = pygame.font.SysFont("Arial", 48, bold=True)
text_font = pygame.font.SysFont("Arial", 24)
subtitle_font = pygame.font.SysFont("Arial", 32, bold=True)

# Mengambil ucapan dari file di GitHub
def get_ucapan():
    try:
        response = requests.get('https://raw.githubusercontent.com/RelV-Dev/Image/refs/heads/main/ucapan.txt')
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Mohon Maaf Lahir dan Batin"
    except:
        return "Mohon Maaf Lahir dan Batin"

ucapan = get_ucapan()

# Kelas untuk partikel bintang
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(1, 3)
        self.speed = random.uniform(0.1, 0.5)
        self.brightness = random.uniform(0.5, 1)
        self.color = (
            int(255 * self.brightness),
            int(215 * self.brightness),
            int(random.uniform(0, 100) * self.brightness)
        )
    
    def update(self):
        self.y += self.speed
        self.brightness = random.uniform(0.5, 1)
        self.color = (
            int(255 * self.brightness),
            int(215 * self.brightness),
            int(random.uniform(0, 100) * self.brightness)
        )
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

# Kelas untuk menggambar bulan sabit
class CrescentMoon:
    def __init__(self):
        self.x = WIDTH - 100
        self.y = 100
        self.radius = 40
        self.angle = 0
    
    def update(self):
        self.angle += 0.01
    
    def draw(self):
        # Lingkaran utama (bulan)
        pygame.draw.circle(screen, GOLD, (self.x, self.y), self.radius)
        
        # Lingkaran bayangan (untuk membuat efek sabit)
        shadow_x = self.x + 15 * math.sin(self.angle)
        pygame.draw.circle(screen, (25, 25, 60), (int(shadow_x), self.y), self.radius - 5)

# Kelas untuk menggambar masjid
class Mosque:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 150
        self.base_width = 300
        self.base_height = 150
        self.dome_radius = 50
        self.minaret_height = 100
        self.minaret_width = 20
        self.pulse = 0
    
    def update(self):
        self.pulse += 0.05
        if self.pulse > 2 * math.pi:
            self.pulse = 0
    
    def draw(self):
        # Dasar masjid
        base_rect = pygame.Rect(
            self.x - self.base_width // 2,
            self.y,
            self.base_width,
            self.base_height
        )
        pygame.draw.rect(screen, TEAL, base_rect)
        
        # Kubah utama
        dome_center_x = self.x
        dome_center_y = self.y
        pygame.draw.circle(screen, GOLD, (dome_center_x, dome_center_y), self.dome_radius)
        
        # Menara kiri
        left_minaret_x = self.x - self.base_width // 2 + 20
        pygame.draw.rect(
            screen, 
            TEAL, 
            (left_minaret_x, self.y - self.minaret_height, self.minaret_width, self.minaret_height)
        )
        pygame.draw.circle(screen, GOLD, (left_minaret_x + self.minaret_width // 2, self.y - self.minaret_height), 10)
        
        # Menara kanan
        right_minaret_x = self.x + self.base_width // 2 - 20 - self.minaret_width
        pygame.draw.rect(
            screen, 
            TEAL, 
            (right_minaret_x, self.y - self.minaret_height, self.minaret_width, self.minaret_height)
        )
        pygame.draw.circle(screen, GOLD, (right_minaret_x + self.minaret_width // 2, self.y - self.minaret_height), 10)
        
        # Pintu masjid
        door_width = 50
        door_height = 80
        door_x = self.x - door_width // 2
        door_y = self.y + self.base_height - door_height
        pygame.draw.rect(screen, PURPLE, (door_x, door_y, door_width, door_height))
        
        # Jendela masjid
        window_width = 30
        window_height = 40
        window_padding = 80
        
        # Jendela kiri
        left_window_x = self.x - window_padding - window_width // 2
        left_window_y = self.y + 50
        pygame.draw.rect(
            screen, 
            WHITE, 
            (left_window_x, left_window_y, window_width, window_height),
            border_radius=10
        )
        
        # Jendela kanan
        right_window_x = self.x + window_padding - window_width // 2
        right_window_y = self.y + 50
        pygame.draw.rect(
            screen, 
            WHITE, 
            (right_window_x, right_window_y, window_width, window_height),
            border_radius=10
        )
        
        # Efek cahaya pada kubah
        glow_factor = (math.sin(self.pulse) + 1) / 2
        glow_radius = int(self.dome_radius + 10 * glow_factor)
        pygame.draw.circle(screen, (255, 215, int(100 * glow_factor)), (dome_center_x, dome_center_y), glow_radius, 2)

# Kelas untuk animasi ketupat
class Ketupat:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(-100, -20)
        self.size = random.randint(20, 40)
        self.speed = random.uniform(1, 3)
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.02, 0.02)
        self.color = random.choice([GREEN, TEAL, GOLD])
    
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        if self.y > HEIGHT + 100:
            self.reset()
    
    def reset(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(-100, -20)
        self.speed = random.uniform(1, 3)
        self.color = random.choice([GREEN, TEAL, GOLD])
    
    def draw(self):
        points = []
        for i in range(4):
            angle = self.rotation + i * math.pi / 2
            x = self.x + self.size * math.cos(angle)
            y = self.y + self.size * math.sin(angle)
            points.append((x, y))
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, BLACK, points, 2)

# Kelas untuk lampu hias
class DecorativeLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.colors = cycle([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        self.current_color = next(self.colors)
        self.size = 6
        self.pulse = random.uniform(0, 2 * math.pi)
        self.pulse_speed = random.uniform(0.05, 0.1)
    
    def update(self):
        self.pulse += self.pulse_speed
        if self.pulse > 2 * math.pi:
            self.pulse = 0
            self.current_color = next(self.colors)
    
    def draw(self):
        glow_factor = (math.sin(self.pulse) + 1) / 2
        current_size = self.size * (0.8 + 0.4 * glow_factor)
        
        # Lampu utama
        pygame.draw.circle(screen, self.current_color, (int(self.x), int(self.y)), int(current_size))
        
        # Cahaya
        glow_color = (
            min(255, self.current_color[0] + 50),
            min(255, self.current_color[1] + 50),
            min(255, self.current_color[2] + 50),
            int(100 * glow_factor)
        )
        
        pygame.gfxdraw.filled_circle(
            screen, 
            int(self.x), 
            int(self.y), 
            int(current_size + 2), 
            glow_color
        )

# Inisialisasi objek
stars = [Star() for _ in range(100)]
moon = CrescentMoon()
mosque = Mosque()
ketupats = [Ketupat() for _ in range(15)]

# Buat lampu hias di bagian atas layar
lights = []
for i in range(20):
    x = 40 * i + 20
    y = 20
    lights.append(DecorativeLight(x, y))

# Buat lampu hias di bagian bawah layar
for i in range(20):
    x = 40 * i + 20
    y = HEIGHT - 20
    lights.append(DecorativeLight(x, y))

# Waktu
clock = pygame.time.Clock()

# Loop utama
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Warna latar belakang gradien (biru malam)
    screen.fill((25, 25, 60))
    
    # Update dan gambar bintang
    for star in stars:
        star.update()
        star.draw()
    
    # Update dan gambar bulan
    moon.update()
    moon.draw()
    
    # Update dan gambar ketupat
    for ketupat in ketupats:
        ketupat.update()
        ketupat.draw()
    
    # Update dan gambar masjid
    mosque.update()
    mosque.draw()
    
    # Update dan gambar lampu hias
    for light in lights:
        light.update()
        light.draw()
    
    # Teks Selamat Hari Raya di bagian atas
    title_text = title_font.render("Selamat Hari Raya Idul Fitri", True, GOLD)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 80))
    screen.blit(title_text, title_rect)
    
    # Subteks "1445 H"
    year_text = subtitle_font.render("1445 H", True, GOLD)
    year_rect = year_text.get_rect(center=(WIDTH // 2, 130))
    screen.blit(year_text, year_rect)
    
    # Tampilkan ucapan
    text = text_font.render(ucapan, True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(text, text_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
