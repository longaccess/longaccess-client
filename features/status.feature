Feature: status command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"

    Scenario: I status without having any pending uploads
        Given the command line arguments "status"
        When I run console script "lacli"
        Then I see "No pending uploads."

    Scenario: I poll a non existent status
        Given the command line arguments "status 1"
        When I run console script "lacli"
        Then I see "No such upload pending."

    Scenario: I poll for an upload that doesn't exist
        Given I have 2 pending uploads
        And the command line arguments "status 3"
        When I run console script "lacli"
        Then I see "No such upload pending."

    Scenario: I status with a pending upload
        Given I have 1 pending uploads
        And the command line arguments "status"
        When I run console script "lacli"
        Then I see "Pending uploads:"
        And I see "1) upload"

    Scenario: I poll for an upload that is still pending
        Given I have 1 pending uploads
        And the command line arguments "status 1"
        When I run console script "lacli"
        Then I see "status: pending"

    Scenario: I poll for a upload that completed with an error
        Given I have 1 pending uploads
        And the upload status is "error"
        And the command line arguments "status 1"
        When I run console script "lacli"
        Then I see "status: error"

    Scenario: I poll for an upload that is completed
        Given I have 1 pending uploads
        And the upload status is "completed"
        And the command line arguments "status 1"
        When I run console script "lacli"
        Then I see "status: complete"
        And there is a completed certificate
        And there are 0 pending uploads
        And I see "Certificate:"
        And I see "!archive"
