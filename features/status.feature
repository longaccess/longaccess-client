Feature: status command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the Longaccess directory exists in HOME
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the username "test" 
        And the password "test"
        And the API authenticates a test user
        And I store my credentials in "{homedir}/.netrc"

    Scenario: I poll a non existent archive
        Given the command line arguments "archive status 1"
        When I run console script "lacli"
        Then I see "No such archive"

    Scenario: I poll a not started upload
        Given the command line arguments "archive status 1"
        And I have 1 available archive
        When I run console script "lacli"
        Then I see "status: local"

    Scenario: I poll for an upload that is still pending
        Given I have 1 pending uploads
        And the command line arguments "archive status 1"
        When I run console script "lacli"
        Then I see "status: pending"

    Scenario: I poll for a upload that completed with an error
        Given I have 1 pending uploads
        And the upload status is "error"
        And the command line arguments "archive status 1"
        When I run console script "lacli"
        Then I see "status: error"

    Scenario: I poll for an upload that is completed
        Given I have 1 pending uploads
        And the upload status is "completed"
        And the command line arguments "archive status 1"
        When I run console script "lacli"
        Then I see "status: complete"
        And I see "Certificate [^ ]* saved"
        And there is a completed certificate
        And I see "Use lacli certificate list"
        And there are 0 pending uploads
