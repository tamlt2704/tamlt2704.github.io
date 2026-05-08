/**
 * Level definitions for Algebra Quest
 * Each level has a theme, monster, and equation generator
 */

// Equation generators by difficulty
function oneStepAdd() {
  const answer = Math.floor(Math.random() * 15) + 1;
  const b = Math.floor(Math.random() * 12) + 1;
  return { equation: `x + ${b} = ${answer + b}`, answer };
}

function oneStepSub() {
  const answer = Math.floor(Math.random() * 15) + 1;
  const b = Math.floor(Math.random() * 10) + 1;
  return { equation: `x - ${b} = ${answer - b}`, answer };
}

function oneStepMul() {
  const answer = Math.floor(Math.random() * 10) + 1;
  const b = Math.floor(Math.random() * 5) + 2;
  return { equation: `${b}x = ${answer * b}`, answer };
}

function oneStepDiv() {
  const b = Math.floor(Math.random() * 5) + 2;
  const answer = Math.floor(Math.random() * 10) + 1;
  return { equation: `x / ${b} = ${answer}`, answer: answer * b };
}

function twoStep() {
  const answer = Math.floor(Math.random() * 10) + 1;
  const a = Math.floor(Math.random() * 4) + 2;
  const b = Math.floor(Math.random() * 8) + 1;
  return { equation: `${a}x + ${b} = ${a * answer + b}`, answer };
}

function twoStepSub() {
  const answer = Math.floor(Math.random() * 10) + 1;
  const a = Math.floor(Math.random() * 4) + 2;
  const b = Math.floor(Math.random() * 8) + 1;
  return { equation: `${a}x - ${b} = ${a * answer - b}`, answer };
}

function withNegatives() {
  const answer = -(Math.floor(Math.random() * 8) + 1);
  const b = Math.floor(Math.random() * 10) + 3;
  return { equation: `x + ${b} = ${answer + b}`, answer };
}

function bothSides() {
  const answer = Math.floor(Math.random() * 8) + 2;
  const a = Math.floor(Math.random() * 3) + 2;
  const b = Math.floor(Math.random() * 5) + 1;
  const c = a - 1;
  const d = b + answer;
  return { equation: `${a}x + ${b} = ${c}x + ${d}`, answer };
}

export const levels = [
  {
    name: "The Whispering Woods",
    monster: "slime",
    color: "#4eff4a",
    equations: 5,
    generator: oneStepAdd,
    hint: "Subtract the number from both sides!",
    story: "A green slime blocks the forest path. Solve equations to shrink it!",
  },
  {
    name: "The Rocky Pass",
    monster: "golem",
    color: "#c0a060",
    equations: 5,
    generator: oneStepSub,
    hint: "Add the number to both sides!",
    story: "A stone golem guards the mountain pass. Each correct answer cracks its armor!",
  },
  {
    name: "The Crystal Cave",
    monster: "bat",
    color: "#c080ff",
    equations: 5,
    generator: oneStepMul,
    hint: "Divide both sides by the number in front of x!",
    story: "Crystal bats swarm the cave. Solve to light your torch and scare them away!",
  },
  {
    name: "The Potion Lab",
    monster: "wizard",
    color: "#4a9eff",
    equations: 5,
    generator: oneStepDiv,
    hint: "Multiply both sides by the divisor!",
    story: "A rogue wizard challenges you to a duel of division!",
  },
  {
    name: "The Two-Lock Tower",
    monster: "knight",
    color: "#ff8040",
    equations: 6,
    generator: twoStep,
    hint: "Undo addition first, then divide!",
    story: "The tower has two locks on each door. Two steps to solve each one!",
  },
  {
    name: "The Subtraction Swamp",
    monster: "croc",
    color: "#40c080",
    equations: 6,
    generator: twoStepSub,
    hint: "Add first to undo subtraction, then divide!",
    story: "Crocodiles lurk in the swamp. Solve fast before they snap!",
  },
  {
    name: "The Underground Kingdom",
    monster: "shadow",
    color: "#8080ff",
    equations: 6,
    generator: withNegatives,
    hint: "The answer can be negative! Below zero is okay!",
    story: "In the underground, numbers go below zero. Don't fear the negatives!",
  },
  {
    name: "The Dragon's Lair",
    monster: "dragon",
    color: "#ff4040",
    equations: 7,
    generator: bothSides,
    hint: "Get all x's on one side first!",
    story: "The Equation Dragon speaks in variables on BOTH sides. This is the final battle!",
  },
];
