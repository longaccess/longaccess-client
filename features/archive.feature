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

    Scenario: I prepare a new archive with an empty directory
        Given an empty folder "foo"
        And the command line arguments "archive {foo}"
        When I run console script "lacli"
        Then I see "archive prepared"

    Scenario: I prepare a new archive with an empty directory and title
        Given an empty folder "foo"
        And the command line arguments "archive -t foo {foo}"
        When I run console script "lacli"
        Then I see "archive prepared"
        And there is a prepared archive titled "foo"

    Scenario: I prepare a new archive but it fails due to unreadable files
        Given an empty folder "foo"
        And under "{foo}" an empty file "bar"
        And file "{bar}" is unreadable
        And the command line arguments "archive -t foo {foo}"
        When I run console script "lacli"
        Then I see "error: "

    Scenario: I prepare a new archive but it fails due to unwritable files
        Given an empty folder "foo"
        And an empty folder "bar"
        And directory "{bar}" is unwritable
        And the command line arguments "archive --home {bar} -t foo {foo}"
        When I run console script "lacli"
        Then I see "error: "
