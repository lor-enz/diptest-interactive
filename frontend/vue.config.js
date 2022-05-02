// vue.config.js
module.exports = {
    chainWebpack: config => {
      config.plugin("define").tap(args => {
        let _base = args[0]["process.env"];
        args[0]["process.env"] = {
          ..._base,
          "VUE_APP_API_URL": JSON.stringify(process.env.VUE_APP_API_URL ),
        };
        return args;
      });
    }
  }

  // Now API_URL can be accessed as process.env.VUE_APP_API_URL