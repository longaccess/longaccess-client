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
                    modules.assert.ok("content-type" in req.headers, "client didn't send content-type")
                    modules.assert.equal(req.headers['content-type'], 'application/json')
                    content = JSON.parse(req.rawBody)
                    modules.assert.ok("title" in content)
                    modules.assert.ok("description" in content)
                    modules.assert.ok("capsule" in content)
                    modules.assert.ok("size" in content)
                    res.statusCode='200';
                    
                    date = new Date()
                    date.setTime(date.getTime()+(60*60*1000))
                    res.write(JSON.stringify({
                        id: 1,
                        resource_uri: '/path/to/upload/1',
                        token_access_key: '123123',
                        token_secret_key: '123123',
                        token_session: '123123',
                        token_expiration: date.toISOString(),
                        token_uid: '123123',
                        bucket: 'lastage',
                        prefix: 'foobar',
                    }));
                    res.end(); 
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
