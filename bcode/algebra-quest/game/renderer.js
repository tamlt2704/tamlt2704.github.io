/**
 * Algebra Quest — Renderer
 * Handles all canvas drawing: backgrounds, sprites, text, effects
 */

export class Renderer {
  constructor(ctx, width, height) {
    this.ctx = ctx;
    this.width = width;
    this.height = height;
    this.starPositions = this.generateStars(60);
  }

  generateStars(count) {
    const stars = [];
    for (let i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height * 0.8,
        size: Math.random() * 2 + 0.5,
        speed: Math.random() * 0.3 + 0.1,
        brightness: Math.random(),
      });
    }
    return stars;
  }

  clear(color) {
    this.ctx.fillStyle = color;
    this.ctx.fillRect(0, 0, this.width, this.height);
  }

  rect(x, y, w, h, color) {
    this.ctx.fillStyle = color;
    this.ctx.fillRect(x, y, w, h);
  }

  circle(x, y, radius, color) {
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, Math.PI * 2);
    this.ctx.fillStyle = color;
    this.ctx.fill();
  }

  stars(time) {
    this.starPositions.forEach(star => {
      const twinkle = Math.sin(time * star.speed * 5 + star.brightness * 10) * 0.3 + 0.7;
      this.ctx.globalAlpha = twinkle * star.brightness;
      this.ctx.fillStyle = '#ffffff';
      this.ctx.fillRect(star.x, star.y, star.size, star.size);
    });
    this.ctx.globalAlpha = 1;
  }

  drawText(text, x, y, color = '#fff', size = 14, blink = false) {
    if (blink && Math.floor(Date.now() / 600) % 2 === 0) return;
    this.ctx.font = `${size}px "Courier New", monospace`;
    this.ctx.fillStyle = color;
    this.ctx.fillText(text, x, y + size);
  }

  drawSprite(spriteData, x, y, scale = 1) {
    if (!spriteData) return;
    const { data, palette, width: sw, height: sh } = spriteData;
    const pixelSize = scale;

    for (let py = 0; py < sh; py++) {
      for (let px = 0; px < sw; px++) {
        const colorIndex = data[py * sw + px];
        if (colorIndex === 0) continue; // transparent
        this.ctx.fillStyle = palette[colorIndex];
        this.ctx.fillRect(
          x + px * pixelSize,
          y + py * pixelSize,
          pixelSize,
          pixelSize
        );
      }
    }
  }
}
