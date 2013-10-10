var heads               = require('robohydra').heads,
    RoboHydraHead       = require("robohydra").heads.RoboHydraHead,
    apiPrefix           = require("./index.js").apiPrefix

exports.getBodyParts = function(config, modules) {
    return {
        heads: [
            new RoboHydraHead({
                path: '/.*',
                handler: function(req, res, next) {
                    if("authorization" in req.headers) {
                        if (res.hasOwnProperty('authuser')) {
                            var auth = req.headers["authorization"].split(" ");
                            modules.assert.equal(auth.length, 2, "client sent invalid auth");
                            modules.assert.equal(auth[0], "Basic", "client didn't send basic auth");
                            var b64creds = new Buffer(auth[1], 'base64'),
                                creds = b64creds.toString().split(":");
                            modules.assert.equal(creds.length, 2, "client sent invalid basic auth");
                            if (creds[0] == "test" && creds[1] == "test")
                                return next(req, res);
                        } else if (!res.hasOwnProperty('authfail'))
                                return next(req, res);
                        
                    }
                    res.headers["www-authenticate"] = 'Basic realm="foobar"';
                    res.statusCode = '401';
                    res.send("401 - Forbidden")
                }
            })
        ],
        scenarios: {
            authFails: {
                instructions: "Authentication will fail",
                heads: [
                    new RoboHydraHead({
                        path: '/.*',
                        handler: function(req, res, next) {
                            res.authfail = true;
                            next(req, res);
                        }
                    })
                ]
            },
            authUser: {
                instructions: "Authentication for user test with password test",
                heads: [
                    new RoboHydraHead({
                        path: '/.*',
                        handler: function(req, res, next) {
                            res.authuser = true;
                            next(req, res);
                        }
                    })
                ]
            }

        }
    };
};

