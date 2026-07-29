# core/particles_engine.py
# Small solid cyan orbs - no blur

import io
import math
import random
import pygame


class SoftOrb:
    def __init__(self, width, height):
        self.x = random.uniform(0, max(1, width))
        self.y = random.uniform(-height, 0)
        self.radius = random.uniform(2.5, 5.5)   # small size
        self.speed = random.uniform(0.4, 1.2)
        self.drift = random.uniform(-0.2, 0.2)
        self.phase = random.uniform(0, math.pi * 2)
        self.wobble = random.uniform(0.003, 0.01)
        self.color = (0, random.randint(200, 255), random.randint(220, 255))

    def update(self, width, height):
        self.phase += self.wobble
        self.y += self.speed
        self.x += self.drift + math.sin(self.phase) * 0.25

        if self.y - self.radius > height:
            self.y = -self.radius * 2
            self.x = random.uniform(0, max(1, width))
            self.speed = random.uniform(0.4, 1.2)
            self.radius = random.uniform(2.5, 5.5)

        if self.x < -10:
            self.x = width + 10
        elif self.x > width + 10:
            self.x = -10

    def draw(self, surface):
        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            max(1, int(self.radius)),
        )


class PygameEngine:
    def __init__(self, width=720, height=520):
        pygame.init()
        self.width = max(100, int(width))
        self.height = max(100, int(height))
        self.surface = pygame.Surface((self.width, self.height))
        self.orbs = [SoftOrb(self.width, self.height) for _ in range(22)]

    def resize(self, width, height):
        if width and height and width > 0 and height > 0:
            self.width = int(width)
            self.height = int(height)
            self.surface = pygame.Surface((self.width, self.height))

    def render_frame_bytes(self):
        self.surface.fill((8, 10, 14))

        for orb in self.orbs:
            orb.update(self.width, self.height)
            orb.draw(self.surface)

        buffer = io.BytesIO()
        pygame.image.save(self.surface, buffer, "PNG")
        return buffer.getvalue()