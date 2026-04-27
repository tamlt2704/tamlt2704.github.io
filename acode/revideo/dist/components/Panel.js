"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Panel = void 0;
const jsx_runtime_1 = require("@revideo/2d/lib/jsx-runtime");
const _2d_1 = require("@revideo/2d");
const theme_1 = require("./theme");
class Panel extends _2d_1.Rect {
    constructor(props) {
        const fills = {
            panel: theme_1.Theme.panelBg,
            header: theme_1.Theme.headerBg,
            status: theme_1.Theme.statusBg,
        };
        const { label, ...rest } = props;
        super({
            fill: fills[props.variant || 'panel'],
            radius: 0,
            clip: true,
            layout: true,
            direction: 'column',
            ...props,
        });
        if (label) {
            this.add((0, jsx_runtime_1.jsx)(_2d_1.Txt, { text: label }));
        }
    }
}
exports.Panel = Panel;
//# sourceMappingURL=Panel.js.map