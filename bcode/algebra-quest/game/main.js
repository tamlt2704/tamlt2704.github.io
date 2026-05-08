/**
 * Algebra Quest — The Game
 * A pixel-art algebra adventure for kids (ages 10-14)
 * 
 * Solve equations to defeat monsters and progress through levels.
 * Each level introduces harder algebra concepts.
 */

import { Game } from './engine.js';
import { levels } from './levels.js';

const canvas = document.getElementById('game');
const game = new Game(canvas, levels);
game.start();
