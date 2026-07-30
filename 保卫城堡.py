import pygame
import sys
import math
import os
import random

# 初始化
pygame.init()
pygame.mixer.init()

# 常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 32
MAP_WIDTH = SCREEN_WIDTH // GRID_SIZE
MAP_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (160, 82, 45)
DARK_GREEN = (0, 128, 0)
GOLD = (255, 215, 0)

# 游戏设置
FPS = 60
START_GOLD = 300
START_LIVES = 20
TURRET_PRICE = 100
TURRET_RANGE = 150
TURRET_COOLDOWN = 30
BULLET_SPEED = 8
WAVE_DELAY = 90
ENEMY_SPAWN_DELAY = 30
BUILD_COOLDOWN_SECONDS = 1.5   # 放置冷却时间（秒）

# 敌人类型
class EnemyType:
    NORMAL = 0
    ELITE = 1
    BOSS = 2

# ========== 十个不同关卡路径 ==========
level_paths = [
    [(x, 9) for x in range(MAP_WIDTH)],
    [(x, 6) for x in range(12)] + [(12, y) for y in range(6, 12)] + [(x, 11) for x in range(12, MAP_WIDTH)],
    [(x, 5) for x in range(8)] + [(8, y) for y in range(5, 9)] + [(x, 8) for x in range(8, 16)] +
    [(16, y) for y in range(8, 12)] + [(x, 11) for x in range(16, MAP_WIDTH)],
    [(x, 4) for x in range(5)] + [(5, y) for y in range(4, 9)] + [(x, 8) for x in range(5, 10)] +
    [(10, y) for y in range(8, 13)] + [(x, 12) for x in range(10, 20)] + [(20, y) for y in range(12, 16)] +
    [(x, 15) for x in range(20, MAP_WIDTH)],
    [(x, 10) for x in range(10)] + [(10, y) for y in range(10, MAP_HEIGHT-2)] + [(x, MAP_HEIGHT-3) for x in range(10, MAP_WIDTH)],
    [(x, 5) for x in range(8)] + [(8, y) for y in range(5, 10)] + [(x, 9) for x in range(8, 15)] +
    [(15, y) for y in range(9, 14)] + [(x, 13) for x in range(15, MAP_WIDTH)],
    [(x, 7) for x in range(12)] + [(12, y) for y in range(7, MAP_HEIGHT-4)] + [(x, MAP_HEIGHT-5) for x in range(12, MAP_WIDTH-8)] +
    [(MAP_WIDTH-8, y) for y in range(MAP_HEIGHT-5, 8, -1)] + [(x, 8) for x in range(MAP_WIDTH-8, -1, -1)] +
    [(0, y) for y in range(8, 11)] + [(x, 10) for x in range(0, MAP_WIDTH)],
    [(x, 3) for x in range(7)] + [(7, y) for y in range(3, 9)] + [(x, 8) for x in range(7, 14)] +
    [(14, y) for y in range(8, 13)] + [(x, 12) for x in range(14, 20)] +
    [(20, y) for y in range(12, MAP_HEIGHT-2)] + [(x, MAP_HEIGHT-3) for x in range(20, MAP_WIDTH)],
    [(x, 4) for x in range(5)] + [(5, y) for y in range(4, 8)] + [(x, 7) for x in range(5, 10)] +
    [(10, y) for y in range(7, 11)] + [(x, 10) for x in range(10, 16)] +
    [(16, y) for y in range(10, 14)] + [(x, 13) for x in range(16, MAP_WIDTH)],
    [(x, 2) for x in range(5)] + [(5, y) for y in range(2, 8)] + [(x, 7) for x in range(5, 12)] +
    [(12, y) for y in range(7, 13)] + [(x, 12) for x in range(12, 18)] +
    [(18, y) for y in range(12, MAP_HEIGHT-3)] + [(x, MAP_HEIGHT-4) for x in range(18, MAP_WIDTH)]
]

# 清理路径
for i, path in enumerate(level_paths):
    clean = []
    for p in path:
        if not clean or p != clean[-1]:
            clean.append(p)
    level_paths[i] = clean

