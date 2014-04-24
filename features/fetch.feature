Feature: fetch certificate command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the Longaccess directory exists in HOME
        And the mock API "longaccessmock"
        And the environment variable "LA_API_URL" is "{api_url}path/to/api"
        And the username "test" 
        And the password "test"
        And the API authenticates a test user

    Scenario: I import a certificate by fetching
        Given the command line arguments "fetch FOOKEY1"
        And I store my credentials in "{homedir}/.netrc"
        And I have 2 uploaded archives
        When I run console script "lacli"
        Then I see "photos from my wedding"
        Then I see "Type the decryption key"
        When I type "DEADBEEFDEADBEEF"
        And I type "DEADBEEFDEADBEEF"
        And I type "DEADBEEFDEADBEEF"
        And I type "DEADBEEFDEADBEEF"
        Then I see "key valid"
        When I type " "
        Then I see "Fetched certificate FOOKEY1"

    Scenario: I import a certificate by fetching with key
        Given the command line arguments "fetch FOOKEY1 DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF"
        And I store my credentials in "{homedir}/.netrc"
        And I have 2 uploaded archives
        When I run console script "lacli"
        Then I see "photos from my wedding"
        And I see "Fetched certificate FOOKEY1"
