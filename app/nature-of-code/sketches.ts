export const sketches = {
  'basic-circle': (p: any) => {
    p.setup = () => {
      p.createCanvas(400, 400);
    }
    p.draw = () => {
      p.background(220);
      p.ellipse(p.width/2, p.height/2, 50, 50);
    }
  },
  
  'bouncing-ball': (p: any) => {
    let x = 200, y = 200;
    let xSpeed = 3, ySpeed = 2;
    
    p.setup = () => {
      p.createCanvas(400, 400);
    }
    p.draw = () => {
      p.background(220);
      p.ellipse(x, y, 30, 30);
      x += xSpeed;
      y += ySpeed;
      if (x > p.width - 15 || x < 15) xSpeed *= -1;
      if (y > p.height - 15 || y < 15) ySpeed *= -1;
    }
  },
  
  'random-walker': (p: any) => {
    let x = 200, y = 200;
    
    p.setup = () => {
      p.createCanvas(400, 400);
      p.background(255);
    }
    p.draw = () => {
      p.stroke(0);
      p.point(x, y);
      x += p.random(-1, 1);
      y += p.random(-1, 1);
    }
  }
};

export const sketchNames = {
  'basic-circle': 'Basic Circle',
  'bouncing-ball': 'Bouncing Ball',
  'random-walker': 'Random Walker'
};