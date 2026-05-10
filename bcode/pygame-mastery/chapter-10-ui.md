# Chapter 10: UI & Menus — Scene Management

[← Chapter 9: Particles](chapter-09-particles.md) | [Chapter 11: Save & Load →](chapter-11-persistence.md)

---

## The Problem

The game launches directly into gameplay. There's no title screen. No pause menu. No game over screen. No way to restart without closing and reopening. Sam watches you playtest and asks: "How does someone who isn't you know what to do?"

Games need scenes — distinct states with their own logic and rendering:

- **Title Screen**: Press Start, Options, Quit
- **Gameplay**: The actual game
- **Pause Menu**: Resume, Settings, Quit to Title
- **Game Over**: Score, Retry, Quit

## Scene Architecture

```python
class Scene:
    """Base class for all game scenes."""
    def __init__(self, game):
        self.game = game  # Reference to main game (for scene switching)

    def enter(self):
        """Called when this scene becomes active."""
        pass

    def exit(self):
        """Called when leaving this scene."""
        pass

    def handle_events(self, events):
        """Process input events."""
        pass

    def update(self, dt):
        """Update logic."""
        pass

    def draw(self, surface):
        """Render the scene."""
        pass


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene = None

    def change_scene(self, new_scene):
        if self.scene:
            self.scene.exit()
        self.scene = new_scene
        self.scene.enter()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if self.scene:
                self.scene.handle_events(events)
                self.scene.update(dt)
                self.scene.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
```

## Title Screen

```python
class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.options = ["Start Game", "Options", "Quit"]
        self.selected = 0
        self.pulse_timer = 0.0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._select_option()

    def _select_option(self):
        if self.options[self.selected] == "Start Game":
            self.game.change_scene(GameplayScene(self.game))
        elif self.options[self.selected] == "Quit":
            self.game.running = False

    def update(self, dt):
        self.pulse_timer += dt

    def draw(self, surface):
        surface.fill((10, 10, 20))

        # Title
        title = self.title_font.render("VOID RUNNERS", True, (0, 255, 180))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title, title_rect)

        # Menu options
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected else (100, 100, 100)
            if i == self.selected:
                # Pulsing highlight
                import math
                alpha = int(180 + 75 * math.sin(self.pulse_timer * 4))
                color = (0, min(255, alpha), min(255, int(alpha * 0.7)))

            text = self.menu_font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 50))
            surface.blit(text, text_rect)

            # Selection indicator
            if i == self.selected:
                pygame.draw.polygon(surface, color, [
                    (text_rect.left - 20, text_rect.centery),
                    (text_rect.left - 10, text_rect.centery - 6),
                    (text_rect.left - 10, text_rect.centery + 6),
                ])
```

## Pause Menu

The pause menu overlays on top of gameplay — it doesn't replace it:

```python
class PauseOverlay:
    def __init__(self):
        self.active = False
        self.options = ["Resume", "Settings", "Quit to Title"]
        self.selected = 0
        self.font = pygame.font.Font(None, 36)

    def toggle(self):
        self.active = not self.active
        self.selected = 0

    def handle_events(self, events, game):
        if not self.active:
            return False  # Not consuming events

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle()
                    return True
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._select(game)
        return True  # Events consumed by pause menu

    def _select(self, game):
        if self.options[self.selected] == "Resume":
            self.toggle()
        elif self.options[self.selected] == "Quit to Title":
            game.change_scene(TitleScene(game))

    def draw(self, surface):
        if not self.active:
            return

        # Dim overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        surface.blit(overlay, (0, 0))

        # Pause text
        title = self.font.render("PAUSED", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 200)))

        # Options
        for i, option in enumerate(self.options):
            color = (0, 255, 180) if i == self.selected else (150, 150, 150)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 280 + i * 40))
            surface.blit(text, rect)
```

## HUD (Heads-Up Display)

In-game UI showing health, score, wave number:

