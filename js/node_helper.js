var NodeHelper = require("node_helper")

module.exports = NodeHelper.create({
  socketNotificationReceived: function(notification, payload) {
    if (notification === "GET_ACTIVE_MODULES") {
      this.sendSocketNotification("MMPM", "hello");
    }
  },
})
