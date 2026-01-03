import pygame
import random
import math
import sys
import threading
import socket

# ================== CONFIG ==================
WIDTH, HEIGHT = 960, 640
FPS = 60

# Twitch Chat (OPTIONAL)
TWITCH_ENABLED = True
TWITCH_CHANNEL = "joeyxherrmann"
TWITCH_NICK = "joeyxherrmann"
TWITCH_TOKEN = "esnrqwdawebhypvcwtdie0y9ft7ktn"

# ================== INIT ==================
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceX: Mars Last Stand")
clock = pygame.time.Clock()

# ================== AUDIO ==================
try:
    pygame.mixer.music.load("assets/music.wav")
    pygame.mixer.music.play(-1)
    shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
    boom_sound = pygame.mixer.Sound("assets/explosion.wav")
except:
    shoot_sound = boom_sound = None

# ================== COLORS ==================
MARS_RED = (90, 20, 20)
NEON_PINK = (255, 60, 200)
NEON_BLUE = (80, 200, 255)
NEON_GREEN = (80, 255, 160)
WHITE = (240, 240, 240)

font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 48)

# ================== PLAYER ==================
player = pygame.Rect(WIDTH//2 - 30, HEIGHT - 70, 60, 30)
player_speed = 7
player_hp = 3

bullets = []
alien_bullets = []

# ================== ALIENS ==================
aliens = []
ROWS, COLS = 4, 9
alien_dir = 1
alien_speed = 1.2
wave = 1

# ================== BOSS ==================
boss = None
boss_hp = 0
boss_active = False

# ================== FX ==================
shake = 0

# ================== CHAT FLAGS ==================
chat_commands = {
    "faster": False,
    "boss": False,
    "storm": False
}

# ================== FUNCTIONS ==================
def spawn_wave():
    global aliens
    aliens.clear()
    for r in range(ROWS):
        for c in range(COLS):
            aliens.append(pygame.Rect(120 + c*70, 80 + r*50, 40, 30))

def spawn_boss():
    global boss, boss_hp, boss_active
    boss = pygame.Rect(WIDTH//2 - 120, 60, 240, 80)
    boss_hp = 200 + wave * 50
    boss_active = True

def draw_glow_rect(rect, color):
    glow = pygame.Surface((rect.width+10, rect.height+10), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*color, 100), glow.get_rect(), border_radius=8)
    screen.blit(glow, (rect.x-5, rect.y-5))
    pygame.draw.rect(screen, color, rect, border_radius=6)

def screen_shake():
    global shake
    shake = 10

# ================== TWITCH CHAT ==================
def twitch_chat():
    sock = socket.socket()
    sock.connect(("irc.chat.twitch.tv", 6667))
    sock.send(f"PASS {TWITCH_TOKEN}\n".encode())
    sock.send(f"NICK {TWITCH_NICK}\n".encode())
    sock.send(f"JOIN #{TWITCH_CHANNEL}\n".encode())

    while True:
        msg = sock.recv(2048).decode(errors="ignore")
        if "faster" in msg:
            chat_commands["faster"] = True
        if "boss" in msg:
            chat_commands["boss"] = True
        if "storm" in msg:
            chat_commands["storm"] = True

if TWITCH_ENABLED:
    threading.Thread(target=twitch_chat, daemon=True).start()

# ================== START ==================
spawn_wave()
score = 0
game_over = False

# ================== MAIN LOOP ==================
while True:
    clock.tick(FPS)
    offset_x = offset_y = 0

    if shake > 0:
        offset_x = random.randint(-shake, shake)
        offset_y = random.randint(-shake, shake)
        shake -= 1

    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill(MARS_RED)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bullets.append(pygame.Rect(player.centerx-4, player.top, 8, 14))
                if shoot_sound: shoot_sound.play()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
    player.x = max(0, min(WIDTH-player.width, player.x))

    # -------- BULLETS --------
    for b in bullets[:]:
        b.y -= 9
        if b.bottom < 0:
            bullets.remove(b)

    # -------- ALIENS --------
    if not boss_active:
        edge = False
        for a in aliens:
            a.x += alien_speed * alien_dir
            if a.right >= WIDTH or a.left <= 0:
                edge = True
        if edge:
            alien_dir *= -1
            for a in aliens:
                a.y += 18

        if random.random() < 0.02:
            shooter = random.choice(aliens)
            alien_bullets.append(pygame.Rect(shooter.centerx, shooter.bottom, 6, 12))

    # -------- BOSS --------
    if boss_active:
        boss.x += int(math.sin(pygame.time.get_ticks()*0.002) * 3)
        if random.random() < 0.05:
            alien_bullets.append(pygame.Rect(boss.centerx, boss.bottom, 10, 18))

    # -------- COLLISIONS --------
    for b in bullets[:]:
        for a in aliens[:]:
            if b.colliderect(a):
                aliens.remove(a)
                bullets.remove(b)
                score += 10
                if boom_sound: boom_sound.play()
                break
        if boss_active and b.colliderect(boss):
            boss_hp -= 5
            bullets.remove(b)
            screen_shake()
            if boss_hp <= 0:
                boss_active = False
                wave += 1
                spawn_wave()

    for ab in alien_bullets[:]:
        ab.y += 6
        if ab.colliderect(player):
            game_over = True
        if ab.top > HEIGHT:
            alien_bullets.remove(ab)

    # -------- WAVE CONTROL --------
    if not aliens and not boss_active:
        spawn_boss()

    # -------- CHAT EFFECTS --------
    if chat_commands["faster"]:
        alien_speed += 0.5
        chat_commands["faster"] = False
    if chat_commands["boss"] and not boss_active:
        spawn_boss()
        chat_commands["boss"] = False

    # -------- DRAW --------
    draw_glow_rect(player, NEON_BLUE)
    for b in bullets:
        draw_glow_rect(b, NEON_GREEN)
    for a in aliens:
        draw_glow_rect(a, NEON_PINK)
    for ab in alien_bullets:
        pygame.draw.rect(surface, (255,100,100), ab)

    if boss_active:
        draw_glow_rect(boss, (255, 80, 80))
        pygame.draw.rect(surface, NEON_GREEN, (boss.x, boss.y-10, boss.width*(boss_hp/300), 6))

    surface.blit(font.render(f"Score: {score}  Wave: {wave}", True, WHITE), (10, 10))
    screen.blit(surface, (offset_x, offset_y))
    pygame.display.flip()
