const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/api/template-variables/': '/api/template-variables/'  // Explicit path rewrite
      },
      onProxyReq: (proxyReq, req, res) => {
        // Forward all headers from the original request
        Object.keys(req.headers).forEach(key => {
          proxyReq.setHeader(key, req.headers[key]);
        });
        
        // Ensure Authorization header is properly forwarded
        if (req.headers.authorization) {
          proxyReq.setHeader('Authorization', req.headers.authorization);
        }
        
        // Log the proxied request for debugging
        console.log('Proxying request:', {
          originalUrl: req.originalUrl,
          path: req.path,
          headers: req.headers
        });
      },
      onProxyRes: (proxyRes, req, res) => {
        // Add CORS headers to the response
        proxyRes.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000';
        proxyRes.headers['Access-Control-Allow-Credentials'] = 'true';
        proxyRes.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS';
        proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, businessapikey, Accept, Origin, X-API-Key';
      },
      onError: (err, req, res) => {
        console.error('Proxy Error:', err);
        res.status(500).json({ error: 'Proxy Error', details: err.message });
      },
      logLevel: 'debug'  // Enable debug logging
    })
  );
};