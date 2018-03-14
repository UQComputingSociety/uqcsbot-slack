# Contributing to uqcsbot

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to uqcsbot. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by the [UQCS Code of Conduct](https://github.com/UQComputingSociety/code-of-conduct/blob/master/README.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [contact@uqcs.org.au](mailto:contact@uqcs.org.au).

## Got a Question or Problem?

If you would like to chat about the question in real-time, you can reach out via [our slack channel](https://uqcs.slack.com/).

## How Can I Contribute?

### Reporting Bugs

Bug reports are tracked as [GitHub issues](https://github.com/UQComputingSociety/uqcsbot/issues). When you are creating a bug report, please include as many details as possible about what the problem is and how to reproduce it. This helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer:, and find related reports :mag_right:. If an issue already exists for the bug, add any additional helpful details as a comment on that issue. Even better, you can [submit a Pull Request](#submit-pr) with a fix!

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/UQComputingSociety/uqcsbot/issues). When creating an enhancement issue, please provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include copy/pasteable snippets which you use in those examples, as [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Include screenshots and animated GIFs** which help you demonstrate the steps. You can use [this tool](https://www.cockos.com/licecap/) to record GIFs on macOS and Windows, and [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) on Linux.
* **Explain why this enhancement would be useful** to most users.

### Your First Code Contribution

Unsure where to begin contributing to uqcsbot? You can start by looking through these `beginner` and `help-wanted` issues:

* [Entry level issues](https://github.com/UQComputingSociety/uqcsbot/issues?q=is%3Aissue+is%3Aopen+label%3A%22entry+level%22) - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues](https://github.com/UQComputingSociety/uqcsbot/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) - issues which should be a bit more involved than `beginner` issues.

#### Local development

See the [README](README.md) for getting started on local development.

### <a name="submit-pr"></a> Pull Requests

1. Fork the UQComputingSociety/uqcsbot repo.
1. Make your changes in a new git branch:

     ```shell
     git checkout -b my-fix-branch
     ```

1. Create your patch, **including test cases where appropriate**.
1. Run the full test suite, as described in the [README](README.md),
  and ensure that all tests pass.
1. Commit your changes using a descriptive commit message.

     ```shell
     git add .
     git commit -m "descriptive message"
     ```

1. Push your branch to GitHub:

    ```shell
    git push origin my-fix-branch
    ```

1. In GitHub, send a pull request to `uqcsbot:python-rewrite`.
    * If we suggest changes then:
    * Make the required updates.
    * Re-run the test suite to ensure tests are still passing.

1. If the PR is a small addition, one approval should suffice before merging. Else for more complicated PRs, multiple approvals may be necessary.

That's it! Thank you for your contribution!

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :memo: `:memo:` when writing docs
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings

### Python Styleguide

All Python code must adhere to the [PEP-8 Styleguide](https://www.python.org/dev/peps/pep-0008/) as closely as possible.

## Additional Notes

This doc was adapted from the [Atom](https://github.com/atom/atom/blob/master/CONTRIBUTING.md) and [Angular](https://github.com/angular/angular/blob/master/CONTRIBUTING.md) Contributing documents.