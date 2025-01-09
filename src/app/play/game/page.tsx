'use client'
import kaplay from "kaplay";
import { useEffect } from "react";

export default function GameA() {
    useEffect(() => {
        const FLOOR_HEIGHT = 48;
        const JUMP_FORCE = 800;
        const SPEED = 480;
        const {
            setGravity, 
            loadSprite,
            add, sprite, pos, area, body, onKeyPress, rect, width, height, color, outline, anchor, move, LEFT,        
            //loop,
            rand, scene, text,
            addKaboom, shake, wait, go, center,onUpdate
        } = kaplay();
        
        loadSprite("bean", "/assets/sprites/bean.png");
        
        
        scene("game", () => {
            setGravity(1600);
            let score = 0;
            const scoreLabel = add([text(score.toString()), pos(24, 24)]);
            onUpdate(() => {
                score++;
                scoreLabel.text = score.toString();
            });

            const bean = add([
                sprite("bean"),
                pos(80, 40),
                area(), // collision
                body(), // fall due to gravity and able to jump
            ]);
    
            //floor
            add([
                rect(width(), FLOOR_HEIGHT),
                pos(0, height()-48),
                area(), body({isStatic: true}), color(127, 200, 255), outline(4)
            ])

            function spawnTree() {
                add([
                    rect(48, rand(24, 64)),
                    area(),
                    outline(4),
                    pos(width(), height() - 48),
                    anchor("botleft"),
                    color(255, 180, 255),
                    move(LEFT, 480), 
                    "tree",
                ]);
    
                wait(rand(0.5, 1.5), () => {
                    spawnTree();
                });
            }
    
            spawnTree()
    
            bean.onCollide("tree", () => {
                addKaboom(bean.pos);
                shake();
                go("lose");
            })
    
            onKeyPress("space", () => {
                if (bean.isGrounded()) {
                    bean.jump();
                }
            });
        });

        scene("lose", () => {
            add([text("Game Over"), pos(center()), anchor("center")]);
        });
        
        go("game");
        // loop(1, () => {
        //     add([
        //         rect(48, rand(24, 64)),
        //         area(),
        //         outline(4),
        //         pos(width(), height() - 48),
        //         anchor("botleft"),
        //         color(255, 180, 255),
        //         move(LEFT, 480), 
        //         "tree",
        //     ]);
        // })
        
    }, [])
    return (
        <div>
        </div>
    )
}
