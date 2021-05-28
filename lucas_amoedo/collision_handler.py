from constants import (
    BULLET_COLLISION_TYPE,
    NINJA_COLLISION_TYPE,
    PLAYER_COLLISION_TYPE,
    PLATFORM_COLLISION_TYPE
)


class CollisionHandler:
    def __init__(self, space):
        self.space = space

    def add_handlers_to_space(self):

        def handle_bullet_ninja_collision(arbiter, space, data):
            bullet_shape, ninja_shape = arbiter.shapes
            ninja = ninja_shape.body.reference
            ninja.hit_points -= 1

            bullet = bullet_shape.body.reference
            bullet.tick = 30

            return True

        def handle_player_ninja_collision(arbiter, space, data):
            _, player_shape = arbiter.shapes
            player = player_shape.body.reference

            if not player.blinking:
                player.hit_points -= 1
                player.blink()

            return True

        def handle_bullet_platform_col(arbiter, space, data):
            bullet_shape, _ = arbiter.shapes
            bullet_shape.body.reference.tick = 30
            return True

        def handle_player_bullet_collision(arbiter, space, data):
            return False

        bullet_ninja_collision_handler = self.space.add_collision_handler(
            BULLET_COLLISION_TYPE,
            NINJA_COLLISION_TYPE
        )

        bullet_ninja_collision_handler.begin = handle_bullet_ninja_collision

        player_ninja_collision_handler = self.space.add_collision_handler(
            NINJA_COLLISION_TYPE,
            PLAYER_COLLISION_TYPE
        )

        player_ninja_collision_handler.begin = handle_player_ninja_collision

        bullet_platform_collision_handler = self.space.add_collision_handler(
            BULLET_COLLISION_TYPE,
            PLATFORM_COLLISION_TYPE
        )

        bullet_platform_collision_handler.begin = handle_bullet_platform_col

        player_bullet_collision_handler = self.space.add_collision_handler(
            PLAYER_COLLISION_TYPE,
            BULLET_COLLISION_TYPE
        )

        player_bullet_collision_handler.begin = handle_player_bullet_collision
