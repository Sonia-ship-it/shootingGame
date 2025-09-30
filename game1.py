import pygame
import random
import time
import serial  


use_keyboard = False  


if not use_keyboard:

    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)  


pygame.init()
WIDTH, HEIGHT = 600, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("War Shooter - Arduino Joystick")


background_img = pygame.image.load("background.jpeg").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

player_img = pygame.image.load("gun.jpeg").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 50))

bullet_img = pygame.image.load("bul.jpeg").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (12, 24))

enemy_img = pygame.image.load("car.jpeg").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (40, 40))

enemy_bullet_img = pygame.transform.scale(bullet_img, (10, 20))


player_x = WIDTH // 2
player_y = HEIGHT - 70
player_health = 10
bullets = []
enemy_bullets = []


NUM_ENEMIES = 5
enemy_fire_rate = 800         
enemy_bullet_speed = 12
MAX_SIMULTANEOUS_SHOOTERS = 3
SIMULTANEOUS_COOLDOWN = 8000   

enemies = []
for _ in range(NUM_ENEMIES):
    x = random.randint(50, WIDTH-50)
    y = random.randint(20, 150)
    last_shot = pygame.time.get_ticks() - random.randint(0, enemy_fire_rate)
    enemies.append({'pos':[x,y], 'last_shot': last_shot, 'cooldown_end': 0})

score = 0
font = pygame.font.SysFont("Arial", 24)
target_score = 20


WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
HUD_ALPHA = 180  


hud_surface = pygame.Surface((WIDTH-20, 60), pygame.SRCALPHA)
hud_surface.fill((30,30,30,HUD_ALPHA))


running = True
clock = pygame.time.Clock()

while running:
    clock.tick(30)
    win.blit(background_img, (0,0))

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    if not use_keyboard:
        try:
            if arduino.in_waiting > 0:
                data = arduino.readline().decode().strip()
                vals = data.split(",")
                if len(vals) == 3:
                    xVal, yVal, button = map(int, vals)
                
                    if xVal < 400:  
                        player_x -= 5
                    elif xVal > 600:  
                        player_x += 5
                   
                    if button == 0:
                        bullets.append([player_x, player_y])
        except:
            pass

    player_x = max(25, min(WIDTH - 25, player_x))

    for b in bullets: b[1] -= 12
    bullets = [b for b in bullets if b[1] > 0]


    current_time = pygame.time.get_ticks()
    shooters_this_frame = 0

    for e in enemies:
        e['pos'][1] += 1
        if e['pos'][1] > HEIGHT:
            e['pos'] = [random.randint(50, WIDTH-50), random.randint(20, 150)]
            e['last_shot'] = current_time - random.randint(0, enemy_fire_rate)
            e['cooldown_end'] = 0


    for e in enemies:
        if shooters_this_frame >= MAX_SIMULTANEOUS_SHOOTERS:
            break
        if current_time >= e['cooldown_end'] and current_time - e['last_shot'] >= enemy_fire_rate:
            if random.choice([True, False]):
                enemy_bullets.append([e['pos'][0]+20, e['pos'][1]+30])
                e['last_shot'] = current_time
                shooters_this_frame += 1

    for e in enemies:
        if current_time - e['last_shot'] < enemy_fire_rate:
            continue
        if not any(eb for eb in enemy_bullets if eb[0] == e['pos'][0]+20 and eb[1] == e['pos'][1]+30):
            e['cooldown_end'] = current_time + SIMULTANEOUS_COOLDOWN

    
    for eb in enemy_bullets: eb[1] += enemy_bullet_speed
    enemy_bullets = [eb for eb in enemy_bullets if eb[1] < HEIGHT]


    player_rect = pygame.Rect(player_x-25, player_y, player_img.get_width(), player_img.get_height())
    for b in bullets[:]:
        for e in enemies[:]:
            enemy_rect = pygame.Rect(e['pos'][0], e['pos'][1], enemy_img.get_width(), enemy_img.get_height())
            if pygame.Rect(b[0], b[1], bullet_img.get_width(), bullet_img.get_height()).colliderect(enemy_rect):
                bullets.remove(b)
                enemies.remove(e)
                enemies.append({'pos':[random.randint(50, WIDTH-50), random.randint(20, 150)],
                                'last_shot': current_time - random.randint(0, enemy_fire_rate),
                                'cooldown_end': 0})
                score += 1
                break

    for eb in enemy_bullets[:]:
        eb_rect = pygame.Rect(eb[0], eb[1], enemy_bullet_img.get_width(), enemy_bullet_img.get_height())
        if eb_rect.colliderect(player_rect):
            enemy_bullets.remove(eb)
            player_health -= 1
            break


    win.blit(player_img, (player_x-25, player_y))
    for b in bullets: win.blit(bullet_img, (b[0], b[1]))
    for e in enemies: win.blit(enemy_img, (e['pos'][0], e['pos'][1]))
    for eb in enemy_bullets: win.blit(enemy_bullet_img, (eb[0], eb[1]))


    win.blit(hud_surface, (10,10))
    pygame.draw.rect(win, RED, (15,15,210,26))
    pygame.draw.rect(win, GREEN, (15,15,21*player_health,26))
    pygame.draw.rect(win, WHITE, (15,15,210,26),2)

    score_surface = pygame.Surface((130,40), pygame.SRCALPHA)
    score_surface.fill((0,0,0,HUD_ALPHA))
    win.blit(score_surface, (WIDTH-140,10))
    score_text = font.render(f"Score: {score}", True, WHITE)
    win.blit(score_text, (WIDTH-130,15))

   
    if score >= target_score:
        win_text = font.render("YOU WIN!", True, GREEN)
        pygame.draw.rect(win, (0,0,0,100), (WIDTH//2-80, HEIGHT//2-30, 160, 60))
        win.blit(win_text, (WIDTH//2-60, HEIGHT//2))
        pygame.display.update()
        pygame.time.delay(3000)
        running = False
    if player_health <= 0:
        lose_text = font.render("GAME OVER", True, RED)
        pygame.draw.rect(win, (0,0,0,100), (WIDTH//2-90, HEIGHT//2-30, 180, 60))
        win.blit(lose_text, (WIDTH//2-80, HEIGHT//2))
        pygame.display.update()
        pygame.time.delay(3000)
        running = False

    pygame.display.update()

pygame.quit()
