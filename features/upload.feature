Feature: upload command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the Longaccess directory exists in HOME
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the environment variable "LA_BATCH_OPERATION" is "1"
        And an S3 bucket named "lastage"

    Scenario: I try an upload without files
        Given the command line arguments "archive upload"
        When I run console script "lacli"
        Then I see "no such archive"

    Scenario: I upload an archive with no local copy
        Given I have 1 available archive titled "foo"
        And I have a certificate for the archive with title "foo"
        And the command line arguments "archive upload"
        When I run console script "lacli"
        Then I see "no local copy exists"

    Scenario: I upload an archive with missing file
        Given I have 1 available archive titled "foo"
        And I have a certificate for the archive with title "foo"
        And the archive titled "foo" has a link to a local copy
        And the command line arguments "archive upload"
        When I run console script "lacli"
        Then I see "File /tmp/test/Longaccess/data/test not found"

    Scenario: I upload an archive with empty copy
        Given I have 1 available archive titled "foo"
        And I have a certificate for the archive with title "foo"
        And the archive titled "foo" has a link to a local copy
        And the local copy for "foo" is an empty file
        And the command line arguments "archive upload"
        When I run console script "lacli"
        Then I see "error: File is not a zip file"

    Scenario: I upload an empty file to an incorrect API url
        Given I prepare an archive with a file "test"
        And the command line arguments "archive upload 1"
        And the environment variable "LA_API_URL" is "http://stage.longaccess.com/foobar"
        When I run console script "lacli"
        Then I see "error: server not found" 

    Scenario: I upload an empty file to a failing API
        Given I prepare an archive with a file "test"
        And the command line arguments "archive upload"
        And the API is failing
        When I run console script "lacli"
        Then I see "error: the server couldn't fulfill your request"

    Scenario: I upload an non-existent archive
        Given the command line arguments "archive upload 1234234234"
        When I run console script "lacli"
        Then I see "no such archive"

    Scenario: I upload an archive
        Given I prepare an archive with a file "test"
        And the command line arguments "archive upload"
        When I run console script "lacli"
        Then I see "ETA:"
        And I see "done"

    @dev
    Scenario: I upload a big archive
        Given the command line arguments "archive create /usr/include"
        And the timeout is 4000 seconds
        When I run console script "lacli"
        Then I see "archive prepared"
        Given the command line arguments "archive upload"
        When I run console script "lacli"
        Then I see "ETA:"
        And I wait until I don't see "ETA:" anymore
        And I see "done"
