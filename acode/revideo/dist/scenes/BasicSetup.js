"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.basicsetup = void 0;
const _2d_1 = require("@revideo/2d");
const core_1 = require("@revideo/core");
exports.basicsetup = (0, _2d_1.makeScene2D)('basicsetup', function* (view) {
    yield* (0, core_1.waitFor)(1);
});
//# sourceMappingURL=BasicSetup.js.map