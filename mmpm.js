
Module.register("mmpm", {
  defaults: {},

  start() {
    console.log("Starting module: mmpm");
    this.sendSocketNotification("Started MMPM", this.config);
  },

  notificationReceived(notification, payload) {
    let modules = MM.getModules();
  },
});
