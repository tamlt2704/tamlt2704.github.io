import { makeScene2D } from "@revideo/2d";
import { waitFor } from "@revideo/core";


export const basicsetup = makeScene2D('basicsetup', function* (view) {
    yield* waitFor(1);
})