import random
import pygame


class Particle:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        # سرعة وانبثاق عشوائي في جميع الاتجاهات عند حركة الماوس
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-2.5, 2.5)
        self.size = random.randint(4, 7)
        self.color = [0, 220, 255]  # لون cyan
        self.lifetime = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.size -= 0.15  # تصغير الحجم تدريجياً
        self.lifetime -= 8  # تلاشي السطوع بسرعة

    def draw(self, surface):
        if self.lifetime > 0 and self.size > 0:
            pygame.draw.circle(
                surface, self.color, (int(self.x), int(self.y)), int(self.size)
            )


# تهيئة Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mouse Motion Particles")
clock = pygame.time.Clock()

particles = []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # توليد الجزيئات فقط عند تحريك الماوس!
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            # كلما تحرك الماوس يتم إنشاء مجموعة جزيئات عند موقعه
            for _ in range(4):
                particles.append(Particle(mouse_x, mouse_y))

    # تحديث الجزيئات وحذف الميتة منها
    for particle in particles[:]:
        particle.update()
        if particle.lifetime <= 0 or particle.size <= 0:
            particles.remove(particle)

    # الرسم
    screen.fill((10, 10, 10))

    for particle in particles:
        particle.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()