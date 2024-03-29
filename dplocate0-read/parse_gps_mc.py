#!/usr/bin/env python

import os
import sys
import pandas as pd
import logging
import argparse as ap
from importlib import import_module

logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    argparser = ap.ArgumentParser('PHOENIX wrapper for GPS parse_gps_mc Pipeline',
        formatter_class= ap.ArgumentDefaultsHelpFormatter)

    # Input and output parameters
    argparser.add_argument('--phoenix-dir',
        help='Phoenix directory',
        required=True)
    argparser.add_argument('--consent-dir',
        help='Consent directory',
        required=True)
    argparser.add_argument('--matlab-dir',
        help='Matlab directory',
        required=True)

    argparser.add_argument('--pipeline',
        help='Name of the pipeline to run',
        default='parse_gps_mc')
    argparser.add_argument('--data-type',
        help='Data type name',
        default='phone')
    argparser.add_argument('--data-dir',
        help='Data directory name',
        default='PROTECTED')
    argparser.add_argument('--phone-stream',
        help='Required if data-type is "phone"',
        default='gps')
    argparser.add_argument('--output-dir',
        help='Path to the output directory')
    argparser.add_argument('--study', 
        help='Study name. Please provide one value.',
        required=True)
    argparser.add_argument('--subject',
        nargs='+', help='Subject ID')

    # Basic targeting parameters
    argparser.add_argument('--input-tz',
        help='Timezone info for the input',
        default = 'UTC')
    argparser.add_argument('--day-from',
        help='Output day from',
        type = int, default = 1)
    argparser.add_argument('--day-to',
        help='Output day to',
        type = int, default = -1)
    argparser.add_argument('--extension',
        help='File extension of gps files',
        default='.csv.lock')
    argparser.add_argument('--include',
        help='All subjects or only the active ones',
        default='all')

    args = argparser.parse_args()

    mod = get_module(args.pipeline)
    default_path = os.path.join(args.phoenix_dir, args.data_dir)

    # Gets all studies under each subdirectory
    studies = [ args.study ]
    for study in studies:
        study_path = os.path.join(default_path, study)
        consent_path = os.path.join(args.consent_dir, study, study + '_metadata.csv')
        consents = get_consents(consent_path)
        actives = get_actives(consent_path)

        # Gets all subjects under the study directory
        subjects = args.subject if args.subject else scan_dir(study_path)
        for subject in subjects:
            subject_path = os.path.join(study_path, subject)

            verified = verify_subject(subject, subject_path, consents)
            if not verified:
                continue
            
            if args.include=='active':
                verified2 = verify_active(subject, subject_path, actives)
                if not verified2:
                    continue

            logger.info('Processing {S} in {ST}'.format(S=subject, ST=study))
            date_from = consents[subject][0]

            data_path = os.path.join(subject_path, args.data_type, 'raw')
            output_path = args.output_dir if args.output_dir else os.path.join(subject_path,
                args.data_type,
                'processed')
            if args.data_type == 'phone':
                mod_parser = mod.parse_args()
                new_args, unknown = mod_parser.parse_known_args([
                    '--date-from', str(date_from),
                    '--read-dir', str(data_path),
                    '--filter-dir', "", str(args.phone_stream),
                    '--output-dir', output_path,
                    '--day-from', str(args.day_from),
                    '--day-to', str(args.day_to),
                    '--input-tz', str(args.input_tz),
                    '--study', str(study),
                    '--subject', str(subject),
                    '--matlab-dir', str(args.matlab_dir),
                    '--extension', str(args.extension)
                ])
                mod.main(new_args)
            else:
                mod_parser = mod.parse_args()
                new_args, unknown = mod_parser.parse_known_args([
                    '--date-from', str(date_from),
                    '--read-dir', str(data_path),
                    '--output-dir', str(output_path),
                    '--day-from', str(args.day_from),
                    '--day-to', str(args.day_to),
                    '--input-tz', str(args.input_tz),
                    '--study', str(study),
                    '--subject', str(subject),
                    '--matlab-dir', str(args.matlab_dir),
                    '--extension', str(args.extension)
                ])
                mod.main(new_args)
    return

# Import module based on user input
def get_module(pipeline):
    try:
        return import_module('{P}'.format(P=pipeline), __name__)
    except Exception as e:
        logger.error(e)
        logger.error('Could not import the pipeline module. Exiting')
        sys.exit(1)

# Ensures data can be processed for the subject
def verify_subject(subject, path, consents):
    # Ensures the subject directory is not the consent directory
    if subject.endswith('.csv'):
        logger.error('Subject {S} is not a valid subject.'.format(S=subject))
        return False

    if not os.path.isdir(path):
        logger.error('Path {P} does not exist.'.format(P=path))
        return False

    if not subject in consents:
        logger.error('Consent date does not exist for {S}.'.format(S=subject))
        return False

    return True

# Get consents for the study
def get_consents(path):
    try:
        df = pd.read_csv(path, keep_default_na=False, dtype={'Subject ID': 'str'}, engine='c', skipinitialspace=True)
        df = df.pivot(
            index='Study',
            columns='Subject ID',
            values='Consent'
        ).reset_index()
        return df
    except Exception as e:
        logger.error(e)
        return None


# Ensures the subject is active
def verify_active(subject, path, actives):
    if actives[subject][0]==0:
        logger.error('Subject {S} is not active anymore.'.format(S=subject))
        return False

    return True

# Get actives of the study
def get_actives(path):
    try:
        df = pd.read_csv(path, keep_default_na=False, dtype={'Subject ID': 'str'}, engine='c', skipinitialspace=True)
        df = df.pivot(
            index='Study',
            columns='Subject ID',
            values='Active'
        ).reset_index()
        return df
    except Exception as e:
        logger.error(e)
        return None

# Check if a directory is valid, then return its child directories 
def scan_dir(path):
    if os.path.isdir(path):
        try:
            return os.listdir(path)
        except Exception as e:
            logger.error(e)
            return []
    else:
        return []

if __name__ == '__main__':
    main()
