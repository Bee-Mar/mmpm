var nodeHelper = require("node_helper");

module.exports = nodeHelper.create({
  socketNotificationReceived: (notification, payload) => {
    console.log(`MMPM TEST: ${MM.getModules()}`);
  }
});
