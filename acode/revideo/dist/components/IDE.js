"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.IDE = void 0;
const jsx_runtime_1 = require("@revideo/2d/lib/jsx-runtime");
const _2d_1 = require("@revideo/2d");
const core_1 = require("@revideo/core");
const theme_1 = require("./theme");
class IDE {
    constructor() {
        this.menuBarRect = (0, core_1.createRef)();
        this.bodyRect = (0, core_1.createRef)();
        this.commandLineRect = (0, core_1.createRef)();
        this.instructionRect = (0, core_1.createRef)();
        this.container = ((0, jsx_runtime_1.jsxs)(_2d_1.Rect, { width: 1600, height: 900, radius: 12, clip: true, layout: true, fill: "white", direction: "column", opacity: 0, children: [(0, jsx_runtime_1.jsx)(_2d_1.Rect, { ref: this.menuBarRect, width: "100%", height: 40, fill: theme_1.Theme.headerBg }), (0, jsx_runtime_1.jsx)(_2d_1.Rect, { ref: this.bodyRect, width: "100%", height: 40, fill: theme_1.Theme.headerBg }), (0, jsx_runtime_1.jsx)(_2d_1.Rect, { ref: this.commandLineRect, width: "100%", height: 40, fill: theme_1.Theme.headerBg }), (0, jsx_runtime_1.jsx)(_2d_1.Rect, { ref: this.instructionRect, width: "100%", height: 40, fill: theme_1.Theme.headerBg })] }));
    }
    *show(duration = 0.4) {
        yield* this.container.opacity(1, duration);
    }
    *hide(duration = 0.4) {
        yield* this.container.opacity(0, duration);
    }
}
exports.IDE = IDE;
//# sourceMappingURL=IDE.js.map