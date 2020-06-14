class Body {
    constructor(x, y, next=null) {
        this.x = x
        this.y = y
        this.next = next
    }
}

const DIRECTION_POS = {
    'UP': [0, -1],
    'DOWN': [0, 1],
    'LEFT': [-1, 0],
    'RIGHT': [1, 0]
}

class Snake {
    constructor(ctx, x, y, strokeStyle="black", fillStyle="white") {
        this.width = 16
        this.height = 16
        this.ctx = ctx
        this.strokeStyle = strokeStyle
        this.fillStyle = fillStyle
        this.head = new Body(x, y)
        this.speed = 200
        this.movetime = 0
        this.alive = true
        this.direction =  DIRECTION_POS.RIGHT
        this.heading = DIRECTION_POS.RIGHT
        this.path = []
    }
    
    eatFootAt(x, y) {
        this.head = new Body(x, y, this.head)
    }

    render() {
        var body = this.head
        while (body) {
            ctx.strokeStyle = this.strokeStyle
            ctx.fillStyle = this.fillStyle
            ctx.fillRect(body.x * this.width, body.y * this.height, this.width, this.height)
            ctx.strokeRect(body.x * this.width, body.y * this.height, this.width, this.height)
            body = body.next
        }
    }

    hitWall(point) {
        var {x, y} = point ? point : this.head
        x *= this.width
        y *= this.height
        if ((x < 0) || (x > this.ctx.canvas.width) || (y < 0) || (y > this.ctx.canvas.height)) {
            return true
        }
        return false
    }

    update(time) {
        if ((time - this.movetime)> this.speed) {
            var newHead
            if (this.path.length) {
                [x, y] = this.path.shift()
                newHead = new Body(x, y)
            } else {
                var [x, y] = this.direction
                newHead = new Body(this.head.x + x, this.head.y + y)
            }
            
            if (!this.hitWall(newHead)) {
                newHead.next = this.head
                var body = newHead
                var prev = body
                while (body) {
                    if (body.next) {
                        prev = body
                    }
                    body = body.next
                }
                prev.next = null
                this.head = newHead
            }
            this.movetime = time
        }
        
        this.render()
    }
}

const canvas = document.querySelector("#board canvas")
const ctx = canvas.getContext("2d")
const {width: w, height: h} = canvas
ctx.fillStyle = "black"
ctx.fillRect(0, 0, w, h)

const snake = new Snake(ctx, 10, 10)
snake.eatFootAt(11, 10)
snake.eatFootAt(12, 10)
snake.render()

let dt = 0
let last = 0
function gameLoop(ms) {
    requestAnimationFrame(gameLoop)
    ctx.fillStyle = "black"
    ctx.fillRect(0, 0, w, h)
    snake.update(ms)
}

requestAnimationFrame(gameLoop)
