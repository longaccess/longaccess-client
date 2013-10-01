Feature: list capsules command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the username "testuser" 
        And the password "testpass"

    Scenario: I list capsules without having any
        Given I store my credentials in "{homedir}/.netrc"
        And the command line arguments "list"
        When I run console script "lacli"
        Then I see "No available capsules."

    Scenario: I list capsules
        Given I store my credentials in "{homedir}/.netrc"
        And the command line arguments "list"
        And I have 1 capsule
        When I run console script "lacli"
        Then I see "Available capsules:"

    Scenario: I list capsules without netrc auth
        Given the command line arguments "list -u {username} -p {password}"
        And I have 1 capsule
        When I run console script "lacli"
        Then I see "Available capsules:"
