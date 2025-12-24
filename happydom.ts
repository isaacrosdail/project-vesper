// NOTE: Injects browser APIs into global scope & therefore needs to be run before any tests.

import { GlobalRegistrator } from "@happy-dom/global-registrator";

GlobalRegistrator.register();