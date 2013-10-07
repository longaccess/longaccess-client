Feature: prepare archive command

    Background: setup the command configuration
        Given the home directory is "/tmp/test"

    Scenario: I list prepared archives without having any
        Given the command line arguments "archive"
        When I run console script "lacli"
        Then I see "No prepared archives."

    Scenario: I list prepared archives
        Given the command line arguments "archive"
        And I have 1 prepared archive titled "foo"
        When I run console script "lacli"
        Then I see "Prepared archives:"

    Scenario: I list prepared archives with title
        Given the command line arguments "archive"
        And I have 1 prepared archive titled "foo"
        When I run console script "lacli"
        Then I see "Prepared archives:"
        And I see "1) foo"

    Scenario: I prepare a new archive but give a non-existent directory
        Given the command line arguments "archive doesnotexistdir"
        When I run console script "lacli"
        Then I see "The specified folder does not exist"

