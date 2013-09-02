var heads               = require('robohydra').heads,
    RoboHydraHead       = require("robohydra").heads.RoboHydraHead,
    RoboHydraHeadStatic = heads.RoboHydraHeadStatic;

exports.getBodyParts = function(config) {
    return {
        heads: [
            new RoboHydraHeadStatic({
                path: '/',
                content: {
                    capsule: {
                        list_endpoint: "/path/to/api/capsule/",
                        schema: "/path/to/api/capsule/schema/"
                    },
                    upload: {
                        list_endpoint: "/path/to/api/upload/",
                        schema: "/path/to/api/upload/schema/"
                    },
                    user: {
                        list_endpoint: "/path/to/api/user/",
                        schema: "/path/to/api/user/schema/"
                    }
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
