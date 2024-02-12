# check-stacks

A simple little script that will iterate all accounts and find stacks, creating a CSV report.

Entirely meaningless outside GOV.UK One Login.

To use:

- `pip3 install boto3`
- run `./main.py`
- you'll be prompted to log in and authorize the application in AWS Identity Center
- a few minutes later, stacks.csv will appear, with all that juicy data goodness

Enjoy, I guess?

## Environment Variables

### ROLE_FILTER (default: readonly)
- allows basic pattern matching (if role_filter in role_name) to that you can set 
  the role name to use, or roles containing `support` or `readonly`