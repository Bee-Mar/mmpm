Module.register("mmpm", {
	defaults: {
		refreshInterval: 0
	},

	start: function () {
		console.log("Starting module: mmpm");
		// doesn't matter what's sent through the socket, need something to initalize the node_helper
		this.sendSocketNotification("MMPM_START");
	},

	modifyModuleVisibility: function (payload) {
		let modules = MM.getModules();

		for (let index = 0; index < payload.modules.length; index++) {
			const moduleIndex = parseInt(payload.modules[index]) - 1;

			if (payload.directive === "hide") {
				modules[moduleIndex].hide();
			} else {
				modules[moduleIndex].show();
			}
		}

		return payload;
	},

	socketNotificationReceived: function (notification, payload) {
		if (notification === "FROM_MMPM_NODE_HELPER_get_active_modules") {
			Log.log("MMPM module received request to retreive active modules list");

			let activeModules = [];
			const modules = MM.getModules();

			for (let index = 0; index < modules.length; index++) {
				if (modules[index] && modules[index].name.toLowerCase() !== "mmpm") {
					activeModules.push({
						name: modules[index].name,
						hidden: modules[index].hidden,
						index,
					});
				}
			}

			Log.log("MMPM module finished retreival list of active modules");
			Log.log("MMPM module sending back list of active modules to MMPM application");
			this.sendSocketNotification("FROM_MMPM_MODULE_active_modules", activeModules);
		} else if (notification === "FROM_MMPM_NODE_HELPER_toggle_modules") {
			Log.log(`MMPM module received request to hide ${payload} module`);

			let result = this.modifyModuleVisibility(payload);

			Log.log(`MMPM module finished hiding ${payload} module`);
			Log.log("MMPM module sending back modules to MMPM application");
			this.sendSocketNotification("FROM_MMPM_MODULE_modules_toggled", result);
		}
	}
});
