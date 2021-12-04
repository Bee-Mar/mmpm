var NodeHelper = require("node_helper");

module.exports = NodeHelper.create({
	socketNotificationReceived: function (notification, payload) {
		if (notification === "FROM_MMPM_APP_get_active_modules") {
			this.sendSocketNotification("FROM_MMPM_NODE_HELPER_get_active_modules");
		} else if (notification === "FROM_MMPM_MODULE_active_modules") {
			this.sendSocketNotification("ACTIVE_MODULES", payload);
		} else if (notification === "FROM_MMPM_APP_toggle_modules") {
			this.sendSocketNotification("FROM_MMPM_NODE_HELPER_toggle_modules", payload);
		} else if (notification === "FROM_MMPM_MODULE_modules_toggled") {
			this.sendSocketNotification("MODULES_TOGGLED", payload);
		}
	}
});
