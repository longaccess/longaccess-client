Feature: list capsules command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the username "test" 
        And the password "test"
        And I store my credentials in "{homedir}/.netrc"
        And the API authenticates a test user

    Scenario: I list capsules without having any
        And the command line arguments "capsule list"
        When I run console script "lacli"
        Then I see "No available capsules."

    Scenario: I try to list capsules with bad credentials
        Given the API authentication is wrong
        And the command line arguments "capsule list"
        When I run console script "lacli"
        Then I see "error: authentication failed"

    Scenario: I list capsules
        Given the command line arguments "capsule list"
        And I have 1 capsule
        When I run console script "lacli"
        Then I see "Available capsules:"
        And I see "title"
        And I see "size"
        And I see "remaining"

    Scenario: I list capsules without netrc auth
        Given the command line arguments "-u test -p test capsule list"
        And I have 1 capsule
        When I run console script "lacli"
        Then I see "Available capsules:"
