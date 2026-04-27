import { Rect } from "@revideo/2d";
import { createRef } from "@revideo/core";
import { Theme } from "./theme";

export class IDE {
    public readonly container: Rect;
    private menuBarRect = createRef<Rect>();
    private bodyRect = createRef<Rect>();
    private commandLineRect = createRef<Rect>();
    private instructionRect = createRef<Rect>();

    constructor() {
        this.container = (
            <Rect 
                width={1600}
                height={900}
                radius={12}
                clip
                layout
                fill="white"
                direction={"column"}
                opacity={0}
            >
                <Rect ref={this.menuBarRect} width="100%" height={40} fill={Theme.headerBg}/>
                <Rect ref={this.bodyRect} width="100%" height={40} fill={Theme.headerBg}/>
                <Rect ref={this.commandLineRect} width="100%" height={40} fill={Theme.headerBg}/>
                <Rect ref={this.instructionRect} width="100%" height={40} fill={Theme.headerBg}/>
            </Rect>
        ) as Rect;
    }

    public *show(duration=0.4) {
        yield* this.container.opacity(1, duration);
    }

    public *hide(duration=0.4) {
        yield* this.container.opacity(0, duration);
    }
}