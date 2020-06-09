
Module.register("mmpm", {
  defaults: {},

  start() {
    console.log("Starting module: mmpm");
    this.sendSocketNotification("Started MMPM", this.config);
  },

  notificationReceived(notification, payload) {
    console.log(notification, payload);

    if (notification == "GET_ACTIVE_MODULES") {
      this.notificationSend(MM.getModules());
    }
  },
});
