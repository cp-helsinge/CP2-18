import pygame
import time
from random import randint, choice, uniform

FRAMES_PER_SECOND = 60


class Player:
    def __init__(self, rect):
        self.rect = rect
        self.speed_pixels_per_draw = 2
        self.alive = True


class PlayerShot:
    def __init__(self, rect):
        self.rect = rect
        self.speed_pixels_per_draw = 5


class AlienShot:
    def __init__(self, rect, speed_x, speed_y):
        self.rect = rect
        self.x = rect.x
        self.y = rect.y
        self.speed_x = speed_x
        self.speed_y = speed_y


class Alien:
    def __init__(self, rect, movement_area, extra_speed):
        self.rect = rect
        self.movement_area = movement_area
        self.speed = 1 + extra_speed
        self.moving_left = True


class Star:
    def __init__(self, x, y, radius, color, speed):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.radius = radius
        self.rect = pygame.Rect((x - radius, y - radius),
                                (2 * radius, 2 * radius))


class Explosion:
    def __init__(self, center, max_radius, color):
        self.x = center[0]
        self.y = center[1]
        self.max_radius = max_radius
        self.color = color
        self.current_radius = 0
        self.grow_speed = 5
        self.shrink_speed = 1
        self.growing = True
        self.done = False


class PlayerInput:
    def __init__(self):
        self.stop = False
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.fire = False


class Graphics:
    # noinspection PyUnresolvedReferences
    def __init__(self):
        self.player = pygame.image.load("player.png").convert_alpha()
        self.player_shot = pygame.image.load("basic_shot.png").convert_alpha()
        self.alien = pygame.image.load("enemy1.png").convert_alpha()
        self.alien_shot = pygame.image.load("enemy1_shot.png").convert_alpha()
        self.status_font = pygame.font.Font(None, 40)


