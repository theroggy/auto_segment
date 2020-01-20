# -*- coding: utf-8 -*-
"""
Process the tasks as configured in the run_tasks_config.csv file.
"""

from email.message import EmailMessage
import json
import logging
import logging.config
import os
import smtplib

import pandas as pd

def run_tasks():

    ##### Init #####
    run_local = True

    # Init logging
    with open('bin/taskrunner_logconfig.json', 'r') as log_config_file:
        log_config_dict = json.load(log_config_file)
    logging.config.dictConfig(log_config_dict)
    global logger
    logger = logging.getLogger()

    # Prepare the path to the dir where the config can be found,...
    script_dir = os.path.dirname(os.path.abspath(__file__))
    run_config_filepath = os.path.join(script_dir, "taskrunner_tasks.csv")

    # Read the tasks that need to be ran in the run_tasks file
    run_config_df = read_run_tasks_config(run_config_filepath)

    # Loop over tasks to run
    for run_info in run_config_df.itertuples(): 
        if(run_info.active == 0):
            continue

        if run_local:
            # Run local (possible to debug,...)
            if run_info.command == 'bin/run_orthoseg.py':
                try:                 
                    import run_orthoseg as run_orthoseg
                    run_orthoseg.orthoseg_argstr(run_info.argumentstring)
                    sendmail(f"Completed task {run_info.command} {run_info.argumentstring}")
                except Exception as ex:
                    message = f"ERROR in task {run_info.command} {run_info.argumentstring}"
                    sendmail(subject=message, body=f"Exception: {ex}")
                    raise Exception(message) from ex
            else:
                raise Exception(f"Unknown command: {run_info.command}")
        else:
            # Run the tasks by command
            # TODO: support running on remote machine over ssh?
            try:
                # TODO: make the running script cancellable?
                # Remark: this path will depend on the python environment the task 
                # needs to run in
                python_path = r"C:\Tools\anaconda3\envs\orthoseg\python.exe"
                fullcommand = f"{python_path} {run_info.command} {run_info.argumentstring}"
                returncode = os.system(fullcommand)
                if returncode == 0:
                    sendmail(f"Completed task {run_info.command} {run_info.argumentstring}")
                else:
                    raise Exception(f"Error: returncode: {returncode} returned for {fullcommand}")

            except Exception as ex:
                message = f"ERROR in task {run_info.command} {run_info.argumentstring}"
                sendmail(subject=message, body=f"Exception: {ex}")
                raise Exception(message) from ex

def read_run_tasks_config(filepath):
    
    # Read
    run_config_df = pd.read_csv(filepath)

    # Trim column names and string columns
    for column in run_config_df.columns:
        column_stripped = column.strip()
        if column != column_stripped:
            run_config_df.rename(columns={column:column_stripped}, inplace=True)
        if run_config_df[column_stripped].dtype in ('str', 'object'):
            run_config_df[column_stripped] = run_config_df[column_stripped].astype(str).str.strip()

    # Check mandatory columns
    mandatory_columns = ['command', 'active', 'argumentstring']
    missing_columns = set(mandatory_columns).difference(set(run_config_df.columns))
    if(len(missing_columns) > 0):
        raise Exception(f"Missing column(s) in {filepath}: {missing_columns}")
    
    return run_config_df

def sendmail(
        subject: str, 
        body: str = None,
        stop_on_error: bool = False):

    try:
        # Create message
        # TODO: email adress shouldn't be hardcoded... I suppose
        msg = EmailMessage()
        msg.add_header('from', 'pieter.roggemans@lv.vlaanderen.be')
        msg.add_header('to', 'pieter.roggemans@lv.vlaanderen.be')
        msg.add_header('subject', subject)
        if body is not None:
            msg.set_payload(body)

        # Send the email
        server = smtplib.SMTP('mail.dg3.be')
        #server.login("MrDoe", "PASSWORD")
        server.send_message(msg)
        server.quit()
    except Exception as ex:
        if stop_on_error is False:
            logger.exception("Error sending email")
        else:
            raise Exception("Error sending email") from ex
        
if __name__ == '__main__':
    run_tasks()
