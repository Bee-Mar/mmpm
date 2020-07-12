Module.register("mmpm", {
  defaults: {
    refreshInterval: 0
  },

  start: function() {
    console.log("Starting module: mmpm");
    // doesn't matter what's sent through the socket, need something to initalize the node_helper
    this.sendSocketNotification("MMPM_START");
  },

  modifyModuleVisibility: function(payload, method) {
    let result = {
      successes: [],
      fails: []
    };

    for (const userProvidedModuleName of payload) {
      // returns an array of matches
      let found = MM.getModules().filter((module) => module.name === userProvidedModuleName);

      if (found.length) {
        method(found[0]);
        result.successes.push(m);
      } else {
        result.fails.push(m)
      }
    }
    return result
  },

  socketNotificationReceived: function(notification, payload) {
    if (notification === "FROM_MMPM_NODE_HELPER_get_active_modules") {
      Log.log("MMPM module received request to retreive active modules list");

      let activeModules = [];

      for (const module of MM.getModules()) {
        if (typeof module !== "undefined") {
          activeModules.push({
            name: module.name,
            hidden: module.hidden
          });
        }
      }

      Log.log("MMPM module finished retreival list of active modules");
      Log.log("MMPM module sending back list of active modules to MMPM application");
      this.sendSocketNotification("FROM_MMPM_MODULE_active_modules", activeModules);

    } else if (notification === "FROM_MMPM_NODE_HELPER_hide_modules") {
      Log.log(`MMPM module received request to hide ${payload} module`);

      let result = this.modifyModuleVisibility(payload, MM.hideModule);

      Log.log(`MMPM module finished hiding ${payload} module`);
      Log.log("MMPM module sending back success to MMPM application");
      this.sendSocketNotification("FROM_MMPM_MODULE_modules_hidden", result);

    } else if (notification === "FROM_MMPM_NODE_HELPER_show_modules") {
      Log.log(`MMPM module received request to show ${payload} module`);

      let result = this.modifyModuleVisibility(payload, MM.showModule);

      Log.log(`MMPM module finished showing ${payload} module`);
      Log.log("MMPM module sending back success to MMPM application");
      this.sendSocketNotification("FROM_MMPM_MODULE_modules_shown", result);
    }
  },
});
