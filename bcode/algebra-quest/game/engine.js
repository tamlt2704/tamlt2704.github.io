/**
 * Algebra Quest — Game Engine
 * Handles rendering, game state, animations, and scene management
 */

import { Renderer } from './renderer.js';
import { sprites } from './sprites.js';

const SCENES = { TITLE: 'title', LEVEL_INTRO: 'level_intro', PLAYING: 'playing', VICTORY: 'victory', GAME_OVER: 'game_over' };

export class Game {
  constructor(canvas, levels) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.levels = levels;
    this.renderer = new Renderer(this.ctx, 480, 320);

    // State
    this.scene = SCENES.TITLE;
    this.level = 0;
    this.score = 0;
    this.lives = 3;
    this.currentEquation = null;
    this.equationsSolved = 0;
    this.monsterHP = 0;
    this.monsterMaxHP = 0;
    this.shakeTimer = 0;
    this.flashTimer = 0;
    this.particles = [];
    this.time = 0;

    // DOM elements
    this.hud = document.getElementById('hud');
    this.levelDisplay = document.getElementById('level-display');
    this.scoreDisplay = document.getElementById('score-display');
    this.livesDisplay = document.getElementById('lives-display');
    this.equationPanel = document.getElementById('equation-panel');
    this.equationText = document.getElementById('equation-text');
    this.answerInput = document.getElementById('answer-input');
    this.submitBtn = document.getElementById('submit-btn');
    this.feedback = document.getElementById('feedback');

