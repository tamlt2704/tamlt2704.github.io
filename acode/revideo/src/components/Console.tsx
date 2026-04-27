import { createRef, waitFor } from "@revideo/core";
import { Panel, PanelProps} from "./Panel";
import { Txt } from "@revideo/2d";
import { Theme } from "./theme";

export class Console extends Panel {
    private txt = createRef<Txt>();

    public constructor(props: PanelProps) {
        super({
            variant: "panel",
            padding: 12,
            stroke: 'red',
            lineWidth: 2,
            ...props
        });

        this.add(
            <Txt 
                ref={this.txt}
                text="$ "
                fill={Theme.textAccent}
                fontFamily={Theme.fontMono}
                fontSize={Theme.fontSizeCode}
            />
        );
    }

    public *type(text: string, speed=0.03) {
        for(let i = 0; i <= text.length; i++) {
            this.txt().text(text.slice(0, i));
            yield* waitFor(speed);
        }
    }

    public *clear() {
        this.txt().text("", 0.1);
    }
}