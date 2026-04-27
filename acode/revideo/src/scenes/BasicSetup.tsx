import { makeScene2D } from "@revideo/2d";
import { waitFor } from "@revideo/core";
import { IDE } from "../components/IDE";


export const basicsetup = makeScene2D('basicsetup', function* (view) {
    const ide = new IDE();
    view.add(ide.container);

    yield* ide.show();
    yield* ide.consoleTypeText('npm run dev', 0.03);
    yield* waitFor(1);
    // yield* ide.hideMenubar();
})