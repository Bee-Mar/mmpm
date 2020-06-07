"use strict";

Module.regster("mmpm", {
  defaults:{},
  start: () => {
    this.sendSocketNotification("mmpm", this.config);
  },
  socketNotificationReceived: function(notification, payload) {
    this.sendNotification(notification);
  }
});
