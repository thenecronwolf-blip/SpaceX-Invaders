import pygame, random, math, sys, os
from assets.sprites import load_sprites
from assets.ui import generate_stars, draw_stars, neon_text, button

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 960, 640
FPS = 60

MENU, PLAYING, PAUSED, GAME_OVER = "menu", "playing", "paused", "gameover"

# ---------------- INIT ----------------
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceX: Mars Last Stand")
clock = pygame.time.Clock()

sprites = load_sprites()

# ---------------- AUDIO ----------------
try:
    pygame.mixer.music.load("assets/music.wav")
    pygame.mixer.music.play(-1)
    shoot = pygame.mixer.Sound("assets/shoot.wav")
    boom = pygame.mixer.Sound("assets/explosion.wav")
except:
    shoot = boom = None

font = pygame.font.SysFont("consolas", 20)
big = pygame.font.SysFont("consolas", 48)

# ---------------- STATE ----------------
state = MENU
stars = generate_stars(WIDTH, HEIGHT)

player = pygame.Rect(WIDTH//2-30, HEIGHT-70, 60, 30)
bullets, enemy_bullets = [], []

aliens = []
ROWS, COLS = 4, 9
alien_dir = 1
alien_speed = 1.3
wave = 1

boss = None
boss_hp = 0
boss_active = False

score = 0

# ---------------- FUNCTIONS ----------------
def spawn_wave():
    aliens.clear()
    for r in range(ROWS):
        for c in range(COLS):
            aliens.append(pygame.Rect(120+c*70, 80+r*50, 40, 30))

def spawn_boss():
    global boss, boss_hp, boss_active
    boss = pygame.Rect(WIDTH//2-120, 50, 240, 80)
    boss_hp = 300 + wave * 60
    boss_active = True

spawn_wave()

# ---------------- MAIN LOOP ----------------
while True:
    clock.tick(FPS)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                if state == PLAYING:
                    state = PAUSED
                elif state == PAUSED:
                    state = PLAYING

            if e.key == pygame.K_SPACE and state == PLAYING:
                bullets.append(pygame.Rect(player.centerx-4, player.top, 8, 16))
                if shoot: shoot.play()

    # ================= MENU =================
    if state == MENU:
        screen.fill((10,10,20))
        draw_stars(screen, stars)

        title = neon_text("SPACEX: MARS LAST STAND", big, (255,80,200))
        screen.blit(title, (WIDTH//2-title.get_width()//2, 140))

        play_btn = pygame.Rect(WIDTH//2-140, 300, 280, 60)
        quit_btn = pygame.Rect(WIDTH//2-140, 380, 280, 60)

        surf, start = button(play_btn, "LAUNCH MISSION", mouse, click)
        screen.blit(surf, play_btn)

        surf, quit_game = button(quit_btn, "ABORT", mouse, click)
        screen.blit(surf, quit_btn)

        if start:
            state = PLAYING
        if quit_game:
            pygame.quit()
            sys.exit()

        pygame.display.flip()
        continue

    # ================= PAUSED =================
    if state == PAUSED:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180))
        screen.blit(overlay, (0,0))

        pause = neon_text("PAUSED", big, (80,200,255))
        screen.blit(pause, (WIDTH//2-pause.get_width()//2, 280))

        pygame.display.flip()
        continue

    # ================= GAME OVER =================
    if state == GAME_OVER:
        screen.fill((10,10,20))
        draw_stars(screen, stars)

        over = neon_text("MISSION FAILED", big, (255,80,80))
        screen.blit(over, (WIDTH//2-over.get_width()//2, 240))

        pygame.display.flip()
        continue

    # ================= GAMEPLAY =================
    screen.fill((90,20,20))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.x -= 7
    if keys[pygame.K_RIGHT]: player.x += 7
    player.x = max(0, min(WIDTH-player.width, player.x))

    for b in bullets[:]:
        b.y -= 10
        if b.bottom < 0:
            bullets.remove(b)

    if not boss_active:
        edge = False
        for a in aliens:
            a.x += alien_speed * alien_dir
            if a.left <= 0 or a.right >= WIDTH:
                edge = True
        if edge:
            alien_dir *= -1
            for a in aliens:
                a.y += 18

        if random.random() < 0.02 and aliens:
            s = random.choice(aliens)
            enemy_bullets.append(pygame.Rect(s.centerx, s.bottom, 8, 14))

    if boss_active:
        boss.x += int(math.sin(pygame.time.get_ticks()*0.002) * 3)
        if random.random() < 0.05:
            enemy_bullets.append(pygame.Rect(boss.centerx, boss.bottom, 10, 18))

    for b in bullets[:]:
        for a in aliens[:]:
            if b.colliderect(a):
                bullets.remove(b)
                aliens.remove(a)
                score += 10
                if boom: boom.play()
                break
        if boss_active and b.colliderect(boss):
            boss_hp -= 6
            bullets.remove(b)
            if boss_hp <= 0:
                boss_active = False
                wave += 1
                spawn_wave()

    for eb in enemy_bullets[:]:
        eb.y += 6
        if eb.colliderect(player):
            state = GAME_OVER
        if eb.top > HEIGHT:
            enemy_bullets.remove(eb)

    if not aliens and not boss_active:
        spawn_boss()

    screen.blit(sprites["player"], player)
    for a in aliens: screen.blit(sprites["alien"], a)
    for b in bullets: screen.blit(sprites["bullet"], b)
    for eb in enemy_bullets: screen.blit(sprites["enemy_bullet"], eb)
    if boss_active:
        screen.blit(sprites["boss"], boss)
        pygame.draw.rect(screen,(80,255,160),(boss.x,boss.y-10,boss.width*(boss_hp/400),6))

    screen.blit(font.render(f"Score {score} | Wave {wave}",True,(240,240,240)),(10,10))
    pygame.display.flip()
