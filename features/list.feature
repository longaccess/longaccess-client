Feature: list capsules command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the Longaccess directory exists in HOME
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the username "test" 
        And the password "test"
        And the API authenticates a test user

    Scenario: I list capsules without having any
        Given I store my credentials in "{homedir}/.netrc"
        And the command line arguments "capsule list"
        When I run console script "lacli"
        Then I see "No available capsules."

    Scenario: I try to list capsules with bad credentials
        Given the API authentication is wrong
        And I store my credentials in "{homedir}/.netrc"
        And the command line arguments "capsule list"
        When I run console script "lacli"
        Then I see "error: authentication failed"

    Scenario: I list capsules without credentials
        Given the command line arguments "capsule list"
        When I run console script "lacli"
        Then I see "Username"
        When I type "test"
        Then I see "Password: "
        When I type "test"
        Then I see "Save credentials?"
        When I type "no"
        Then I see "No available capsules."

    Scenario: I list capsules without credentials 2
        Given the command line arguments "capsule list"
        When I run console script "lacli"
        Then I see "Username"
        When I type "test"
        Then I see "Password: "
        When I type "wtf"
        Then I see "authentication failed"

    Scenario: I list capsules
        Given the command line arguments "capsule list"
        And I store my credentials in "{homedir}/.netrc"
        And I have 1 capsule
        When I run console script "lacli"
        And I see "SIZE"
        And I see "FREE"
        Then I see "TITLE"
        And I see "Photos"

    Scenario: I list capsules without netrc auth
        Given the command line arguments "-u test -p test capsule list"
        And I have 1 capsule
        When I run console script "lacli"
        And I see "SIZE"
        And I see "FREE"
        Then I see "TITLE"
        And I see "Photos"
