import arcade, math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Что-нибудь вроде прототипа накодили"

SPEED = 100
ROTATING_SPEED = 90
PROJECTILE_SPEED = 100


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


class Projectile(arcade.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        angle = angle
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


class GameNameOrSmth(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background = arcade.load_texture("background.png")

    def setup(self):
        self.players_list = arcade.SpriteList()
        self.player = Player()
        self.players_list.append(self.player)
        self.projectiles_list = arcade.SpriteList()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background,
                                 arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH,SCREEN_HEIGHT))
        self.players_list.draw()
        self.projectiles_list.draw()

    def on_update(self, delta_time):
        self.players_list.update(delta_time)
        self.projectiles_list.update(delta_time)

    def on_key_press(self, key, modifiers):
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
            projectile = Projectile(self.player.center_x, self.player.center_y, 450 - self.player.angle)
            self.projectiles_list.append(projectile)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.S:
            self.player.change_y = 0
        elif key == arcade.key.A or key == arcade.key.D:
            self.player.change_x = 0
        elif key == arcade.key.Q or key == arcade.key.E:
            self.player.change_angle = 0

    def on_mouse_press(self, x, y, button, modifiers):
        if arcade.MOUSE_BUTTON_LEFT == button:
            projectile = Projectile(self.player.center_x, self.player.center_y,
                                    360 - arcade.math.get_angle_degrees(self.player.center_x, self.player.center_y, x,
                                                                        y))
            self.projectiles_list.append(projectile)


def setup_game(width=800, height=600, title="GameNameOrSmth"):
    game = GameNameOrSmth(width, height, title)
    game.setup()
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()