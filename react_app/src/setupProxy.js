const { createProxyMiddleware } = require("http-proxy-middleware");

// Proxy middleware for npm start

module.exports = function (app) {
  app.use(
    "/auth",
    createProxyMiddleware({
      target: "http://localhost:5000",
      changeOrigin: true,
      logLevel: "debug", // Add logging for troubleshooting
    })
  );

  app.use(
    "/t4",
    createProxyMiddleware({
      target: "http://localhost:5000",
      changeOrigin: true,
      logLevel: "debug", // Add logging for troubleshooting
    })
  );
};
