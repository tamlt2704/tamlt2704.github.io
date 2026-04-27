import { Rect, RectProps, Txt } from "@revideo/2d";
import { Theme } from "./theme";

export interface PanelProps extends RectProps {
    variant?: 'panel' | 'header' | 'status';
    label?: string;
}

export class Panel extends Rect {
    public constructor(props: PanelProps) {
        const fills = {
            panel: Theme.panelBg,
            header: Theme.headerBg,
            status: Theme.statusBg,    
        }
        const {label, ...rest} = props;

        super({
            fill: fills[props.variant || 'panel'],
            clip: true,
            layout: true,
            direction: 'column',
            stroke: 'white',
            lineWidth: 2,
            ...props,
        })

        if (label) {
            this.add(<Txt 
                text={label}
            />)
        }
    }
}