# ========== 辅助函数 ==========
def world_to_grid(pos):
    return (int(pos[0] // GRID_SIZE), int(pos[1] // GRID_SIZE))

def grid_to_world(grid_pos):
    return (grid_pos[0] * GRID_SIZE + GRID_SIZE//2, grid_pos[1] * GRID_SIZE + GRID_SIZE//2)

def is_path_tile(grid_pos, path_points):
    return grid_pos in path_points

def is_tower_allowed(grid_pos, path_points):
    return not is_path_tile(grid_pos, path_points)

def get_chinese_font(size):
    font_names = ['SimHei', 'Microsoft YaHei', 'SimSun', 'FangSong', 'KaiTi',
                  'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'Noto Sans CJK TC']
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, size)
            test_surf = font.render('测', True, WHITE)
            if test_surf.get_width() > 0:
                return font
        except:
            continue
    font_paths = []
    if os.name == 'nt':
        font_paths = ['C:/Windows/Fonts/simhei.ttf', 'C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simsun.ttc']
    else:
        font_paths = ['/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
                      '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc']
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = pygame.font.Font(path, size)
                return font
            except:
                continue
    print("未找到中文字体，使用默认字体")
    return pygame.font.Font(None, size)

# ========== 敌人 ==========
class Enemy(pygame.sprite.Sprite):
    def __init__(self, path_world, enemy_type=EnemyType.NORMAL, start_index=0):
        super().__init__()
        self.path = path_world
        self.current_point_index = start_index
        if self.current_point_index < len(self.path):
            self.pos = list(self.path[self.current_point_index])
        else:
            self.pos = [0, 0]

        self.enemy_type = enemy_type
        if enemy_type == EnemyType.NORMAL:
            self.max_health = 30
            self.speed = 2
            self.value = 50
            self.color = RED
            self.size = 18
        elif enemy_type == EnemyType.ELITE:
            self.max_health = 80
            self.speed = 1.5
            self.value = 120
            self.color = PURPLE
            self.size = 22
        else:
            self.max_health = 200
            self.speed = 1.0
            self.value = 500
            self.color = ORANGE
            self.size = 30

        self.health = self.max_health
        self.alive = True
        self.hit_flash = 0
        self.death_animation = False
        self.death_counter = 0
        self.reward_given = False
        self.direction = (0, 0)
        self.update_direction()

    def update_direction(self):
        if self.current_point_index < len(self.path) - 1:
            target = self.path[self.current_point_index + 1]
            dx = target[0] - self.pos[0]
            dy = target[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                self.direction = (dx/dist, dy/dist)
            else:
                self.direction = (0, 0)
        else:
            self.direction = (0, 0)

    def update(self):
        if self.death_animation:
            self.death_counter += 1
            if self.death_counter > 15:
                self.kill()
            return

        if self.hit_flash > 0:
            self.hit_flash -= 1

        if self.current_point_index >= len(self.path) - 1:
            self.alive = False
            return

        target = self.path[self.current_point_index + 1]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.pos = [target[0], target[1]]
            self.current_point_index += 1
            self.update_direction()
        else:
            self.pos[0] += self.direction[0] * self.speed
            self.pos[1] += self.direction[1] * self.speed

    def draw(self, surface):
        if self.death_animation:
            radius = self.size * (1 - self.death_counter/15)
            pygame.draw.circle(surface, ORANGE, (int(self.pos[0]), int(self.pos[1])), int(radius))
            return

        color = self.color
        if self.hit_flash > 0:
            color = WHITE
        pygame.draw.circle(surface, color, (int(self.pos[0]), int(self.pos[1])), self.size)
        bar_len = self.size * 2
        percent = self.health / self.max_health
        pygame.draw.rect(surface, RED, (self.pos[0]-bar_len//2, self.pos[1]-self.size-5, bar_len, 4))
        pygame.draw.rect(surface, GREEN, (self.pos[0]-bar_len//2, self.pos[1]-self.size-5, bar_len * percent, 4))

        if self.enemy_type == EnemyType.ELITE:
            pygame.draw.circle(surface, YELLOW, (int(self.pos[0]), int(self.pos[1])), self.size, 2)
        elif self.enemy_type == EnemyType.BOSS:
            pygame.draw.circle(surface, YELLOW, (int(self.pos[0]), int(self.pos[1])), self.size+2, 3)

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 5
        if self.health <= 0:
            self.die()

    def die(self):
        self.alive = False
        self.death_animation = True

# ========== 炮塔（支持等级外观） ==========
class Turret(pygame.sprite.Sprite):
    def __init__(self, grid_pos):
        super().__init__()
        self.grid_pos = grid_pos
        self.world_pos = grid_to_world(grid_pos)
        self.range = TURRET_RANGE
        self.cooldown = 0
        self.price = TURRET_PRICE
        self.level = 1
        self.damage = 10
        # 等级外观参数
        self.colors = [BLUE, GREEN, GOLD]       # Lv1蓝, Lv2绿, Lv3金
        self.sizes = [GRID_SIZE//2, GRID_SIZE//2+2, GRID_SIZE//2+4]
        self.angle = 0

    def update(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1

        closest = None
        min_dist = self.range
        for e in enemies:
            if not e.alive or e.death_animation:
                continue
            dx = e.pos[0] - self.world_pos[0]
            dy = e.pos[1] - self.world_pos[1]
            dist = math.hypot(dx, dy)
            if dist < min_dist:
                min_dist = dist
                closest = e
                self.angle = math.degrees(math.atan2(dy, dx))

        if closest and self.cooldown == 0:
            self.cooldown = TURRET_COOLDOWN
            return Bullet(self.world_pos, closest, self.damage)
        return None

    def draw(self, surface):
        # 根据等级选择外观
        idx = min(self.level-1, 2)
        color = self.colors[idx]
        size = self.sizes[idx]
        # 底座
        pygame.draw.circle(surface, DARK_GRAY, (int(self.world_pos[0]), int(self.world_pos[1])), size)
        # 主体
        pygame.draw.circle(surface, color, (int(self.world_pos[0]), int(self.world_pos[1])), size-2)
        # 炮口线条（随等级变粗）
        line_width = 3 + (self.level-1)*2
        end_x = self.world_pos[0] + math.cos(math.radians(self.angle)) * size
        end_y = self.world_pos[1] + math.sin(math.radians(self.angle)) * size
        pygame.draw.line(surface, YELLOW, self.world_pos, (end_x, end_y), line_width)
        # 范围指示器
        pygame.draw.circle(surface, CYAN, (int(self.world_pos[0]), int(self.world_pos[1])), self.range, 1)

    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.damage += 5
            self.range += 20
            return True
        return False

# ========== 子弹 ==========
class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, damage):
        super().__init__()
        self.pos = list(start_pos)
        self.target = target
        self.speed = BULLET_SPEED
        self.damage = damage
        self.active = True
        self.size = 4
        self.color = YELLOW

    def update(self):
        if not self.target or not self.target.alive or self.target.death_animation:
            self.active = False
            return
        dx = self.target.pos[0] - self.pos[0]
        dy = self.target.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.target.take_damage(self.damage)
            self.active = False
        else:
            if dist != 0:
                dir_vec = (dx/dist, dy/dist)
                self.pos[0] += dir_vec[0] * self.speed
                self.pos[1] += dir_vec[1] * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.size)

# ========== 游戏主类 ==========
class TowerDefenseGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("塔防 - 十关挑战")
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(20)
        self.big_font = get_chinese_font(40)

        self.gold = START_GOLD
        self.lives = START_LIVES
        self.score = 0
        self.level = 1
        self.current_wave = 1
        self.game_over = False
        self.game_win = False

        # 放置冷却（单位：帧）
        self.build_cooldown = 0

        # 当前路径
        self.current_path_points = level_paths[self.level-1]
        self.current_path_world = [grid_to_world(p) for p in self.current_path_points]

        # 精灵组
        self.all_enemies = pygame.sprite.Group()
        self.all_turrets = []
        self.all_bullets = []

        # 波次控制
        self.wave_in_progress = False
        self.wave_timer = 0
        self.enemy_spawn_timer = 0
        self.enemies_to_spawn = []
        self.enemies_spawned = 0

        # UI
        self.selected_turret = None
        self.mouse_pos = (0, 0)
        self.show_turret_range = False

        self.background = self.create_background()
        self.start_wave()

    def create_background(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            green = min(255, 100 + y // 3)
            color = (50, green, 150)
            pygame.draw.line(surf, color, (0, y), (SCREEN_WIDTH, y))
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(surf, DARK_GREEN, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(surf, DARK_GREEN, (0, y), (SCREEN_WIDTH, y), 1)
        for i in range(len(self.current_path_world)-1):
            start = self.current_path_world[i]
            end = self.current_path_world[i+1]
            pygame.draw.line(surf, BROWN, start, end, GRID_SIZE-4)
        if self.current_path_world:
            pygame.draw.circle(surf, GREEN, self.current_path_world[0], 15)
            pygame.draw.circle(surf, RED, self.current_path_world[-1], 15)
        return surf

    def update_background(self):
        self.background = self.create_background()

    def start_wave(self):
        self.wave_in_progress = True
        self.enemies_to_spawn = self.generate_wave_enemies()
        self.enemies_spawned = 0
        self.enemy_spawn_timer = 0

    def generate_wave_enemies(self):
        wave = self.current_wave
        level = self.level
        enemies = []
        normal_count = int(5 + wave * 2 + level * 0.5)
        elite_count = int(1 + wave // 2 + level // 3)
        boss_count = 1 if wave == 5 else 0
        normal_count = min(normal_count, 15)
        elite_count = min(elite_count, 3)
        for _ in range(normal_count):
            enemies.append(EnemyType.NORMAL)
        for _ in range(elite_count):
            enemies.append(EnemyType.ELITE)
        if boss_count:
            enemies.append(EnemyType.BOSS)
        random.shuffle(enemies)
        return enemies

    def spawn_enemy(self):
        if self.enemies_spawned >= len(self.enemies_to_spawn):
            return
        etype = self.enemies_to_spawn[self.enemies_spawned]
        enemy = Enemy(self.current_path_world, etype)
        self.all_enemies.add(enemy)
        self.enemies_spawned += 1

    def update(self):
        if self.game_over or self.game_win:
            return

        # 更新放置冷却
        if self.build_cooldown > 0:
            self.build_cooldown -= 1

        # 波次控制
        if self.wave_in_progress:
            if self.enemies_spawned < len(self.enemies_to_spawn):
                if self.enemy_spawn_timer <= 0:
                    self.spawn_enemy()
                    self.enemy_spawn_timer = ENEMY_SPAWN_DELAY
                else:
                    self.enemy_spawn_timer -= 1
            else:
                if len(self.all_enemies) == 0:
                    self.wave_in_progress = False
                    if self.current_wave < 5:
                        self.current_wave += 1
                        self.wave_timer = WAVE_DELAY
                    else:
                        if self.level < 10:
                            self.level += 1
                            self.current_wave = 1
                            self.gold += 200
                            self.current_path_points = level_paths[self.level-1]
                            self.current_path_world = [grid_to_world(p) for p in self.current_path_points]
                            self.update_background()
                            self.all_turrets.clear()
                            self.wave_timer = WAVE_DELAY * 2
                        else:
                            self.game_win = True
        else:
            if self.wave_timer > 0:
                self.wave_timer -= 1
            else:
                self.start_wave()

        # 更新敌人和奖励
        for enemy in self.all_enemies:
            enemy.update()
            if not enemy.alive and not enemy.reward_given:
                self.gold += enemy.value
                self.score += enemy.value
                enemy.reward_given = True
            if enemy.current_point_index >= len(self.current_path_world) - 1 and enemy.alive:
                self.lives -= 1
                enemy.alive = False
                enemy.reward_given = True
                enemy.die()
                if self.lives <= 0:
                    self.game_over = True

        # 移除死亡动画结束的敌人
        for enemy in self.all_enemies:
            if enemy.death_animation and enemy.death_counter > 15:
                enemy.kill()

        # 炮塔与子弹
        for turret in self.all_turrets:
            bullet = turret.update(self.all_enemies)
            if bullet:
                self.all_bullets.append(bullet)

        for bullet in self.all_bullets:
            bullet.update()
        self.all_bullets = [b for b in self.all_bullets if b.active]

        # 鼠标悬停炮塔范围
        mouse_grid = world_to_grid(self.mouse_pos)
        self.show_turret_range = False
        for turret in self.all_turrets:
            if turret.grid_pos == mouse_grid:
                self.selected_turret = turret
                self.show_turret_range = True
                break
        else:
            self.selected_turret = None

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for turret in self.all_turrets:
            turret.draw(self.screen)
        for bullet in self.all_bullets:
            bullet.draw(self.screen)
        for enemy in self.all_enemies:
            enemy.draw(self.screen)

        self.draw_ui()

        # 炮塔预览（带冷却限制）
        if not self.game_over and not self.game_win:
            mouse_grid = world_to_grid(self.mouse_pos)
            # 检查能否放置（路径、已有炮塔、金币足够）
            can_place = (is_tower_allowed(mouse_grid, self.current_path_points) and
                         not self.is_tower_at(mouse_grid) and
                         self.gold >= TURRET_PRICE)
            # 冷却中则不能放置
            if self.build_cooldown > 0:
                can_place = False
            if can_place:
                rect = pygame.Rect(mouse_grid[0]*GRID_SIZE, mouse_grid[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
                s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                s.fill((0, 255, 0, 100))
                self.screen.blit(s, rect)
            elif not is_tower_allowed(mouse_grid, self.current_path_points) or self.is_tower_at(mouse_grid):
                rect = pygame.Rect(mouse_grid[0]*GRID_SIZE, mouse_grid[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
                s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                s.fill((255, 0, 0, 100))
                self.screen.blit(s, rect)

        if self.show_turret_range and self.selected_turret:
            pygame.draw.circle(self.screen, CYAN, self.selected_turret.world_pos, self.selected_turret.range, 2)

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            text = self.big_font.render("GAME OVER", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(text, text_rect)
            text2 = self.font.render("按 R 重新开始，按 ESC 退出", True, WHITE)
            text2_rect = text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(text2, text2_rect)
        elif self.game_win:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            text = self.big_font.render("VICTORY!", True, GREEN)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(text, text_rect)
            text2 = self.font.render("通关！按 R 重新开始", True, WHITE)
            text2_rect = text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(text2, text2_rect)

        pygame.display.flip()

    def draw_ui(self):
        ui_bg = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
        ui_bg.fill((0, 0, 0, 180))
        self.screen.blit(ui_bg, (0, 0))

        gold_text = self.font.render(f"💰 {self.gold}", True, YELLOW)
        lives_text = self.font.render(f"❤️ {self.lives}", True, RED)
        level_text = self.font.render(f"第 {self.level}/10 关", True, CYAN)
        wave_text = self.font.render(f"第 {self.current_wave}/5 波", True, ORANGE)
        score_text = self.font.render(f"🏆 {self.score}", True, WHITE)
        enemies_left = len(self.all_enemies)
        enemies_text = self.font.render(f"👾 剩余 {enemies_left}", True, WHITE)

        self.screen.blit(gold_text, (10, 8))
        self.screen.blit(lives_text, (10, 28))
        self.screen.blit(level_text, (100, 8))
        self.screen.blit(wave_text, (100, 28))
        self.screen.blit(score_text, (200, 8))
        self.screen.blit(enemies_text, (200, 28))

        # 显示冷却倒计时
        if self.build_cooldown > 0:
            cd_sec = self.build_cooldown / FPS
            cd_text = self.font.render(f"建造冷却: {cd_sec:.1f}s", True, RED)
            self.screen.blit(cd_text, (SCREEN_WIDTH - 150, 28))

        if not self.wave_in_progress and self.wave_timer > 0 and not self.game_over and not self.game_win:
            countdown = self.wave_timer // FPS
            cd_text = self.font.render(f"下一波: {countdown}秒", True, WHITE)
            self.screen.blit(cd_text, (SCREEN_WIDTH//2 - 80, 35))

        turret_price_text = self.font.render(f"炮塔 {TURRET_PRICE}💰", True, GREEN)
        self.screen.blit(turret_price_text, (SCREEN_WIDTH - 120, 8))
        tip_text = self.font.render("左键建塔 | 右键升级", True, WHITE)
        self.screen.blit(tip_text, (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT - 20))

    def is_tower_at(self, grid_pos):
        for turret in self.all_turrets:
            if turret.grid_pos == grid_pos:
                return True
        return False

    def add_tower(self, grid_pos):
        # 检查冷却
        if self.build_cooldown > 0:
            return False
        if is_tower_allowed(grid_pos, self.current_path_points) and not self.is_tower_at(grid_pos) and self.gold >= TURRET_PRICE:
            self.gold -= TURRET_PRICE
            self.all_turrets.append(Turret(grid_pos))
            self.build_cooldown = int(BUILD_COOLDOWN_SECONDS * FPS)
            return True
        return False

    def upgrade_tower(self, grid_pos):
        for turret in self.all_turrets:
            if turret.grid_pos == grid_pos:
                cost = 80 * turret.level
                if self.gold >= cost:
                    if turret.upgrade():
                        self.gold -= cost
                        return True
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over or self.game_win:
                    continue
                mouse_grid = world_to_grid(pygame.mouse.get_pos())
                if event.button == 1:  # 左键
                    self.add_tower(mouse_grid)
                elif event.button == 3:  # 右键
                    self.upgrade_tower(mouse_grid)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.game_over or self.game_win):
                    self.__init__()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TowerDefenseGame()
    game.run()
