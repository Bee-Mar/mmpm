Module.register("mmpm", {
  defaults: {
    refreshInterval: 0
  },

  start: function() {
    console.log("Starting module: mmpm");
    this.sendSocketNotification("MMPM_START");
  },

  notificationReceived: function(notification, payload, sender) {
    if (notification !== "CLOCK_SECOND") {
      this.sendSocketNotification(
        "FROM_MMPM_MODULE_magicmirror_logs", {
          notification: notification,
          payload: payload,
          sender: sender ? sender.name : "MagicMirror"
        }
      );
    }
  },

  socketNotificationReceived: function(notification, payload) {
    if (notification === "FROM_MMPM_NODE_HELPER_get_active_modules") {
      Log.log("MMPM module received request to retreive active modules list");

      const modules = MM.getModules();
      let payload = [];

      for (const m of modules) {
        if (typeof m !== "undefined") {
          payload.push({
            name: m.name,
            hidden: m.hidden
          });
        }
      }

      Log.log("MMPM module finished retreival list of active modules");
      Log.log("MMPM module sending back list of active modules to MMPM application");
      this.sendSocketNotification("FROM_MMPM_MODULE_active_modules", payload);

    } else if (notification === "FROM_MMPM_NODE_HELPER_hide_modules") {
      Log.log(`MMPM module received request to hide ${payload} module`);

      let m = MM.getModules((mod) => mod.name === payload);
      let found = false;

      if (m.length) {
        MM.hideModule(m[0]);
        found = true;
      }

      Log.log(`MMPM module finished hiding ${payload} module`);
      Log.log("MMPM module sending back success to MMPM application");
      this.sendSocketNotification("FROM_MMPM_MODULE_modules_hidden", {success: found});

    } else if (notification === "FROM_MMPM_NODE_HELPER_show_modules") {
      Log.log(`MMPM module received request to show ${payload} module`);

      let m = MM.getModules((mod) => mod.name === payload);
      let found = false;

      if (m.length) {
        MM.showModule(m[0]);
        found = true;
      }

      Log.log(`MMPM module finished showing ${payload} module`);
      Log.log("MMPM module sending back success to MMPM application");
      this.sendSocketNotification("FROM_MMPM_MODULE_active_modules", {success: found});
    }
  },
});
