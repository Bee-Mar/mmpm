var NodeHelper = require("node_helper")

module.exports = NodeHelper.create({
  socketNotificationReceived: function(notification, payload) {

    // the pseudo log stream from magicmirror
    if (notification === "FROM_MMPM_MODULE_magicmirror_logs") {
      this.sendSocketNotification("MAGICMIRROR_LOGS", payload);
    }

    if (notification === "FROM_MMPM_APP_get_active_modules") {
      this.sendSocketNotification("FROM_MMPM_NODE_HELPER_get_active_modules");

    } else if (notification === "FROM_MMPM_MODULE_active_modules") {
      this.sendSocketNotification("ACTIVE_MODULES", payload);

    } else if (notification === "FROM_MMPM_APP_hide_modules") {
      this.sendSocketNotification("FROM_MMPM_NODE_HELPER_hide_modules", payload);

    } else if (notification === "FROM_MMPM_APP_show_modules") {
      this.sendSocketNotification("FROM_MMPM_NODE_HELPER_show_modules", payload);

    } else if (notification === "FROM_MMPM_MODULE_modules_hidden") {
      this.sendSocketNotification("MODULES_HIDDEN", payload);

    } else if (notification === "FROM_MMPM_MODULE_modules_visible") {
      this.sendSocketNotification("MODULES_VISIBLE", payload);
    }
  },
})