class GameState:
    def __init__(self, graphics, game_area):
        self.mode = "waiting"
        self.graphics = graphics
        player_center = (game_area.width // 2, game_area.height // 2)
        player_rect = graphics.player.get_rect(center=player_center)
        self.player = Player(player_rect)
        self.player_shots = []
        self.stars = []
        self.game_area = game_area
        self.has_shot = 0
        self.wave_number = 0
        self.aliens = make_wave(graphics, game_area, self.wave_number)
        self.alien_shots = []
        self.lives = 2
        self.explosions = []

        for x in range(game_area.width):
            if should_have_star():
                star = random_star_for_x(x, game_area.height)
                self.stars.append(star)


def reap_outsiders(objects, game_area):
    for obj in list(objects):
        if not game_area.colliderect(obj.rect):
            objects.remove(obj)


def move_x(object_to_move, speed, time_seconds):
    pixels_to_move = speed * time_seconds
    object_to_move.x = object_to_move.x + pixels_to_move
    object_to_move.rect.x = object_to_move.x


def move_y(object_to_move, speed, time_seconds):
    pixels_to_move = speed * time_seconds
    object_to_move.y = object_to_move.y + pixels_to_move
    object_to_move.rect.y = object_to_move.y


def should_have_star():
    return choice([0, 0, 0, 0, 0, 0, 1])


def random_star_for_x(x, height):
    radius = randint(0, 2)
    y = randint(0, height)
    red = randint(230, 255)
    blue = randint(100, 255)
    green = randint(min(255, blue + 50), 255)

    color = (red, green, blue)
    speed = randint(10, 100)
    star = Star(x, y, radius, color, speed)
    return star


def update_player_input(player_input):
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            player_input.stop = True

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_a:
                player_input.left = True
            if e.key == pygame.K_d:
                player_input.right = True
            if e.key == pygame.K_s:
                player_input.down = True
            if e.key == pygame.K_w:
                player_input.up = True
            if e.key == pygame.K_RETURN:
                player_input.fire = True

        elif e.type == pygame.KEYUP:
            if e.key == pygame.K_a:
                player_input.left = False
            if e.key == pygame.K_d:
                player_input.right = False
            if e.key == pygame.K_s:
                player_input.down = False
            if e.key == pygame.K_w:
                player_input.up = False
            if e.key == pygame.K_RETURN:
                player_input.fire = False


def update_game_state(game_state, player_input, graphics, time_seconds):
    if game_state.mode == "playing":
        update_game_state_playing(game_state, player_input, graphics, time_seconds)
    if game_state.mode == "waiting":
        update_game_state_waiting(game_state, player_input, graphics)
    if game_state.mode == "gameover":
        update_game_state_gameover(game_state)


def update_game_state_waiting(game_state, player_input, graphics):
    if player_input.fire:
        game_state.mode = "playing"
        game_state.has_shot = True


def update_game_state_gameover(game_state):
    if time.time() - game_state.gameover_time > 2:
        game_state.mode = "restart"


def update_game_state_playing(game_state, player_input, graphics, time_seconds):
    height = game_state.game_area.height
    if not game_state.player.alive and game_state.lives > 0 and time.time() - game_state.time_of_death > 1:
        game_state.alien_shots = []
        game_state.aliens = make_wave(graphics, game_state.game_area, game_state.wave_number)
        game_state.player.rect.midleft = (0, height // 2)
        game_state.player.x = game_state.player.rect.x
        game_state.player.y = game_state.player.rect.y
        game_state.player.alive = True
        game_state.lives = game_state.lives - 1

    if len(game_state.aliens) == 0:
        game_state.wave_number = game_state.wave_number + 1
        game_state.aliens = make_wave(graphics, game_state.game_area, game_state.wave_number)

    if not game_state.player.alive and game_state.lives == 0:
        game_state.mode = "gameover"
        game_state.gameover_time = time.time()

    player = game_state.player
    if player_input.down and player.rect.bottom < game_state.game_area.bottom:
        player.rect.y = player.rect.y + player.speed_pixels_per_draw
    if player_input.up and player.rect.top > game_state.game_area.top:
        player.rect.y = player.rect.y - player.speed_pixels_per_draw
    if player_input.right and player.rect.right < game_state.game_area.right:
        player.rect.x = player.rect.x + player.speed_pixels_per_draw
    if player_input.left and player.rect.left > game_state.game_area.left:
        player.rect.x = player.rect.x - player.speed_pixels_per_draw

    may_fire = not game_state.has_shot and game_state.player.alive
    if player_input.fire and may_fire:
        shot_coord = game_state.player.rect.midright
        new_shot = PlayerShot(graphics.player_shot.get_rect(center=shot_coord))
        game_state.player_shots.append(new_shot)
        game_state.has_shot = True
    elif not player_input.fire:
        game_state.has_shot = False

    for star in game_state.stars:
        move_x(star, -star.speed, time_seconds)

    for shot in game_state.player_shots:
        shot.rect.x = shot.rect.x + shot.speed_pixels_per_draw
    reap_outsiders(game_state.player_shots, game_state.game_area)

    for shot in game_state.alien_shots:
        move_x(shot, shot.speed_x, time_seconds)
        move_y(shot, shot.speed_y, time_seconds)
    reap_outsiders(game_state.alien_shots, game_state.game_area)

    if should_have_star():
        star = random_star_for_x(game_state.game_area.width,
                                 game_state.game_area.height)
        game_state.stars.append(star)
    reap_outsiders(game_state.stars, game_state.game_area)

    for alien in game_state.aliens:
        if alien.rect.left <= alien.movement_area.left:
            alien.moving_left = False

        if alien.rect.right >= alien.movement_area.right and not alien.moving_left:
            alien.moving_left = True

        if alien.moving_left:
            alien.rect.x = alien.rect.x - alien.speed
        else:
            alien.rect.x = alien.rect.x + alien.speed

        if randint(1, 10000) > 9990:
            add_alien_shot(game_state, graphics, alien)

    for shot in list(game_state.player_shots):
        for alien in list(game_state.aliens):
            if shot.rect.colliderect(alien.rect):
                if shot in game_state.player_shots:
                    game_state.player_shots.remove(shot)
                if alien in game_state.aliens:
                    game_state.aliens.remove(alien)
                explosion_center = alien.rect.center
                new_explosion = Explosion(explosion_center, 60, (255, 200, 0))
                game_state.explosions.append(new_explosion)

    for shot in list(game_state.alien_shots):
        if shot.rect.colliderect(game_state.player.rect):
            game_state.player.alive = False
            game_state.time_of_death = time.time()
            explosion_center = game_state.player.rect.center
            new_explosion = Explosion(explosion_center, 200, (255, 50, 0))
            game_state.explosions.append(new_explosion)

    for explosion in list(game_state.explosions):
        if explosion.growing:
            explosion.current_radius = explosion.current_radius + explosion.grow_speed
            if explosion.current_radius >= explosion.max_radius:
                explosion.growing = False
        else:
            explosion.current_radius = explosion.current_radius - explosion.shrink_speed
            if explosion.current_radius <= 0:
                game_state.explosions.remove(explosion)


def paint_screen(window, game_state, graphics):
    window.fill((0,0,0))
    if game_state.mode == "playing":
        paint_screen_playing(window, game_state, graphics)
    if game_state.mode == "waiting":
        paint_screen_waiting(window, graphics)
    if game_state.mode == "gameover":
        paint_screen_gameover(window, graphics)
    pygame.display.flip()


def paint_screen_playing(window, game_state, graphics):
    game_area = game_state.game_area
    status_line_height = window.get_rect().height - game_area.height
    game_surface = window.subsurface(game_area.move(0, status_line_height))
    for star in game_state.stars:
        pygame.draw.circle(game_surface, star.color,
                           (star.rect.x, star.rect.y),
                           star.radius)

    if game_state.player.alive:
        game_surface.blit(graphics.player, game_state.player.rect)

    for shot in game_state.player_shots:
        game_surface.blit(graphics.player_shot, shot.rect)

    for alien in game_state.aliens:
        game_surface.blit(graphics.alien, alien.rect)

    for shot in game_state.alien_shots:
        game_surface.blit(graphics.alien_shot, shot.rect)

    for explosion in game_state.explosions:
        pygame.draw.circle(game_surface, explosion.color, (explosion.x, explosion.y), explosion.current_radius)

    lives_text = "Lives: " + str(game_state.lives)
    text_image = graphics.status_font.render(lives_text, True, (150, 150, 150))
    screen_rect = window.get_rect()
    text_rect = text_image.get_rect(topright=screen_rect.topright).move(0, 8)
    window.blit(text_image, text_rect)


def paint_screen_waiting(window, graphics):
    text_image = graphics.status_font.render("Press fire to play", True, (255, 0, 0))
    window_rect = window.get_rect()
    text_rect = text_image.get_rect(center=window_rect.center)
    window.blit(text_image, text_rect)


def paint_screen_gameover(window, graphics):
    text_image = graphics.status_font.render("Game Over", True, (255, 0, 0))
    window_rect = window.get_rect()
    text_rect = text_image.get_rect(center=window_rect.center)
    window.blit(text_image, text_rect)


def add_alien_shot(game_state, graphics, shooting_alien):
    center = shooting_alien.rect.center
    rect = graphics.alien_shot.get_rect(center=center)
    if shooting_alien.rect.left < game_state.player.rect.right:
        direction_x = 1
    else:
        direction_x = -1
    if shooting_alien.rect.top < game_state.player.rect.bottom:
        direction_y = 1
    else:
        direction_y = -1

    shot = AlienShot(rect, direction_x * 500, uniform(-100 + 80 * direction_y,
                                                      100 + 80 * direction_y))
    game_state.alien_shots.append(shot)


def make_wave(graphics, game_area, wave_number):
    def make_alien(x, y, extra_speed):
        width = game_area.width
        height = game_area.height
        alien_rect = graphics.alien.get_rect(center=(width + x, height // 2 + y))
        alien = Alien(alien_rect, game_area, extra_speed)
        return alien

    extra_speed = wave_number // 3

    if wave_number % 3 == 0:
        return [make_alien(10, 0, extra_speed),
                make_alien(100, 0, extra_speed),
                make_alien(200, 0, extra_speed),
                make_alien(300, 0, extra_speed),
                make_alien(400, 0, extra_speed)]

    elif wave_number % 3 == 1:
        return [make_alien(10, 0, extra_speed),
                make_alien(100, 50, extra_speed),
                make_alien(100, -50, extra_speed),
                make_alien(200, 100, extra_speed),
                make_alien(200, -100, extra_speed)]
    else:
        return [make_alien(10, 0, extra_speed),
                make_alien(100, -50, extra_speed),
                make_alien(100, 0, extra_speed),
                make_alien(100, 50, extra_speed),
                make_alien(200, -100, extra_speed),
                make_alien(200, -50, extra_speed),
                make_alien(200, 0, extra_speed),
                make_alien(200, 50, extra_speed),
                make_alien(200, 100, extra_speed)]


def main_loop():
    pygame.init()
    screen_width = 800
    screen_height = 600
    window = pygame.display.set_mode((screen_width, screen_height))
    game_area = pygame.Rect((0, 0), (screen_width, screen_height - 40))

    graphics = Graphics()
    game_state = GameState(graphics, game_area)
    player_input = PlayerInput()

    previous_seconds = time.time()
    while not player_input.stop:
        if game_state.mode == "restart":
            game_state = GameState(game_state.graphics, game_state.game_area)

        current_seconds = time.time()
        elapsed_seconds = current_seconds - previous_seconds
        previous_seconds = current_seconds
        delay_seconds = max(0.0, 1.0 / FRAMES_PER_SECOND - elapsed_seconds)
        pygame.time.delay(int(delay_seconds * 1000))
        update_player_input(player_input)
        update_game_state(game_state, player_input, graphics, elapsed_seconds)
        paint_screen(window, game_state, graphics)
    pygame.quit()


main_loop()
