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
                        if (!res.hasOwnProperty('authfail'))
                            return next(req, res);
                    } else { 
                        res.headers["www-authenticate"] = 'Basic realm="foobar"';
                    }
                    res.statusCode = '401';
                    res.send("401 - Forbidden")
                }
            })
        ],
        tests: {
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
            }
        }
    };
};

