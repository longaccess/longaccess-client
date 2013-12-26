Longaccess client options
=========================

`user`
------

The username

### Default 

the saved username or None)

`pass`
------


The password.

### Default

the saved password or None

`url`
-----

The API URL.

### Default

`https://www.longaccess.com/api/v1/

`verify`
--------

Toggle verification of SSL certificate for API calls

### Default

True

`debug`
-------

Integer to disable or enable debugging features, e.g. extra messages or non-forking workers. Higher values enable more features.

### Default

0 (i.e. no debugging)

`home`
------

Where to store the cache (archives, certificates, etc.)

### Default

`~/Longaccess`

`nprocs`
--------

Number of parallel uploading processes.

### Default

Number of processing cores minus one.

