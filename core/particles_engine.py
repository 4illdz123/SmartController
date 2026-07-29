# core/particles_engine.py

import io
import random
import pygame


class Particle:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-1.5, 1.5)
        self.size = random.uniform(3, 6)
        self.life = random.randint(30, 80)
        self.max_life = self.life
        self.color = (
            0,
            random.randint(180, 255),
            random.randint(220, 255),
        )  # ألوان Cyan مضيئة

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.size = max(0, self.size - 0.05)
        self.life -= 1

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            pygame.draw.circle(
                surface, self.color, (int(self.x), int(self.y)), int(self.size)
            )


class PygameEngine:

    def __init__(self, width=980, height=760):
        pygame.init()
        self.width = int(width) if width and width > 0 else 980
        self.height = int(height) if height and height > 0 else 760
        self.surface = pygame.Surface((self.width, self.height))
        self.particles = []

    def resize(self, width, height):
        if width and height and width > 0 and height > 0:
            self.width = int(width)
            self.height = int(height)
            self.surface = pygame.Surface((self.width, self.height))

    def add_particles(self, x, y):
        for _ in range(3):
            self.particles.append(Particle(x, y))

    def render_frame_bytes(self):
        self.surface.fill((10, 10, 10))  # خلفية داكنة

        # توليد جسيمات عشوائية مستمرة خلف الواجهة
        if random.random() < 0.4:
            rx = random.randint(0, self.width)
            ry = random.randint(0, self.height)
            self.particles.append(Particle(rx, ry))

        # تحديث ورسم الجسيمات
        for p in self.particles[:]:
            p.update()
            p.draw(self.surface)
            if p.life <= 0 or p.size <= 0:
                self.particles.remove(p)

        buffer = io.BytesIO()
        pygame.image.save(self.surface, buffer, "PNG")
        return buffer.getvalue()