```python
class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 48)

    def draw(self, surface, player_hp, max_hp, score, wave):
        # Health bar
        bar_width = 200
        bar_height = 16
        bar_x = 16
        bar_y = 16

        # Background
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        # Fill
        fill_width = int(bar_width * (player_hp / max_hp))
        color = (0, 255, 100) if player_hp > max_hp * 0.3 else (255, 50, 50)
        pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height))
        # Border
        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)

        # HP text
        hp_text = self.font.render(f"{player_hp}/{max_hp}", True, (255, 255, 255))
        surface.blit(hp_text, (bar_x + bar_width + 8, bar_y - 2))

        # Score (top right)
        score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(topright=(SCREEN_WIDTH - 16, 16))
        surface.blit(score_text, score_rect)

        # Wave indicator
        wave_text = self.font.render(f"Wave {wave}", True, (200, 200, 200))
        wave_rect = wave_text.get_rect(topright=(SCREEN_WIDTH - 16, 44))
        surface.blit(wave_text, wave_rect)
```

## Game Over Screen

```python
class GameOverScene(Scene):
    def __init__(self, game, final_score, waves_survived):
        super().__init__(game)
        self.final_score = final_score
        self.waves_survived = waves_survived
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.fade_in = 0.0

    def update(self, dt):
        self.fade_in = min(1.0, self.fade_in + dt * 2)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.change_scene(GameplayScene(self.game))
                elif event.key == pygame.K_ESCAPE:
                    self.game.change_scene(TitleScene(self.game))

    def draw(self, surface):
        surface.fill((10, 5, 5))
        alpha = int(255 * self.fade_in)

        title = self.font.render("GAME OVER", True, (255, 50, 50))
        title.set_alpha(alpha)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 180)))

        score = self.small_font.render(f"Score: {self.final_score}", True, (255, 255, 255))
        surface.blit(score, score.get_rect(center=(SCREEN_WIDTH // 2, 260)))

        waves = self.small_font.render(f"Waves Survived: {self.waves_survived}", True, (200, 200, 200))
        surface.blit(waves, waves.get_rect(center=(SCREEN_WIDTH // 2, 300)))

        if self.fade_in >= 1.0:
            prompt = self.small_font.render("ENTER to Retry | ESC for Title", True, (150, 150, 150))
            surface.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, 400)))
```

## Scene Transitions

Smooth fades between scenes:

```python
class FadeTransition:
    def __init__(self, duration=0.5):
        self.duration = duration
        self.timer = 0.0
        self.active = False
        self.fading_out = True
        self.callback = None

    def start(self, callback):
        """Start fade out, call callback at midpoint, then fade in."""
        self.active = True
        self.fading_out = True
        self.timer = 0.0
        self.callback = callback

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt
        if self.fading_out and self.timer >= self.duration:
            # Midpoint — execute scene change
            if self.callback:
                self.callback()
                self.callback = None
            self.fading_out = False
            self.timer = 0.0
        elif not self.fading_out and self.timer >= self.duration:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return

        if self.fading_out:
            alpha = int(255 * (self.timer / self.duration))
        else:
            alpha = int(255 * (1 - self.timer / self.duration))

        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(alpha)
        surface.blit(fade_surface, (0, 0))
```

## What You Learned

- **Scene architecture** — base Scene class, Game manages current scene
- **Title screen** — menu navigation, selection, visual feedback
- **Pause overlay** — dims gameplay, handles input separately
- **HUD** — health bar, score, wave indicator
- **Game over** — final stats, retry/quit options
- **Transitions** — fade in/out between scenes

The game has structure. A beginning (title), middle (gameplay), and end (game over). Players can pause. They can restart. It feels complete.

But close the game and all progress is lost. No high scores. No settings saved. No "continue from wave 5." Time to persist data.

---

[← Chapter 9: Particles](chapter-09-particles.md) | [Chapter 11: Save & Load →](chapter-11-persistence.md)
