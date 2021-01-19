# Console Latest Build Static HTML Script
#
# Generates the static HTML version of the newsletter from the interesting
# tools and beta programs JSON provided as input. Designed to be run as part
# of a build process.

import argparse
import json
from datetime import date

import jinja2
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta, TH

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument('--tools-json', help='Path to the file containing the'
                    ' interesting tools list as a JSON object', required=True)
parser.add_argument('--beta-json', help='Path to the file containing the beta'
                    ' list as a JSON object', required=True)
parser.add_argument('--template', help='Path to the file containing the table'
                    ' template within the templates/ directory', required=True)
parser.add_argument('--output', help='Path to the location of the output file'
                    ' (will be created if it does not exist, overwritten if it'
                    ' does)', required=True)
args = parser.parse_args()

print('Starting build')

# Get last Thursday
today = date.today()
last_thursday = today - relativedelta(weekday=TH(-1))

# Open and parse the JSON file to get the list of beta programs.
# See example-beta-list.json for what this should look like.
# It will be generated as part of the build steps using the GitHub
# gsheet.action from the Beta Programs Google Sheet (see README.md).
print('Loading beta JSON...')

programs = []

with open(args.beta_json, 'r') as f:
    betas = json.load(f)

    for program in betas['results'][0]['result']['formatted']:
        if program['Scheduled for'] == "":
            continue

        scheduled_for = parse(program['Scheduled for'])

        # Only pull out things scheduled for the last newsletter
        if scheduled_for.isocalendar() == last_thursday.isocalendar():
            programs.append(program)

    print('Loaded beta JSON')

# Load the template file, providing the list for it to loop through
print('Rendering template...')
template_loader = jinja2.FileSystemLoader(searchpath='templates')
template_env = jinja2.Environment(loader=template_loader, autoescape=True)
template = template_env.get_template(args.template)
rendered = template.render(betas=programs)
print('Rendered template')

# Output the rendered template
print('Outputting template')
output = open(args.output, "w")
output.write(rendered)
output.close()
print('Output template')

print('Build table complete')
