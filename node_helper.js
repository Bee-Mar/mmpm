import { create } from "node_helper";

export default create({
  socketNotificationReceived: (notification, payload) => {
    console.log(`MMPM TEST: ${MM.getModules()}`);
  }
});
