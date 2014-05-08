Feature: resume upload feature

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the Longaccess directory exists in HOME
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the username "test" 
        And the password "test"
        And I have 2 capsules
        And I store my credentials in "{homedir}/.netrc"

    @dev
    Scenario: I pause an archive
        Given the command line arguments "archive create -t foobar lacli"
        And an S3 bucket named "foobucket"
        When I run console script "lacli"
        Then I wait 10 seconds to see "archive prepared"
        Given the command line arguments "archive upload"
        When I run console script "lacli"
        Then I see "ETA:"
        When I send control-c
        And I wait until I don't see "ETA:" anymore
        Then I see "paused"

    Scenario: I resume an archive
        Given I have 1 pending uploads
        And an S3 bucket named "foobucket"
        Given the command line arguments "-d 4 archive upload"
        When I run console script "lacli"
        Then I see "ETA:"
        When the upload status is "completed"
        Then I wait 5 seconds to see "done."
