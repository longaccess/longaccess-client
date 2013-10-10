Feature: restore command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"

    Scenario: I restore without having any available archives
        Given the command line arguments "restore"
        When I run console script "lacli"
        Then I see "No such archive."

    Scenario: I restore without having any available archives
        Given the command line arguments "restore -o /tmp"
        When I run console script "lacli"
        Then I see "No such archive."

    Scenario: I restore a non existent
        Given the command line arguments "restore 1"
        When I run console script "lacli"
        Then I see "No such archive."

    Scenario: I restore an empty archive
        Given an empty folder "foo"
        And the command line arguments "archive {foo}"
        When I run console script "lacli"
        Then I see "archive prepared"
        Given the command line arguments "restore"
        When I run console script "lacli"
        Then I see "archive restored"
