var heads               = require('robohydra').heads,
    RoboHydraHead       = require("robohydra").heads.RoboHydraHead,
    RoboHydraHeadStatic = heads.RoboHydraHeadStatic,
    token               = require('./tokens.js').token,
    apiPrefix           = "/path/to/api";

exports.getBodyParts = function(config, modules) {
    capsules = {
        'Photos': {
            created: "2013-06-07T10:45:01",
            id: 3,
            resource_uri: "/api/v1/capsule/3/",
            title: "Photos",
            user: "/api/v1/user/3/",
            remaining: 1073741824,
            size: 2073741824
        },
        'Stuff': {
            created: "2013-06-07T10:44:38",
            id: 2,
            resource_uri: "/api/v1/capsule/2/",
            title: "Stuff",
            user: "/api/v1/user/2/",
            remaining: 482,
            size: 1024
        },
        'BFC': {
            created: "2013-06-07T10:45:01",
            id: 1,
            resource_uri: "/api/v1/capsule/1/",
            title: "BFC",
            user: "/api/v1/user/3/",
            remaining: 1024000000,
            size: 1024000000
        }
    }
    archives = {
        'wedding': {
            created: "2013-06-07T10:45:01",
            expires: "2043-06-07T10:45:01",
            id: 1,
            key: 'FOOKEY1',
            resource_uri: "/api/v1/archive/1/",
            title: "My wedding",
            description: "photos from my wedding",
            capsule: "/api/v1/capsule/3/",
            size: 2073741824
        },
        'other': {
            created: "2013-06-07T10:44:38",
            expires: "2043-06-07T10:45:01",
            id: 2,
            key: 'FOOKEY2',
            resource_uri: "/api/v1/archive/2/",
            title: "something else",
            description: "whatevah",
            capsule: "/api/v1/capsule/3/",
            capsule: "/api/v1/capsule/2/",
            size: 1024
        }
    }
    function mockupload() {
        return { id: 1,
            resource_uri: apiPrefix +'/upload/1',
            token_access_key: '123123',
            token_secret_key: '123123',
            token_session: '123123',
            token_uid: '123123',
            bucket: 'foobucket',
            prefix: 'foobar',
            status: 'pending',
        }
    }
    function meta(n){
        return {
            limit: 20,
            next: null,
            offset: 0,
            previous: null,
            total_count: n
        }
    }
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
                    account: {
                        list_endpoint: apiPrefix + "/account/",
                        schema: apiPrefix + "/account/schema/"
                    },
                    archive: {
                        list_endpoint: apiPrefix + "/archive/",
                        schema: apiPrefix + "/archive/schema/"
                    },
                }
            }),
            new RoboHydraHeadStatic({
                path: apiPrefix + '/capsule/',
                content: {
                    meta: meta(0),
                    objects: []
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
                    var ret = mockupload();
                    date = new Date();
                    date.setTime(date.getTime()+(60*60*1000));
                    ret['token_expiration'] = date.toISOString();
                    if (res.hasOwnProperty('token')) {
                        for (var attr in res.token) { 
                            ret[attr] = res.token[attr]; 

                        }
                    }
                    res.write(JSON.stringify(ret));
                    res.end(); 
                }
            }),
            new RoboHydraHead({
                path: apiPrefix + '/upload/1',
                handler: function(req, res, next) {
                    if (req.method == "PATCH") {
                        content = JSON.parse(req.rawBody)
                        modules.assert.ok("status" in content)
                    }
                    res.statusCode='200';
                    var ret = mockupload();
                    date = new Date();
                    date.setTime(date.getTime()+(60*60*1000));
                    ret['token_expiration'] = date.toISOString();
                    if (res.hasOwnProperty('token')) {
                        for (var attr in res.token) { 
                            ret[attr] = res.token[attr]; 

                        }
                    }
                    if (res.hasOwnProperty('upload_status'))
                        ret['status'] = res.upload_status;
                        if (res.upload_status == 'completed')
                            ret['archive_key'] = 'https://longaccess.com/yoyoyo';

                    res.write(JSON.stringify(ret));
                    res.end(); 
                }
            }),
            new RoboHydraHead({
                path: apiPrefix + '/account/',
                handler: function(req, res, next) {
                    ret = {displayname: '', email: ''}
                    if (!res.hasOwnProperty('authuser_name')) {
                        res.statusCode = '401';
                        res.send("401 - Forbidden")
                    }

                    ret['email'] = res.authuser_name;
                    res.write(JSON.stringify(ret));
                    res.end();
                }
            }),
            new RoboHydraHeadStatic({
                path: apiPrefix + '/archive/',
                content: {
                    meta: meta(0),
                    objects: []
                }
            }),
        ],
        scenarios: {
            uploadError: {
                instructions: "Init an upload and then check it's status. it will be 'error'",
                heads: [
                    new RoboHydraHead({
                        path: apiPrefix + '/upload/1',
                        handler: function(req, res, next) {
                            res.upload_status = 'error';
                            next(req, res);
                        }
                    })
                ]
            },
            uploadComplete: {
                instructions: "Init an upload and then check it's status. it will be 'complete'",
                heads: [
                    new RoboHydraHead({
                        path: '/.*',
                        handler: function(req, res, next) {
                            res.authuser = true;
                            next(req, res);
                        }
                    }),
                    new RoboHydraHead({
                        path: apiPrefix + '/upload/1',
                        handler: function(req, res, next) {
                            res.upload_status = 'completed';
                            next(req, res);
                        }
                    })
                ]
            },
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
            },
            realToken: {
                instructions: "return real AWS token.",
                heads: [
                    new RoboHydraHead({
                        path: '/.*',
                        handler: function(req, res, next) {
                            res.token = token;
                            next(req, res);
                        }
                    })
                ]
            },
            oneCapsule: {
                instructions: "activate 1 capsule.",
                heads: [
                    new RoboHydraHead({
                        path: '/.*',
                        handler: function(req, res, next) {
                            res.authuser = true;
                            next(req, res);
                        }
                    }),
                    new RoboHydraHeadStatic({
                        path: apiPrefix + '/capsule/',
                        content: {
                            meta: meta(2),
                            objects: [
                                capsules.Photos,
                                capsules.Stuff
                            ]
                        }
                    })
                ]
            },
            oneHugeCapsule: {
                instructions: "activate 1 capsule.",
                heads: [
                    new RoboHydraHead({
                        path: '/.*',
                        handler: function(req, res, next) {
                            res.authuser = true;
                            next(req, res);
                        }
                    }),
                    new RoboHydraHeadStatic({
                        path: apiPrefix + '/capsule/',
                        content: {
                            meta: meta(1),
                            objects: [
                                capsules.BFC
                            ]
                        }
                    })
                ]
            },
            twoArchives: {
                instructions: "activate 2 archives.",
                heads: [
                    new RoboHydraHead({
                        path: '/.*',
                        handler: function(req, res, next) {
                            console.log("SCENARIO")
                            res.authuser = true;
                            next(req, res);
                        }
                    }),
                    new RoboHydraHeadStatic({
                        path: apiPrefix + '/archive/',
                        content: {
                            meta: meta(2),
                            objects: [
                                archives.wedding,
                                archives.other,
                            ]
                        }
                    }),
                    new RoboHydraHeadStatic({
                        path: apiPrefix + '/capsule/',
                        content: {
                            meta: meta(2),
                            objects: [
                                capsules.Photos,
                                capsules.Stuff
                            ]
                        }
                    })
                ]
            },
        }
    };
};
