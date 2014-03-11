@dev
Feature: restore command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"
        And the Longaccess directory exists in HOME

    Scenario: I restore without having any available archives
        Given the command line arguments "archive restore"
        When I run console script "lacli"
        Then I see "No such archive."

    Scenario: I restore without having any available archives
        Given the command line arguments "archive restore -o /tmp"
        When I run console script "lacli"
        Then I see "No such archive."

    Scenario: I restore a non existent
        Given the command line arguments "archive restore 1"
        When I run console script "lacli"
        Then I see "No such archive."

    Scenario: I restore an archive with no cert
        Given I have 1 available archive titled "foo"
        And the command line arguments "archive restore"
        When I run console script "lacli"
        Then I see "no matching certificate found"

    Scenario: I restore an archive with no local copy
        Given I have 1 available archive titled "foo"
        And I have a certificate for the archive with title "foo"
        And the command line arguments "archive restore"
        When I run console script "lacli"
        Then I see "no local copy exists"

    Scenario: I restore an archive with missing file
        Given I have 1 available archive titled "foo"
        And I have a certificate for the archive with title "foo"
        And the archive titled "foo" has a link to a local copy
        And the command line arguments "archive restore"
        When I run console script "lacli"
        Then I see "No such file or directory"

    Scenario: I restore an archive with empty copy
        Given I have 1 available archive titled "foo"
        And I have a certificate for the archive with title "foo"
        And the archive titled "foo" has a link to a local copy
        And the local copy for "foo" is an empty file
        And the command line arguments "archive restore"
        When I run console script "lacli"
        Then I see "error: File is not a zip file"

    Scenario: I restore an empty archive with one file in it
        Given an empty folder "foo"
        And under "{foo}" an empty file "test"
        And I have downloaded an archive containing "{foo}"
        And an empty folder "bar"
        And the command line arguments "archive restore -o {bar}"
        When I run console script "lacli"
        Then I see "archive restored"
        And there is a file "{test}" under "{foo}" 
