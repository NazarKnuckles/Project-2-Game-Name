import arcade
import math
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Что-нибудь вроде прототипа накодили"

SPEED = 200
ROTATING_SPEED = 180
PROJECTILE_SPEED = 150
ENEMY_SPEED = 80
ENEMY_PROJECTILE_SPEED = 100
ENEMY_SHOOT_COOLDOWN = 3
CHARGER_SHOTS_COUNT = 3
SHOT_SPREAD_COOLDOWN = 1.3

WAVE_TIME = 5

BASE_ENEMY_SCORE = 10
PLAYER_MAX_HEALTH = 3

CHARGER_CHANCE = 0.25
INITIAL_ENEMY_COUNT = 5
MAX_ENEMY_COUNT = 20
ENEMY_COUNT_INCREMENT = 1
INCREMENT_WAVE_INTERVAL = 3

MAX_SPEED_BOOST = 2.0
SPEED_BOOST_PER_WAVE = 0.05

SCORE_INCREMENT_PER_3_WAVES = 10
HEALTH_RESTORE_WAVE_INTERVAL = 5

# NEW: Constants for added features
HEALTH_DROP_CHANCE = 0.1  # 10% chance to drop a health power-up
SPREAD_ANGLE = 15  # degrees between projectiles in spread shot
SPREAD_COUNT = 3  # number of projectiles per shot


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.texture = arcade.load_texture("character.png")
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.angle = 0
        self.change_x = 0
        self.change_y = 0
        self.change_angle = 0
        self.health = PLAYER_MAX_HEALTH

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        if self.center_x > SCREEN_WIDTH:
            self.center_x = SCREEN_WIDTH
        elif self.center_x < 0:
            self.center_x = 0
        if self.center_y > SCREEN_HEIGHT:
            self.center_y = SCREEN_HEIGHT
        elif self.center_y < 0:
            self.center_y = 0
        self.angle += self.change_angle * delta_time


class ScorePopup:
    """отдельный ласс для всплывающих очков при убийстве врага"""

    def __init__(self, x, y, score):
        self.x = x
        self.y = y
        self.score = score
        self.lifetime = 1.0
        self.timer = 0

    def update(self, delta_time):
        self.timer += delta_time
        self.y += 50 * delta_time
        return self.timer < self.lifetime

    def draw(self):
        alpha = int(255 * (1 - self.timer / self.lifetime))
        arcade.draw_text(f"+{self.score}", self.x, self.y,
                         (255, 215, 0, alpha), 16,
                         font_name="Kenney Pixel", anchor_x="center")


class DamagePopup:
    """Класс для всплывающего текста при получении урона"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 0.8
        self.timer = 0

    def update(self, delta_time):
        self.timer += delta_time
        self.y += 30 * delta_time
        return self.timer < self.lifetime

    def draw(self):
        alpha = int(255 * (1 - self.timer / self.lifetime))
        arcade.draw_text(f"-1", self.x, self.y,
                         (255, 0, 0, alpha), 16,
                         font_name="Kenney Pixel", anchor_x="center")


class HealthRestorePopup:
    """Класс для всплывающего текста при восстановлении здоровья"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 1.2
        self.timer = 0

    def update(self, delta_time):
        self.timer += delta_time
        self.y += 40 * delta_time
        return self.timer < self.lifetime

    def draw(self):
        alpha = int(255 * (1 - self.timer / self.lifetime))
        arcade.draw_text(f"❤️ ЗДОРОВЬЕ ВОССТАНОВЛЕНО ❤️", self.x, self.y,
                         (0, 255, 0, alpha), 18,
                         font_name="Kenney Pixel", anchor_x="center")


