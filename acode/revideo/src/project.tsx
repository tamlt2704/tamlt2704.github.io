import {makeProject} from '@revideo/core';

import {Audio, Img, makeScene2D, Video} from '@revideo/2d';
import {all, chain, createRef, waitFor} from '@revideo/core';
import { basicsetup } from './scenes/BasicSetup';

/**
 * The final revideo project
 */
export default makeProject({
  scenes: [basicsetup],
  settings: {
    // Example settings:
    shared: {
      background: '#141414',
      size: {x: 1920, y: 1080},
    },
  },
});