    this.setupInput();
  }

  setupInput() {
    // Submit answer
    this.submitBtn.addEventListener('click', () => this.submitAnswer());
    this.answerInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.submitAnswer();
    });

    // Title screen click
    this.canvas.addEventListener('click', () => {
      if (this.scene === SCENES.TITLE) this.startGame();
      if (this.scene === SCENES.LEVEL_INTRO) this.startLevel();
      if (this.scene === SCENES.VICTORY) this.nextLevel();
      if (this.scene === SCENES.GAME_OVER) this.resetGame();
    });
  }

  start() {
    this.loop();
  }

  loop() {
    this.time += 1 / 60;
    this.update();
    this.render();
    requestAnimationFrame(() => this.loop());
  }

  update() {
    // Shake decay
    if (this.shakeTimer > 0) this.shakeTimer -= 1 / 60;
    if (this.flashTimer > 0) this.flashTimer -= 1 / 60;

    // Particles
    this.particles = this.particles.filter(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.15; // gravity
      p.life -= 0.02;
      return p.life > 0;
    });
  }

  render() {
    const r = this.renderer;
    const shake = this.shakeTimer > 0 ? (Math.random() - 0.5) * 4 : 0;

    this.ctx.save();
    this.ctx.translate(shake, shake);

    switch (this.scene) {
      case SCENES.TITLE: this.renderTitle(r); break;
      case SCENES.LEVEL_INTRO: this.renderLevelIntro(r); break;
      case SCENES.PLAYING: this.renderPlaying(r); break;
      case SCENES.VICTORY: this.renderVictory(r); break;
      case SCENES.GAME_OVER: this.renderGameOver(r); break;
    }

    // Render particles on top
    this.particles.forEach(p => {
      this.ctx.globalAlpha = p.life;
      this.ctx.fillStyle = p.color;
      this.ctx.fillRect(p.x, p.y, p.size, p.size);
    });
    this.ctx.globalAlpha = 1;

    this.ctx.restore();
  }

  // ── Scenes ────────────────────────────────────

  renderTitle(r) {
    r.clear('#0a0a2e');
    r.stars(this.time);
    r.drawText('ALGEBRA QUEST', 140, 80, '#ffd700', 24);
    r.drawText('The Adventure Begins', 155, 115, '#aaa', 12);
    r.drawSprite(sprites.wizard, 216, 150, 3);
    r.drawText('Click to Start', 185, 270, '#4a9eff', 14, true);
  }

  renderLevelIntro(r) {
    const lvl = this.levels[this.level];
    r.clear('#0a0a2e');
    r.stars(this.time);
    r.drawText(`Level ${this.level + 1}`, 200, 60, '#fff', 16);
    r.drawText(lvl.name, 240 - lvl.name.length * 5, 90, '#ffd700', 18);
    r.drawText(lvl.story, 40, 140, '#ccc', 11);
    r.drawSprite(sprites[lvl.monster], 216, 180, 4);
    r.drawText('Click to Begin', 185, 280, '#4a9eff', 14, true);
  }

  renderPlaying(r) {
    const lvl = this.levels[this.level];
    r.clear('#0f0f2a');
    r.stars(this.time * 0.3);

    // Ground
    r.rect(0, 260, 480, 60, '#1a1a3a');
    r.rect(0, 258, 480, 3, '#333');

    // Monster
    const monsterY = 140 + Math.sin(this.time * 2) * 5;
    const flash = this.flashTimer > 0 && Math.floor(this.flashTimer * 10) % 2 === 0;
    if (!flash) {
      r.drawSprite(sprites[lvl.monster], 320, monsterY, 5);
    }

    // Monster HP bar
    const hpPct = this.monsterHP / this.monsterMaxHP;
    r.rect(280, 120, 120, 10, '#333');
    r.rect(280, 120, 120 * hpPct, 10, lvl.color);
    r.drawText(`${this.monsterHP}/${this.monsterMaxHP}`, 310, 108, '#fff', 10);

    // Player (wizard)
    const playerY = 195 + Math.sin(this.time * 1.5) * 2;
    r.drawSprite(sprites.wizard, 80, playerY, 4);

    // Spell effect when answering correctly
    if (this.flashTimer > 0.3) {
      r.circle(200, 180, 15 + (0.5 - this.flashTimer) * 40, 'rgba(255, 215, 0, 0.3)');
    }
  }

  renderVictory(r) {
    const lvl = this.levels[this.level];
    r.clear('#0a1a0a');
    r.stars(this.time);
    r.drawText('VICTORY!', 180, 80, '#4eff4a', 24);
    r.drawText(`${lvl.name} cleared!`, 150, 120, '#aaa', 12);
    r.drawText(`Score: ${this.score}`, 200, 160, '#ffd700', 16);
    if (this.level < this.levels.length - 1) {
      r.drawText('Click for Next Level', 170, 270, '#4a9eff', 14, true);
    } else {
      r.drawText('🏆 YOU BEAT THE GAME! 🏆', 130, 200, '#ffd700', 16);
      r.drawText('Click to Play Again', 175, 270, '#4a9eff', 14, true);
    }
  }

  renderGameOver(r) {
    r.clear('#1a0a0a');
    r.drawText('GAME OVER', 170, 100, '#ff4040', 24);
    r.drawText(`Final Score: ${this.score}`, 185, 150, '#fff', 14);
    r.drawText(`Reached: Level ${this.level + 1}`, 185, 175, '#aaa', 12);
    r.drawSprite(sprites.skull, 216, 200, 3);
    r.drawText('Click to Try Again', 175, 280, '#4a9eff', 14, true);
  }

  // ── Game Logic ────────────────────────────────

  startGame() {
    this.level = 0;
    this.score = 0;
    this.lives = 3;
    this.scene = SCENES.LEVEL_INTRO;
  }

  startLevel() {
    const lvl = this.levels[this.level];
    this.equationsSolved = 0;
    this.monsterHP = lvl.equations;
    this.monsterMaxHP = lvl.equations;
    this.scene = SCENES.PLAYING;
    this.showHUD();
    this.generateEquation();
  }

  generateEquation() {
    const lvl = this.levels[this.level];
    this.currentEquation = lvl.generator();
    this.equationText.textContent = this.currentEquation.equation;
    this.equationPanel.classList.remove('hidden');
    this.answerInput.value = '';
    this.answerInput.focus();
    this.feedback.textContent = '';
    this.feedback.className = '';
  }

  submitAnswer() {
    if (!this.currentEquation) return;
    const userAnswer = parseInt(this.answerInput.value, 10);
    if (isNaN(userAnswer)) return;

    if (userAnswer === this.currentEquation.answer) {
      this.onCorrect();
    } else {
      this.onWrong();
    }
  }

  onCorrect() {
    this.score += 100;
    this.monsterHP--;
    this.equationsSolved++;
    this.flashTimer = 0.5;
    this.shakeTimer = 0.15;
    this.spawnParticles(340, 170, this.levels[this.level].color, 12);

    this.feedback.textContent = '✓ Correct! +100';
    this.feedback.className = 'feedback-correct';
    this.updateHUD();

    if (this.monsterHP <= 0) {
      // Level complete
      setTimeout(() => {
        this.equationPanel.classList.add('hidden');
        this.hud.classList.add('hidden');
        this.scene = SCENES.VICTORY;
      }, 800);
    } else {
      setTimeout(() => this.generateEquation(), 1000);
    }
  }

  onWrong() {
    this.lives--;
    this.shakeTimer = 0.3;
    this.spawnParticles(100, 210, '#ff4040', 8);

    const lvl = this.levels[this.level];
    this.feedback.textContent = `✗ Not quite! Hint: ${lvl.hint}`;
    this.feedback.className = 'feedback-wrong';
    this.updateHUD();

    if (this.lives <= 0) {
      setTimeout(() => {
        this.equationPanel.classList.add('hidden');
        this.hud.classList.add('hidden');
        this.scene = SCENES.GAME_OVER;
      }, 1000);
    } else {
      // Let them try again with same equation
      this.answerInput.value = '';
      this.answerInput.focus();
    }
  }

  nextLevel() {
    if (this.level < this.levels.length - 1) {
      this.level++;
      this.scene = SCENES.LEVEL_INTRO;
    } else {
      this.resetGame();
    }
  }

  resetGame() {
    this.scene = SCENES.TITLE;
    this.equationPanel.classList.add('hidden');
    this.hud.classList.add('hidden');
  }

  // ── UI Helpers ────────────────────────────────

  showHUD() {
    this.hud.classList.remove('hidden');
    this.updateHUD();
  }

  updateHUD() {
    this.levelDisplay.textContent = `Level ${this.level + 1}`;
    this.scoreDisplay.textContent = `⭐ ${this.score}`;
    this.livesDisplay.textContent = '❤️'.repeat(this.lives) + '🖤'.repeat(3 - this.lives);
  }

  spawnParticles(x, y, color, count) {
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x, y,
        vx: (Math.random() - 0.5) * 6,
        vy: (Math.random() - 0.5) * 6 - 2,
        size: Math.random() * 4 + 2,
        color,
        life: 1,
      });
    }
  }
}
