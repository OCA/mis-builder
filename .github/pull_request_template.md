Thanks for your pull request. Please take a moment to review if it meets the following
guidelines.

## Description

Before coding, it is recommended to create an issue to discuss the problem or feature
you want to add. If you did not, don't worry, we can discuss on the PR too.

If there is a pre-existing issue that your PR implements or fixes, add a pointer to it
in the PR description.

If your PR is simple enough that it does not require a preliminary discussion, then make
sure to explain what it does (i.e. _why_ the change is necessary).

## Test

Don't forget to add unit tests. If your PR fixes a bug, prefer creating a separate
commit for the test so we one see that your test reproduces the bug and is fixed by the
PR.

## Target branch

MIS Builder is actively maintained for Odoo versions 9, 10, 11 and 12.

If your feature is applicable with the same implementation to all these versions, please
target branch 10.0. Maintainers will port it to 9, 11 and 12 soon after merging.

In the rare cases your feature or implementation is specific to an Odoo version, then
target the corresponding branch.

## CLA

Have you signed the OCA Contributor License Agreement? If not, please visit
https://odoo-community.org/page/cla to learn how.

## Changelog entry

This projects uses [towncrier](https://pypi.org/project/towncrier/) to generate it's
changelog. Make sure your PR includes a changelog entry in
`<addon>/readme/newsfragments/`. It must have the issue or PR number as name, and one of
`.feature`, `.bugfix`, `.doc` (for documentation improvements), `.misc` (if a ticket has
been closed, but it is not of interest to users). The changelog entry must be reasonably
short and phrased in a way that is understandable by end users.

## Documentation

Consider improving the documention in `docs/`.
