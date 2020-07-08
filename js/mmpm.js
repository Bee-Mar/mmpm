Module.register("mmpm", {
  defaults: {
    refreshInterval: 0
  },

  start: function() {
    console.log("Starting module: mmpm");
    this.sendSocketNotification("MMPM_START");
  },

  socketNotificationReceived: function(notification, payload, sender) {
    if (notification === "FROM_NODE_HELPER_get_active_modules") {
      const modules = MM.getModules();
      let payload = [];

      for (const m of modules) {
        payload.push({
          name: m.data.name,
          config: m.config
        });
      }

      this.sendSocketNotification("FROM_MMPM_MODULE_active_modules", payload);

    } else if (notification === "FROM_NODE_HELPER_hide_modules") {
      this.sendSocketNotification("FROM_MMPM_MODULE_modules_hidden", payload);

    } else if (notification === "FROM_NODE_HELPER_show_modules") {
      this.sendSocketNotification("FROM_MMPM_MODULE_active_modules", payload);

    }
  },
});
