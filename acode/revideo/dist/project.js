"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("@revideo/core");
const BasicSetup_1 = require("./scenes/BasicSetup");
/**
 * The final revideo project
 */
exports.default = (0, core_1.makeProject)({
    scenes: [BasicSetup_1.basicsetup],
    settings: {
        // Example settings:
        shared: {
            background: '#141414',
            size: { x: 1920, y: 1080 },
        },
    },
});
//# sourceMappingURL=project.js.map