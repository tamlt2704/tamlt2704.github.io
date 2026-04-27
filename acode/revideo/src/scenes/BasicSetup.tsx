import { makeScene2D } from "@revideo/2d";
import { waitFor } from "@revideo/core";
import { IDE } from "../components/IDE";


export const basicsetup = makeScene2D('basicsetup', function* (view) {
    const ide = new IDE();
    view.add(ide.container);

    yield* ide.show();
    yield* waitFor(1);
})