class Projectile(arcade.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.texture = arcade.load_texture("projectile.png")
        self.angle = 450 - angle
        angle_rad = math.radians(angle)
        self.center_x = x + 10 * math.cos(angle_rad)
        self.center_y = y + 10 * math.sin(angle_rad)
        self.change_x = math.cos(angle_rad) * PROJECTILE_SPEED
        self.change_y = math.sin(angle_rad) * PROJECTILE_SPEED

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        if self.center_x > SCREEN_WIDTH or self.center_x < 0 or self.center_y > SCREEN_HEIGHT or self.center_y < 0:
            self.remove_from_sprite_lists()
            del self


class EnemyProjectile(arcade.Sprite):
    """Снаряд врага"""

    def __init__(self, x, y, target_x, target_y, speed_boost):
        super().__init__()
        self.texture = arcade.load_texture("enemyprojectile.png")
        self.scale = 1
        angle_rad = math.atan2(target_y - y, target_x - x)
        angle_deg = math.degrees(angle_rad)
        self.angle = 450 - angle_deg
        self.center_x = x
        self.center_y = y
        current_speed = ENEMY_PROJECTILE_SPEED * speed_boost
        self.change_x = math.cos(angle_rad) * current_speed
        self.change_y = math.sin(angle_rad) * current_speed

    def update(self, delta_time):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        if self.center_x > SCREEN_WIDTH + 50 or self.center_x < -50 or self.center_y > SCREEN_HEIGHT + 50 or self.center_y < -50:
            self.remove_from_sprite_lists()
            del self


class Enemy(arcade.Sprite):
    def __init__(self, speed_boost):
        super().__init__()
        self.texture = arcade.load_texture("enemy.png")
        self.scale = 1
        self.center_x = random.randint(50, SCREEN_WIDTH - 50)
        self.center_y = random.randint(50, SCREEN_HEIGHT - 50)
        self.angle = 0
        current_speed = ENEMY_SPEED * speed_boost
        self.change_x = math.cos(math.radians(self.angle)) * current_speed
        self.change_y = math.sin(math.radians(self.angle)) * current_speed
        self.shoot_timer = random.uniform(0, ENEMY_SHOOT_COOLDOWN / speed_boost)

    def update(self, delta_time, player_x, player_y, speed_boost):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        if self.center_x > SCREEN_WIDTH - 30:
            self.center_x = SCREEN_WIDTH - 30
            self.change_x *= -1
        elif self.center_x < 30:
            self.center_x = 30
            self.change_x *= -1
        if self.center_y > SCREEN_HEIGHT - 30:
            self.center_y = SCREEN_HEIGHT - 30
            self.change_y *= -1
        elif self.center_y < 30:
            self.center_y = 30
            self.change_y *= -1
        self.shoot_timer += delta_time


# NEW: Health power-up class
class HealthPowerUp(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Use a heart image if available; otherwise, fallback to a red circle
        try:
            self.texture = arcade.load_texture("health_powerup.png")
        except:
            self.texture = arcade.make_circle_texture(20, arcade.color.RED)
        self.scale = 0.5
        self.center_x = x
        self.center_y = y
        self.change_y = -30  # slowly fall down

    def update(self, delta_time):
        self.center_y += self.change_y * delta_time
        # Remove if off screen
        if self.top < 0:
            self.remove_from_sprite_lists()


# NEW: Charger enemy – moves directly toward player
class ChargerEnemy(Enemy):
    def __init__(self, speed_boost):
        super().__init__(speed_boost)
        # Use a different texture if available
        self.texture = arcade.load_texture("charger_enemy.png")
        # Increase base speed
        self.speed = ENEMY_SPEED * 1.5 * speed_boost

    def update(self, delta_time, player_x, player_y, speed_boost):
        # Calculate direction to player
        dx = player_x - self.center_x
        dy = player_y - self.center_y
        distance = math.hypot(dx, dy)
        if distance > 0:
            # Normalize and set velocity
            self.change_x = (dx / distance) * self.speed
            self.change_y = (dy / distance) * self.speed

        # Move
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        # Bounce off walls
        if self.center_x > SCREEN_WIDTH - 30:
            self.center_x = SCREEN_WIDTH - 30
            self.change_x *= -1
        elif self.center_x < 30:
            self.center_x = 30
            self.change_x *= -1
        if self.center_y > SCREEN_HEIGHT - 30:
            self.center_y = SCREEN_HEIGHT - 30
            self.change_y *= -1
        elif self.center_y < 30:
            self.center_y = 30
            self.change_y *= -1

        self.shoot_timer += delta_time
        self.texture = arcade.load_texture("charger_enemy.png")
        self.speed = ENEMY_SPEED * 1.5 * speed_boost
        self.angle = 0


    # NEW: Simple explosion effect
class Explosion(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.make_circle_texture(30, arcade.color.ORANGE_RED)
        self.center_x = x
        self.center_y = y
        self.scale = 0.5
        self.alpha = 255
        self.lifetime = 0.3
        self.timer = 0

    def update(self, delta_time):
        self.timer += delta_time
        if self.timer >= self.lifetime:
            self.remove_from_sprite_lists()
            return
        # Grow and fade
        self.scale = 0.5 + (self.timer / self.lifetime) * 1.5
        self.alpha = int(255 * (1 - self.timer / self.lifetime))


class GameNameOrSmth(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background = arcade.load_texture("background.png")
        self.game_over = False
        self.player_name = ""

    def setup(self):
        self.shot_cooldown = False
        self.players_list = arcade.SpriteList()
        self.player = Player()
        self.players_list.append(self.player)
        self.projectiles_list = arcade.SpriteList()
        self.enemy_projectiles_list = arcade.SpriteList()
        self.enemies_list = arcade.SpriteList()
        # NEW: power-ups and explosions lists
        self.powerups_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.score = 0
        self.current_wave = 1
        self.score_popups = []
        self.damage_popups = []
        self.health_restore_popups = []
        self.wave_timer = 0
        self.waiting_for_next_wave = False
        self.speed_boost = 1.0
        self.current_enemy_count = INITIAL_ENEMY_COUNT
        self.base_score = BASE_ENEMY_SCORE
        self.shot_spread_cooldown_timer = 0
        self.spawn_enemies()

        self.game_over = False
        self.player_name = ""

    def spawn_enemies(self):
        """Создает врагов для текущей волны, включая ChargerEnemy с вероятностью 30%"""
        for i in range(self.current_enemy_count):
            # NEW: 30% chance to spawn a charger enemy
            if random.random() < CHARGER_CHANCE:
                enemy = ChargerEnemy(self.speed_boost)
            else:
                enemy = Enemy(self.speed_boost)
            self.enemies_list.append(enemy)

    def update_wave_parameters(self):
        """Обновляет параметры для новой волны"""
        if self.current_wave % INCREMENT_WAVE_INTERVAL == 0 and self.current_enemy_count < MAX_ENEMY_COUNT:
            self.current_enemy_count = min(self.current_enemy_count + ENEMY_COUNT_INCREMENT, MAX_ENEMY_COUNT)
        self.speed_boost = min(1.0 + (self.current_wave + 2) * SPEED_BOOST_PER_WAVE, MAX_SPEED_BOOST)
        self.base_score = BASE_ENEMY_SCORE + (self.current_wave // 3) * SCORE_INCREMENT_PER_3_WAVES
        if self.current_wave % HEALTH_RESTORE_WAVE_INTERVAL == 0:
            old_health = self.player.health
            self.player.health = PLAYER_MAX_HEALTH
            if old_health < PLAYER_MAX_HEALTH:
                restore_popup = HealthRestorePopup(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                self.health_restore_popups.append(restore_popup)

    # NEW: spread shot method
    def fire_spread_shot(self, base_angle=None):
        """Fire spread shot. If base_angle is None, use player's angle."""
        if self.shot_cooldown == False:
            self.shot_cooldown = True
            if base_angle is None:
                base_angle = 450 - self.player.angle  # conversion used in original Projectile

            # For odd number of projectiles, center one goes straight
            start_angle = base_angle - (SPREAD_ANGLE * (SPREAD_COUNT - 1) / 2)
            for i in range(SPREAD_COUNT):
                angle = start_angle + i * SPREAD_ANGLE
                projectile = Projectile(self.player.center_x, self.player.center_y, angle)
                self.projectiles_list.append(projectile)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background,
                                 arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT))

        if not self.game_over:
            self.players_list.draw()
            self.projectiles_list.draw()
            self.enemy_projectiles_list.draw()
            self.enemies_list.draw()
            self.powerups_list.draw()
            self.explosions_list.draw()
            for popup in self.score_popups:
                popup.draw()
            for popup in self.damage_popups:
                popup.draw()
            for popup in self.health_restore_popups:
                popup.draw()
            # --- CHANGED: text color from BLACK to WHITE ---
            arcade.draw_text(f"Очки: {self.score}", 10, SCREEN_HEIGHT - 30,
                             arcade.color.WHITE, 20, font_name="Kenney Pixel")
            arcade.draw_text(f"Волна: {self.current_wave}", 10, SCREEN_HEIGHT - 60,
                             arcade.color.WHITE, 20, font_name="Kenney Pixel")
            health_text = f"❤️ " * self.player.health
            arcade.draw_text(health_text, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 45,
                             arcade.color.RED, 25, font_name="Kenney Pixel")
            # --- CHANGED: enemy count color from BLACK to WHITE ---
            arcade.draw_text(f"Врагов: {len(self.enemies_list)}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80,
                             arcade.color.WHITE, 16, font_name="Kenney Pixel")
            if self.waiting_for_next_wave:
                time_left = int(WAVE_TIME - (self.wave_timer)) + 1
                if time_left > 0:
                    arcade.draw_text(f"Следующая волна через: {time_left}",
                                     SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2,
                                     arcade.color.YELLOW, 30, font_name="Kenney Pixel",
                                     align="center")
        else:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
                             arcade.color.RED, 50, font_name="Kenney Pixel", anchor_x="center")
            # --- CHANGED: game-over score from BLACK to WHITE ---
            arcade.draw_text(f"Ваш счет: {self.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40,
                             arcade.color.WHITE, 30, font_name="Kenney Pixel", anchor_x="center")
            # --- CHANGED: prompt from BLACK to WHITE ---
            arcade.draw_text("Введите ваш ник:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
                             arcade.color.WHITE, 20, font_name="Kenney Pixel", anchor_x="center")
            arcade.draw_text(f"{self.player_name}_", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60,
                             arcade.color.LIGHT_BLUE, 25, font_name="Kenney Pixel", anchor_x="center")
            # --- CHANGED: instruction from GRAY to LIGHT_GRAY (still visible) ---
            arcade.draw_text("Нажмите ENTER для сохранения", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                             arcade.color.LIGHT_GRAY, 16, font_name="Kenney Pixel", anchor_x="center")

    def on_update(self, delta_time):
        if self.game_over:
            return

        self.players_list.update(delta_time)
        self.projectiles_list.update(delta_time)
        self.enemy_projectiles_list.update(delta_time)
        # NEW: update power-ups and explosions
        self.powerups_list.update(delta_time)
        self.explosions_list.update(delta_time)
        self.score_popups = [popup for popup in self.score_popups if popup.update(delta_time)]
        self.damage_popups = [popup for popup in self.damage_popups if popup.update(delta_time)]
        self.health_restore_popups = [popup for popup in self.health_restore_popups if popup.update(delta_time)]

        for enemy in self.enemies_list:
            enemy.update(delta_time, self.player.center_x, self.player.center_y, self.speed_boost)
            current_cooldown = ENEMY_SHOOT_COOLDOWN / self.speed_boost
            if enemy.shoot_timer >= current_cooldown and not self.waiting_for_next_wave and type(enemy) == Enemy:
                enemy_projectile = EnemyProjectile(enemy.center_x, enemy.center_y,
                                                   self.player.center_x, self.player.center_y,
                                                   self.speed_boost)
                self.enemy_projectiles_list.append(enemy_projectile)
                enemy.shoot_timer = 0
            elif enemy.shoot_timer >= current_cooldown and not self.waiting_for_next_wave and type(enemy) == ChargerEnemy:
                for i in range(-CHARGER_SHOTS_COUNT * 2, CHARGER_SHOTS_COUNT * 2):
                    enemy_projectile = EnemyProjectile(enemy.center_x, enemy.center_y,
                                                       enemy.center_x + i * random.randint(1, 10), enemy.center_y - i * random.randint(1, 10),
                                                       self.speed_boost)
                    self.enemy_projectiles_list.append(enemy_projectile)
                enemy.shoot_timer = 0

        if self.waiting_for_next_wave:
            self.wave_timer += delta_time
            if self.wave_timer >= WAVE_TIME:
                self.waiting_for_next_wave = False
                self.current_wave += 1
                self.update_wave_parameters()
                self.spawn_enemies()
        if self.shot_cooldown:
            self.shot_spread_cooldown_timer += delta_time
            if self.shot_spread_cooldown_timer >= SHOT_SPREAD_COOLDOWN:
                self.shot_spread_cooldown_timer = 0
                self.shot_cooldown = False

        # Enemy-enemy collision avoidance
        for i in range(len(self.enemies_list)):
            for j in range(i + 1, len(self.enemies_list)):
                enemy1 = self.enemies_list[i]
                enemy2 = self.enemies_list[j]
                distance = math.sqrt(
                    (enemy1.center_x - enemy2.center_x) ** 2 + (enemy1.center_y - enemy2.center_y) ** 2)
                if distance < 50:
                    if enemy1.center_x < enemy2.center_x:
                        enemy1.change_x -= 10
                        enemy2.change_x += 10
                    else:
                        enemy1.change_x += 10
                        enemy2.change_x -= 10
                    if enemy1.center_y < enemy2.center_y:
                        enemy1.change_y -= 10
                        enemy2.change_y += 10
                    else:
                        enemy1.change_y += 10
                        enemy2.change_y -= 10

        # Projectile vs enemy collisions
        for projectile in self.projectiles_list:
            hit_list = arcade.check_for_collision_with_list(projectile, self.enemies_list)
            if hit_list:
                projectile.remove_from_sprite_lists()
                for enemy in hit_list:
                    # NEW: create explosion
                    explosion = Explosion(enemy.center_x, enemy.center_y)
                    self.explosions_list.append(explosion)

                    # NEW: chance to drop health power-up
                    if random.random() < HEALTH_DROP_CHANCE:
                        powerup = HealthPowerUp(enemy.center_x, enemy.center_y)
                        self.powerups_list.append(powerup)

                    points_earned = self.base_score
                    self.score += points_earned
                    popup = ScorePopup(enemy.center_x, enemy.center_y, points_earned)
                    self.score_popups.append(popup)
                    enemy.remove_from_sprite_lists()

        # Enemy projectile vs player collisions
        for enemy_projectile in self.enemy_projectiles_list:
            hit_list = arcade.check_for_collision_with_list(enemy_projectile, self.players_list)
            if hit_list:
                enemy_projectile.remove_from_sprite_lists()
                self.player.health -= 1
                damage_popup = DamagePopup(self.player.center_x, self.player.center_y)
                self.damage_popups.append(damage_popup)
                if self.player.health <= 0:
                    self.game_over = True

        # NEW: Player vs power-up collisions
        powerup_hits = arcade.check_for_collision_with_list(self.player, self.powerups_list)
        for powerup in powerup_hits:
            if self.player.health < PLAYER_MAX_HEALTH:
                self.player.health += 1
            powerup.remove_from_sprite_lists()
            # Optional: add a little popup or sound

        if len(self.enemies_list) == 0 and not self.waiting_for_next_wave and not self.game_over:
            self.waiting_for_next_wave = True
            self.wave_timer = 0

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif key == arcade.key.ENTER:
                print(f"Сохранен рекорд: {self.player_name} - {self.score} очков")
                self.setup()
            elif key == arcade.key.SPACE:
                self.player_name += " "
            else:
                if len(self.player_name) < 15:
                    pass
            return

        if key == arcade.key.W:
            self.player.change_y = SPEED
        elif key == arcade.key.S:
            self.player.change_y = -SPEED
        elif key == arcade.key.A:
            self.player.change_x = -SPEED
        elif key == arcade.key.D:
            self.player.change_x = SPEED
        elif key == arcade.key.Q:
            self.player.change_angle = -ROTATING_SPEED
        elif key == arcade.key.E:
            self.player.change_angle = ROTATING_SPEED
        elif key == arcade.key.SPACE:
            if not self.waiting_for_next_wave:
                # NEW: replace single projectile with spread shot
                self.fire_spread_shot()

    def on_key_release(self, key, modifiers):
        if self.game_over:
            return

        if key == arcade.key.W or key == arcade.key.S:
            self.player.change_y = 0
        elif key == arcade.key.A or key == arcade.key.D:
            self.player.change_x = 0
        elif key == arcade.key.Q or key == arcade.key.E:
            self.player.change_angle = 0

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_over:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if not self.waiting_for_next_wave:
                # NEW: use spread shot toward mouse
                angle = 360 - arcade.math.get_angle_degrees(
                    self.player.center_x, self.player.center_y, x, y)
                self.fire_spread_shot(angle)

    def on_text(self, text):
        """Обработка текстового ввода для ника"""
        if self.game_over:
            if len(self.player_name) < 15:
                self.player_name += text


def setup_game(width=800, height=600, title="GameNameOrSmth"):
    game = GameNameOrSmth(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()