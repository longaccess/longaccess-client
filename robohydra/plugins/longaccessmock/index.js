var heads               = require('robohydra').heads,
    RoboHydraHead       = require("robohydra").heads.RoboHydraHead,
    RoboHydraHeadStatic = heads.RoboHydraHeadStatic,
    apiPrefix           = "/path/to/api";

exports.getBodyParts = function(config, modules) {
    return {
        heads: [
            new RoboHydraHeadStatic({
                path: apiPrefix + '/',
                content: {
                    capsule: {
                        list_endpoint: apiPrefix + "/capsule/",
                        schema: apiPrefix + "/capsule/schema/"
                    },
                    upload: {
                        list_endpoint: apiPrefix + "/upload/",
                        schema: apiPrefix + "/upload/schema/"
                    },
                    user: {
                        list_endpoint: apiPrefix + "/user/",
                        schema: apiPrefix + "/user/schema/"
                    }
                }
            }),
            new RoboHydraHead({
                path: apiPrefix + '/upload/',
                handler: function(req, res, next) {
                    modules.assert.equal(req.method, "POST", "Upload resource supports only POST")
                    res.end()
                }
            })
        ],
        tests: {
            serverProblems: {
                instructions: "Try to upload a file. The client should show some error messaging stating the server couldn't fulfill the request or the API wasn't available",
                heads: [
                    new RoboHydraHead({
                        path: '/.*',
                    handler: function(req, res) {
                        res.statusCode = 500;
                        res.send("500 - (Synthetic) Internal Server Error");
                    }
                    })
                ]
            }
        }
    };
};
