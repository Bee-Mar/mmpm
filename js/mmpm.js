Module.register("mmpm", {
  defaults: {refreshInterval: 0, MM: MM},
  config: {MM},

  start: function() {
    console.log("Starting module: mmpm");
    console.log(MM);
  }
});
