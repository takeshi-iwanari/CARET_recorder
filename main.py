import sys
import os
import subprocess
import pexpect
import time
import PySimpleGUI as sg

autoware_ecu_ip = '192.168.1.1'
trace_data_dir = '~/.ros/tracing'
caret_dir = '~/ros2_caret_ws'
dest_dir = '~/computing_ws/tracing'
user = 'my_user'
password = 'my_password'

layout = [
            [sg.Text('Connection'), sg.Checkbox('Local', key='-Local-', enable_events=True, default=True)],
            [sg.Text('IP Address: '), sg.Input(autoware_ecu_ip, key='-IP Address-', s=20)],
            [sg.Text('User: '), sg.Input(user, key='-User-', s=12),
             sg.Text('   Password: '), sg.Input(password, key='-Password-', s=12)],
            [sg.Button('Test')],
            [sg.HSep()],
            [sg.Text('Operation')],
            [sg.Text('CARET Dir: '), sg.Input(caret_dir, key='-CARET Dir-')],
            [sg.Button('Start Recording', key='-Record-'), sg.Text('REC (please stop recording before closing this app)', key='-Rec status-', text_color='RED', visible=False)],
            [sg.Button('Reset')],
            [sg.Button('Trace Data List')],
            [sg.Button('check_ctf'), sg.Input('', key='-trace_data-')],
            [sg.Button('trace_point_summary'), sg.Button('node_summary'), sg.Button('topic_summary')],
            [sg.Button('Copy to local'), sg.Input(dest_dir, key='-Dest Dir-')],
            [sg.Button('Clear All Trace Data')],
            [sg.HSep()],
            [sg.Multiline(size=(60,15), key='-Output-', expand_x=True, expand_y=True, write_only=True,
                          reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True, autoscroll=True,  auto_refresh=True)],
         ]

connection_keys = ['-IP Address-', '-User-', '-Password-', 'Test']

window = sg.Window('CARET Record', layout, resizable=True, finalize=True)

def _run_command(cmd: str):
    proc = subprocess.run([cmd], executable='/bin/bash', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    window['-Output-'].update(proc.stdout)

def run_command(cmd: str):
    proc = subprocess.Popen([cmd], executable='/bin/bash', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = ''
    while True:
        buf = proc.stdout.readline()
        if buf == '':
            break
        text += buf
        window['-Output-'].update(text)
        window.Refresh()
    return text


def caret_record(no_wait=False):
    caret_dir = window['-CARET Dir-'].Get()

    cmd = f'source /opt/ros/humble/setup.bash &&' + \
          f'source {caret_dir}/install/local_setup.bash &&' + \
          f'ros2 caret record -v'

    child = pexpect.spawn('/bin/bash', ['-c', cmd], logfile=sys.stdout, encoding='utf-8')
    time.sleep(0.1)
    child.sendline('')
    child.expect('press enter to stop')

    window['-Record-'].update('Stop Recording')
    window['-Rec status-'].update(visible=True)

    while True:
        time.sleep(0.01)
        if no_wait:
            event = '-Record-'
        else:
            event, values = window.read()
        if event == '-Record-':
            child.sendline('')
            child.expect('destroying tracing session')
            window['-Record-'].update('Start Recording')
            window['-Rec status-'].update(visible=False)
            break

def record():
    caret_record()


def reset():
    # todo: msg box to ask are you sure?
    cmd = 'ps aux | grep -e lttng -e "ros2 caret record" | grep -v grep | awk \'{ print "kill -9", $2 }\' | sh'
    run_command(cmd)
    cmd = 'rm -rf ~/.lttng'
    run_command(cmd)
    caret_record(True)


def trace_data_list():
    cmd = f'cd {trace_data_dir} && ls -rtd ./* | tail -n 1'
    latest_file = trace_data_dir + '/' + run_command(cmd)
    window['-trace_data-'].update(latest_file)

    cmd = f'du -sh {trace_data_dir}/*'
    run_command(cmd)

def copy_to_local():
    cmd = f'mkdir -p {dest_dir} &&' + \
          f'cd {trace_data_dir} &&' + \
          f'ls -d * | xargs -I[] tar czvf [].tgz [] &&' + \
          f'mv *.tgz {dest_dir}/.'
    run_command(cmd)


def main():

    for key in connection_keys:
        window[key].update(disabled=window['-Local-'].get())

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break

        if event == '-Local-':
            for key in connection_keys:
                window[key].update(disabled=values['-Local-'])
        elif event == '-Record-':
            record()
        elif event == 'Reset':
            reset()
        elif event == 'Trace Data List':
            trace_data_list()
        elif event == 'Copy to local':
            copy_to_local()
        elif event == 'Clear All Trace Data':
            copy_to_local()

    window.close()
    exit(0)


if __name__ == '__main__':
    main()
