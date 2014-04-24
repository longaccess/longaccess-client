Feature: list archives command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the Longaccess directory exists in HOME
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the username "test" 
        And the password "test"
        And the API authenticates a test user

    Scenario: I list archives without having any
        Given I store my credentials in "{homedir}/.netrc"
        And the command line arguments "capsule archives"
        When I run console script "lacli"
        Then I see "No available archives."

    Scenario: I try to list archives with bad credentials
        Given the API authentication is wrong
        And I store my credentials in "{homedir}/.netrc"
        And the command line arguments "capsule archives"
        When I run console script "lacli"
        Then I see "error: authentication failed"

    Scenario: I list archives without credentials
        Given the command line arguments "capsule archives"
        When I run console script "lacli"
        Then I see "Username"
        When I type "test"
        Then I see "Password: "
        When I type "test"
        Then I see "Save credentials?"
        When I type "no"
        Then I see "No available archives."

    Scenario: I list archives without credentials 2
        Given the command line arguments "capsule archives"
        When I run console script "lacli"
        Then I see "Username"
        When I type "test"
        Then I see "Password: "
        When I type "wtf"
        Then I see "authentication failed"

    Scenario: I list archives
        Given the command line arguments "capsule archives"
        And I store my credentials in "{homedir}/.netrc"
        And I have 1 capsule
        And I have 2 uploaded archives
        When I run console script "lacli"
        Then I see "TITLE"
        And I see "My wedding"
        And I see "CAPSULE"
        And I see "Photos"

    Scenario: I list archives of specific capsule
        Given the command line arguments "capsule archives 1"
        And I store my credentials in "{homedir}/.netrc"
        And I have 1 capsule
        And I have 2 uploaded archives
        When I run console script "lacli"
        Then I see "TITLE"
        And I see "My wedding"
        And I see "CAPSULE"
        And I see "Photos"

    Scenario: I list archives of specific capsule with no archives
        Given the command line arguments "capsule archives 2"
        And I store my credentials in "{homedir}/.netrc"
        And I have 1 capsule
        And I have 2 uploaded archives
        When I run console script "lacli"
        Then I see "No available archives"

    Scenario: I list archives of nonexistent capsule
        Given the command line arguments "capsule archives 3"
        And I store my credentials in "{homedir}/.netrc"
        And I have 1 capsule
        When I run console script "lacli"
        Then I see "No such capsule"

    Scenario: I list archives without netrc auth
        Given the command line arguments "-u test -p test capsule archives"
        And I have 1 capsule
        And I have 2 uploaded archives
        When I run console script "lacli"
        Then I see "TITLE"
        And I see "My wedding"
        And I see "CAPSULE"
        And I see "Photos"
