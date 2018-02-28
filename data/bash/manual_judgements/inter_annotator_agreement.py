"""
Compute the inter-annotator agreement.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import csv
import sys

from bashlint import data_tools
from eval.eval_tools import load_cached_evaluations_from_file
from eval.eval_tools import get_example_nl_key, get_example_cm_key
from eval.eval_tools import normalize_judgement

def iaa(a1, a2):
    assert(len(a1) == len(a2))
    num_agree = 0
    for i in range(len(a1)):
        if a1[i].lower() == a2[i].lower():
            num_agree += 1
    return float(num_agree) / len(a1)

def read_annotations(input_file):
    command_judgements, template_judgements = [], []
    with open(input_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            command_eval = normalize_judgement(row['correct command'].strip())
            template_eval = normalize_judgement(row['correct template'].strip())
            command_judgements.append(command_eval)
            template_judgements.append(template_eval)
    return command_judgements, template_judgements

def inter_annotator_agreement(input_files1, input_files2):
    command_judgements1, template_judgements1 = [], []
    command_judgements2, template_judgements2 = [], []
    for input_file in input_files1:
        cj, tj = read_annotations(input_file)
        command_judgements1.extend(cj)
        template_judgements1.extend(tj)
    for input_file in input_files2:
        cj, tj = read_annotations(input_file)
        command_judgements2.extend(cj)
        template_judgements2.extend(tj)
    print('IAA-F: {}'.format(iaa(command_judgements1, command_judgements2)))
    print('IAA-T: {}'.format(iaa(template_judgements1, template_judgements2)))
    
def combine_annotations():
    """
    Combine the annotations input by three annotators.

    :param input_file1: main annotation file 1.
    :param input_file2: main annotation file 2 (should contain the same number of
        lines as input_file1).
    :param input_file3: supplementary annotation file which contains annotations
        of lines in input_file1 and input_file2 that contain a disagreement.
    :param output_file: file that contains the combined annotations.
    """
    input_file1 = sys.argv[1]
    input_file2 = sys.argv[2]
    input_file3 = sys.argv[3]
    output_file = sys.argv[4]
    o_f = open(output_file, 'w')
    o_f.write('description,prediction,template,correct template,correct command,'
              'correct template A,correct command A,'
              'correct template B,correct command B,'
              'correct template C,correct command C\n')
    sup_structure_eval, sup_command_eval = load_cached_evaluations_from_file(
        input_file3, treat_empty_as_correct=True)
    # for key in sup_structure_eval:
    #     print(key)
    # print('------------------')
    with open(input_file1) as f1:
        with open(input_file2) as f2:
            reader1 = csv.DictReader(f1)
            reader2 = csv.DictReader(f2)
            current_desp = ''
            for row1, row2 in zip(reader1, reader2):
                row1_template_eval = normalize_judgement(row1['correct template'].strip())
                row1_command_eval = normalize_judgement(row1['correct command'].strip())
                row2_template_eval = normalize_judgement(row2['correct template'].strip())
                row2_command_eval = normalize_judgement(row2['correct command'].strip())
                if row1['description']:
                    current_desp = row1['description'].strip()
                sc_key = get_example_nl_key(current_desp)
                pred_cmd = row1['prediction'].strip()
                if not pred_cmd:
                    row1_template_eval, row1_command_eval = 'n', 'n'
                    row2_template_eval, row2_command_eval = 'n', 'n'
                pred_cmd_key = get_example_cm_key(pred_cmd)
                pred_temp = data_tools.cmd2template(pred_cmd_key, loose_constraints=True)
                structure_example_key = '{}<NL_PREDICTION>{}'.format(sc_key, pred_temp)
                command_example_key = '{}<NL_PREDICTION>{}'.format(sc_key, pred_cmd_key)
                row3_template_eval, row3_command_eval = None, None
                if structure_example_key in sup_structure_eval:
                    row3_template_eval = sup_structure_eval[structure_example_key]
                if command_example_key in sup_command_eval:
                    row3_command_eval = sup_command_eval[command_example_key]
                if row1_template_eval != row2_template_eval or row1_command_eval != row2_command_eval:
                    if row1_template_eval != row2_template_eval:
                        if row3_template_eval is None:
                            print(structure_example_key)
                        assert(row3_template_eval is not None)
                        template_eval = row3_template_eval
                    else:
                        template_eval = row1_template_eval
                    if row1_command_eval != row2_command_eval:
                        # if row3_command_eval is None:
                        #     print(command_example_key)
                        assert(row3_command_eval is not None)
                        command_eval = row3_command_eval
                    else:
                        command_eval = row1_command_eval
                else:
                    template_eval = row1_template_eval
                    command_eval = row1_command_eval
                if row3_template_eval is None:
                    row3_template_eval = ''
                if row3_command_eval is None:
                    row3_command_eval = ''
                o_f.write('"{}","{}","{}",{},{},{},{},{},{},{},{}\n'.format(
                    current_desp.replace('"', '""'), pred_cmd.replace('"', '""'), pred_temp.replace('"', '""'),
                    template_eval, command_eval,
                    row1_template_eval, row1_command_eval,
                    row2_template_eval, row2_command_eval,
                    row3_template_eval, row3_command_eval))
    o_f.close()

def print_error_analysis_sheet():
    input_file1 = sys.argv[1]
    input_file2 = sys.argv[2]
    input_file3 = sys.argv[3]
    output_file = sys.argv[4]
    o_f = open(output_file, 'w')
    o_f.write('description,model,prediction,correct template,correct command,'
              'correct template A,correct command A,'
              'correct template B,correct command B,'
              'correct template C,correct command C\n')
    sup_structure_eval, sup_command_eval = load_cached_evaluations_from_file(
        input_file3, treat_empty_as_correct=True)
    # for key in sup_structure_eval:
    #     print(key)
    # print('------------------')
    with open(input_file1) as f1:
        with open(input_file2) as f2:
            reader1 = csv.DictReader(f1)
            reader2 = csv.DictReader(f2)
            current_desp = ''
            for row_id, (row1, row2) in enumerate(zip(reader1, reader2)):
                model_name = row2['model']
                if not model_name in ['partial.token-copynet', 'tellina']:
                    continue
                if row_id % 3 != 0:
                    continue
                row1_template_eval = normalize_judgement(row1['correct template'].strip())
                row1_command_eval = normalize_judgement(row1['correct command'].strip())
                row2_template_eval = normalize_judgement(row2['correct template'].strip())
                row2_command_eval = normalize_judgement(row2['correct command'].strip())
                if row1['description']:
                    current_desp = row1['description'].strip()
                sc_key = get_example_nl_key(current_desp)
                pred_cmd = row1['prediction'].strip()
                if not pred_cmd:
                    row1_template_eval, row1_command_eval = 'n', 'n'
                    row2_template_eval, row2_command_eval = 'n', 'n'
                pred_cmd_key = get_example_cm_key(pred_cmd)
                pred_temp = data_tools.cmd2template(pred_cmd_key, loose_constraints=True)
                structure_example_key = '{}<NL_PREDICTION>{}'.format(sc_key, pred_temp)
                command_example_key = '{}<NL_PREDICTION>{}'.format(sc_key, pred_cmd_key)
                row3_template_eval, row3_command_eval = None, None
                if structure_example_key in sup_structure_eval:
                    row3_template_eval = sup_structure_eval[structure_example_key]
                if command_example_key in sup_command_eval:
                    row3_command_eval = sup_command_eval[command_example_key]
                if row1_template_eval != row2_template_eval or row1_command_eval != row2_command_eval:
                    if row1_template_eval != row2_template_eval:
                        if row3_template_eval is None:
                            print(structure_example_key)
                        assert (row3_template_eval is not None)
                        template_eval = row3_template_eval
                    else:
                        template_eval = row1_template_eval
                    if row1_command_eval != row2_command_eval:
                        # if row3_command_eval is None:
                        #     print(command_example_key)
                        assert (row3_command_eval is not None)
                        command_eval = row3_command_eval
                    else:
                        command_eval = row1_command_eval
                else:
                    template_eval = row1_template_eval
                    command_eval = row1_command_eval
                if row3_template_eval is None:
                    row3_template_eval = ''
                if row3_command_eval is None:
                    row3_command_eval = ''
                o_f.write('"{}","{}","{}",{},{},{},{},{},{},{},{}\n'.format(
                    current_desp.replace('"', '""'), model_name, pred_cmd.replace('"', '""'),
                    template_eval, command_eval,
                    row1_template_eval, row1_command_eval,
                    row2_template_eval, row2_command_eval,
                    row3_template_eval, row3_command_eval))
    o_f.close()

def export_annotation_differences(input_file1, input_file2, output_file, command_header):
    o_f = open(output_file, 'w')
    o_f.write('description,{},correct template A,correct command A,correct template B,correct command B\n'.format(
        command_header))
    with open(input_file1) as f1:
        with open(input_file2) as f2:
            reader1 = csv.DictReader(f1)
            reader2 = csv.DictReader(f2)
            current_desp = ''
            desp_written = False
            for row1, row2 in zip(reader1, reader2):
                if row1['description']:
                    current_desp = row1['description']
                    desp_written = False
                if not row1[command_header]:
                    continue
                row1_template_eval = normalize_judgement(row1['correct template'].strip())
                row1_command_eval = normalize_judgement(row1['correct command'].strip())
                row2_template_eval = normalize_judgement(row2['correct template'].strip())
                row2_command_eval = normalize_judgement(row2['correct command'].strip())
                if (row1_template_eval != row2_template_eval) or \
                        (row1_command_eval != row2_command_eval):
                    if not desp_written:
                        o_f.write('"{}","{}",{},{},{},{}\n'.format(
                            current_desp.replace('"', '""'), row1[command_header].replace('"', '""'),
                            row1_template_eval, row1_command_eval, row2_template_eval, row2_command_eval))
                        desp_written = True
                    else:
                        o_f.write(',"{}",{},{},{},{}\n'.format(row1[command_header].replace('"', '""'),
                            row1_template_eval, row1_command_eval, row2_template_eval, row2_command_eval))
    o_f.close()

def main():
    print_error_analysis_sheet()
    # combine_annotations()
    # input_files1 = ['unreleased_files/manual.evaluations.test.stc.annotator.1.csv', 'unreleased_files/manual.evaluations.test.tellina.annotator.1.csv']
    # input_files2 = ['unreleased_files/manual.evaluations.test.stc.annotator.2.csv', 'unreleased_files/manual.evaluations.test.tellina.annotator.2.csv']
    # input_files1 = ['unreleased_files/NL-Cmd Judgement (Hamid) - pc.csv', 'unreleased_files/NL-Cmd Judgement (Hamid) - tellina.csv']
    # input_files2 = ['unreleased_files/NL-Cmd Judgement (Shridhar) - pc.csv', 'unreleased_files/NL-Cmd Judgement (Shridhar) - tellina.csv']
    # input_files1 = ['unreleased_files/manual.evaluations.dev.samples.annotator.1.csv']
    # input_files2 = ['unreleased_files/manual.evaluations.dev.samples.annotator.2.csv']
    # inter_annotator_agreement(input_files1, input_files2)

if __name__ == '__main__':
    main()