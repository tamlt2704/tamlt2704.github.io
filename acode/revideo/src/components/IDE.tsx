import { Rect, Txt } from "@revideo/2d";
import { createRef } from "@revideo/core";
import { Theme } from "./theme";
import { Panel } from "./Panel";
import { Console } from "./Console";

export class IDE {
    public readonly container: Rect;
    private menuBarRect = createRef<Rect>();
    private bodyRect = createRef<Panel>();
    private commandLineRect = createRef<Console>();
    private instructionRect = createRef<Panel>();

    constructor() {
        this.container = (
            <Rect 
                width={1600}
                height={900}
                clip
                layout
                fill={Theme.browserBg}
                direction={"row"}
                opacity={1}
            >
                <Panel ref={this.menuBarRect} grow={1} height={"100%"} width={0} fill={Theme.headerBg} label="explorer 123"/>
                <Rect
                    layout
                    direction={"column"}
                    grow={3}
                    height={"100%"}
                >   
                    <Panel ref={this.bodyRect} grow={4} width={"100%"} fill={Theme.headerBg} label="body"/>

                    {/* <Panel ref={this.commandLineRect} grow={1} width={"100%"} fill={Theme.headerBg} label="console"/> */}
                    <Console ref={this.commandLineRect} grow={1} width={"100%"}/>
                </Rect>
                
            </Rect>
        ) as Rect;
    }

    public *hideMenubar(duration=0.4) {
        yield* this.menuBarRect().width(0, duration);
    }

    public *show(duration=0.4) {
        yield* this.container.opacity(1, duration);
    }

    public *hide(duration=0.4) {
        yield* this.container.opacity(0, duration);
    }

    public *consoleTypeText(text: string, speed: 0.03) {
        yield* this.commandLineRect().type(text);
    }
}