import sys
import os
import subprocess
import pexpect
from pexpect import pxssh
import time
import PySimpleGUI as sg


class Value():
    is_local = True
    autoware_ecu_ip = '192.168.1.1'
    user = 'my_user'
    password = 'my_password'
    timeout_check = 600
    caret_dir = '~/ros2_caret_ws'
    app_dir = '~/autoware'
    record_frequency = 10000
    record_light = True,
    trace_data_dir = '~/.ros/tracing'
    copy_dir = '~/computing_ws/tracing'


class Gui():
    key_cb_local = '-local-'
    key_input_ip = '-IP Address-'
    key_input_user = '-user-'
    key_input_password = '-password-'
    key_input_timeout_check = '-timeout_check-'
    key_btn_test = '-test-'
    key_text_test = '-test_text-'
    key_input_caret_dir = '-CARET dir-'
    key_input_app_dir = '-App dir-'
    key_btn_check_build = '-check build-'
    key_btn_record = '-record-'
    key_text_record = '-record_text-'
    key_input_freq = '-freq-'
    key_cb_light = '-light-'
    key_btn_reset = '-reset-'
    key_btn_list = '-trace_data_list-'
    key_btn_check_lost = '-check_lost-'
    key_btn_check_ctf = '-check_ctf-'
    key_btn_trace_point_summary = '-trace_point_summary-'
    key_btn_node_summary = '-node_summary-'
    key_btn_topic_summary = '-topic_summary-'
    key_btn_copy = '-copy-'
    key_combo_target_trace_data = '-target_trace_data-'
    key_btn_upload = '-upload-'
    key_btn_remove = '-remove-'
    key_btn_remove_copy = '-remove_copy-'
    key_cb_copy_today = '-copy_today-'
    key_input_copy_dir = '-copy_dir-'
    key_text_output = '-output-'
    key_text_executing_cmd = '-executing_cmd-'

    tooltip_record = 'Please avoid start/stop recording while a target application is starting/stopping. Please stop recording before re-launch a target application.'
    tooltip_reset = 'Click in case recording can\'t be started or trace data file size is too small.'
    tooltip_list = 'Click before checking.\nData size will be around 1M ~ 1.5M Byte / sec.\nIf data size is extremely small, click "Reset" and check settings.'
    tooltip_trace_data_dir = 'trace data to be checked'
    tooltip_copy_dir = 'destination directory in local PC'

    sg.theme('dark')
    layout = [
                [sg.Text('Connection'),
                sg.Checkbox('Local', key=key_cb_local, default=Value.is_local, enable_events=True)],
                [sg.Text('IP Address:'),
                sg.Input(Value.autoware_ecu_ip, key=key_input_ip, s=20, enable_events=True)],
                [sg.Text('User:'),
                sg.Input(Value.user, key=key_input_user, s=12, enable_events=True),
                sg.Text('   Password:'),
                sg.Input(Value.password, key=key_input_password, password_char='*', s=12, enable_events=True)],
                [sg.Text('Timeout for check command:'),
                sg.Input(Value.timeout_check, key=key_input_timeout_check, s=12, enable_events=True)],
                [sg.Button('Test Connection', key=key_btn_test),
                sg.Text('', key=key_text_test)],
                [sg.HSep()],
                [sg.Text('CARET Dir: '), sg.Input(Value.caret_dir, key=key_input_caret_dir, enable_events=True)],
                [sg.Text('App Dir: '), sg.Input(Value.app_dir, s=35, key=key_input_app_dir, enable_events=True),
                sg.Button('Check build', key=key_btn_check_build)],
                [sg.Text('Record (?)', tooltip=tooltip_record),
                sg.Text('REC (please stop recording before closing this app)', key=key_text_record, text_color='RED', visible=False)],
                [sg.Button('Start Recording (?)', key=key_btn_record),
                sg.Text('record frequency:'),
                sg.Input(Value.record_frequency, key=key_input_freq, s=8, enable_events=True),
                sg.Checkbox('Light mode', key=key_cb_light, default=Value.record_light, enable_events=True)],
                [sg.Button('!!! Reset (?)', key=key_btn_reset, tooltip=tooltip_reset)],
                [sg.HSep()],
                [sg.Text('Check')],
                [sg.Combo([], s=(60,1), enable_events=True, readonly=True, key=key_combo_target_trace_data)],
                [sg.Button('Trace data list (?)', key=key_btn_list, tooltip=tooltip_list),
                sg.Button('Check data lost (?)', key=key_btn_check_lost)],
                [sg.Text('Detailed checks (?)', tooltip='It will take time, so checking only for the first trial result will be enough.')],
                [sg.Button('check_ctf (?)', key=key_btn_check_ctf),
                sg.Button('trace_point (?)', key=key_btn_trace_point_summary),
                sg.Button('node_summary (?)', key=key_btn_node_summary),
                sg.Button('topic_summary (?)', key=key_btn_topic_summary)],
                [sg.HSep()],
                [sg.Text('Trace data file')],
                [sg.Button('Copy to local', key=key_btn_copy),
                sg.Checkbox("Only today's log", key=key_cb_copy_today, default=True),
                sg.Input(Value.copy_dir, key=key_input_copy_dir, s=30, tooltip=tooltip_copy_dir, enable_events=True)],
                [sg.Button('Upload', key=key_btn_upload)],
                [sg.HSep()],
                [sg.Text('Danger')],
                [sg.Button('!!! Remove all trace data', key=key_btn_remove),
                sg.Button('!!! Remove all copied trace data', key=key_btn_remove_copy)],
                [sg.HSep()],
                [sg.Text('Executing Command...', key=key_text_executing_cmd, text_color='RED', visible=False)],
                [sg.Multiline(size=(60,15), key=key_text_output, expand_x=True, expand_y=True, write_only=True,
                            reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True, autoscroll=True,  auto_refresh=True)],
            ]

    window = sg.Window('CARET Recorder', layout, resizable=True, finalize=True)

    @classmethod
    def get_value(cls, key: str):
        return Gui.window[key].get()

    @classmethod
    def update_value(cls, key: str, args: str):
        Gui.window[key].update(args)

    @classmethod
    def output_text(cls, text: str):
        cls.window[cls.key_text_output].update(text)
        cls.window.Refresh()

    @classmethod
    def update_executing_command(cls, is_executing: bool):
        for elem in cls.window.element_list():
            if elem.Type == sg.ELEM_TYPE_BUTTON:
                elem.update(disabled=is_executing)
        cls.window[cls.key_text_executing_cmd].update(visible=is_executing)
        cls.window.refresh()

    @classmethod
    def update_connection_components(cls):
        disable = cls.get_value(cls.key_cb_local)
        connection_keys = [cls.key_input_ip, cls.key_input_user, cls.key_input_password, cls.key_btn_test]
        for key in connection_keys:
            cls.window[key].update(disabled=disable)
        cls.window.refresh()

    @classmethod
    def update_record_components(cls, status: str):
        if status == 'starting':
            cls.window[cls.key_btn_record].update('Starting')
            cls.window[cls.key_text_record].update('Please wait until recording is started', visible=True)
            for elem in cls.window.element_list():
                if elem.Type == sg.ELEM_TYPE_BUTTON and elem != cls.window[cls.key_btn_record]:
                    elem.update(disabled=True)
        elif status == 'recording':
            cls.window[cls.key_btn_record].update('Stop Recording')
            cls.window[cls.key_text_record].update('REC (please stop recording before closing this app)', visible=True)
        elif status == 'stoping':
            cls.window[cls.key_btn_record].update('Stoping')
        elif status == 'not recording':
            cls.window[cls.key_btn_record].update('Start Recording')
            cls.window[cls.key_text_record].update(visible=False)
            for elem in cls.window.element_list():
                if elem.Type == sg.ELEM_TYPE_BUTTON and elem != cls.window[cls.key_btn_record]:
                    elem.update(disabled=False)
            cls.update_connection_components()
        else:
            print(f'coding error !!!! {status}')
        cls.window.refresh()


def get_record_cmd():
    freq = str(Value.record_frequency)
    if not str.isnumeric(freq):
        freq = 10000
    cmd = f'ros2 caret record -v -f {freq} {"--light" if Value.record_light else ""}'
    print(cmd)
    return cmd


def run_command_local(cmd: str):
    # proc = subprocess.run([cmd], executable='/bin/bash', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Gui.output_text(proc.stdout)
    # return proc.stdout
    proc = subprocess.Popen([cmd], executable='/bin/bash', shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = ''
    while True:
        buf = proc.stdout.readline()
        if buf == '':
            break
        text += buf
        # Gui.output_text(text)
        print(buf.strip())
    return text


def caret_record_local(no_wait=False):
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        get_record_cmd()
    Gui.update_record_components('starting')
    child = pexpect.spawn('/bin/bash', ['-c', cmd], logfile=sys.stdout, encoding='utf-8')
    time.sleep(0.1)
    child.sendline('')
    try:
        child.expect('press enter to stop')
    except:
        msg = f'Error: Please check if CARET is installed in {Value.caret_dir}'
        if not Value.is_local:
            msg = msg + ' in ' + Value.autoware_ecu_ip
        print(msg)
        sg.popup_error(msg)
        child.close()
        Gui.update_record_components('not recording')
        return False
    Gui.update_record_components('recording')
    while True:
        time.sleep(0.1)
        if no_wait:
            event = Gui.key_btn_record
        else:
            event, values = Gui.window.read()
        if event == Gui.key_btn_record:
            Gui.update_record_components('stoping')
            child.sendline('')
            child.expect('destroying tracing session')
            child.close()
            Gui.update_record_components('not recording')
            break
    return True


def get_connection():
    sess = pxssh.pxssh()
    try:
        sess.login(server=Value.autoware_ecu_ip,
                username=Value.user,
                password=Value.password)
    except:
        Gui.window[Gui.key_text_test].update('Error: Connection', text_color='RED')
        sg.popup_error('Connection Error')
        return None

    sess.sendline('source /opt/ros/humble/setup.bash')
    sess.prompt()
    res = sess.before.decode()
    if 'No such file' in res:
        Gui.window[Gui.key_text_test].update('Error: ROS not found', text_color='RED')
        return None

    sess.sendline(f'source {Value.caret_dir}/install/local_setup.bash')
    sess.prompt()
    res = sess.before.decode()
    if 'No such file' in res:
        Gui.window[Gui.key_text_test].update('Error: CARET not found', text_color='RED')
        return None

    Gui.window[Gui.key_text_test].update('OK', text_color='GREEN')

    return sess


def test_connection():
    _ = get_connection()


def caret_record_ssh(no_wait=False):
    Gui.update_record_components('starting')
    sess = get_connection()
    if sess is None:
        Gui.update_record_components('not recording')
        return False

    try:
        sess.sendline(get_record_cmd())
        if sess.expect(['press enter to start', 'error']) != 0:
            raise Exception
        print(sess.before.decode())
        print(sess.after.decode())
        sess.sendline('')
        sess.expect('press enter to stop')
        print(sess.before.decode())
        print(sess.after.decode())
    except:
        print(sess.before.decode())
        print(sess.after.decode())
        msg = f'Error: Please check if CARET is installed in {Value.caret_dir} in {Value.autoware_ecu_ip}'
        print(msg)
        sg.popup_error(msg)
        sess.close()
        Gui.update_record_components('not recording')
        return False
    Gui.update_record_components('recording')
    while True:
        time.sleep(0.1)
        if no_wait:
            event = Gui.key_btn_record
        else:
            event, values = Gui.window.read()
        if event == Gui.key_btn_record:
            Gui.update_record_components('stoping')
            sess.sendline('')
            sess.expect('destroying tracing session')
            print(sess.before.decode())
            print(sess.after.decode())
            sess.close()
            Gui.update_record_components('not recording')
            break
    return True


def run_command_ssh(cmd: str, timeout=30):
    sess = get_connection()
    if sess is None:
        return ''
    sess.sendline(cmd)
    ret = sess.prompt(timeout=timeout)
    if ret:
        res = sess.before.decode()
        res = res.splitlines()
        res = res[1:]    # ignore the first because it's the cmd
        res = [line for line in res if '\x1b' not in line]    # ignore escape sequence
        res = '\n'.join(res)
        print(res)
        return res
    else:
        sg.popup_error('Timeout')
        return ''


def run_command(cmd: str, timeout=30):
    Gui.update_executing_command(True)
    if Value.is_local:
        ret = run_command_local(cmd)
    else:
        ret = run_command_ssh(cmd, timeout)
    Gui.update_executing_command(False)
    return ret


def caret_record(no_wait=False):
    if Value.is_local:
        return caret_record_local(no_wait)
    else:
        return caret_record_ssh(no_wait)


def record():
    caret_record()
    print('Done')


def check_build():
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret check_caret_rclcpp -w {Value.app_dir}'
    Gui.output_text('')
    ret = run_command(cmd)
    if 'directory not found' in ret:
        sg.popup_error('Invalid "App Dir"')
    elif 'All packages are built using caret-rclcpp' in ret:
        sg.popup('All packages are built using caret-rclcpp')
    elif 'The following packages have not been built using caret-rclcpp:' in ret:
        sg.popup_error('Some packages have not been built using caret.\nIf many components(more than 10) are listed, you are using wrong workspace or you forgot enabling CARET when building.')
    else:
        sg.popup('Please check output text')


def get_trace_data_list():
    cmd = f'find {Value.trace_data_dir} -mindepth 1 -maxdepth 1 -type d | xargs ls -rt1d'
    trace_data_list = run_command(cmd)
    if len(trace_data_list) < 3:
        trace_data_list = []
    else:
        trace_data_list = trace_data_list.split()
    return trace_data_list


def reset():
    if sg.PopupYesNo('Do you really want to reset LTTng session?') != 'Yes':
        print('canceled')
        return
    cmd = 'ps aux | grep -e lttng -e "ros2 caret record" | grep -v grep | grep -v root | awk \'{ print "kill -9", $2 }\' | sh'
    if run_command(cmd) == '':
        return
    cmd = 'rm -rf ~/.lttng'
    run_command(cmd)
    if caret_record(True):
        trace_data_list = get_trace_data_list()
        if len(trace_data_list) > 0:
            latest_file = trace_data_list[-1]
            cmd = f'rm -rf {latest_file}'
            run_command(cmd)
    print('Done')


def trace_data_list():
    trace_data_list = get_trace_data_list()
    Gui.window[Gui.key_combo_target_trace_data].update(values=trace_data_list, value=trace_data_list[-1] if len(trace_data_list) > 0 else '')
    trace_data_list = [trace_data + '/ust' for trace_data in trace_data_list]
    Gui.output_text('')
    if len(trace_data_list) > 0:
        cmd = 'du -sh ' + ' '.join(trace_data_list)
        ret = run_command(cmd)

        if ret != '':
            list = ret.splitlines()
            latest = list[-1]
            latest_size = latest.split()[0]
            scale = 1
            scale = 1000 if 'K' in latest_size else 1000000 if 'M' in latest_size else 1000000000 if 'G' in latest_size else 1
            latest_size = latest_size.replace('K', '').replace('M', '').replace('G', '')
            try:
                latest_size = float(latest_size)
            except:
                latest_size = 0
            latest_size = latest_size * scale
            if latest_size == 0:
                sg.popup_error('Please check output')
            elif latest_size < 1000000:
                sg.popup_error('Click "Reset". File size is too small')
            else:
                sg.popup('OK')
    else:
        sg.popup('No trace data found')
    print('Done')


def check_lost():
    filename = Gui.get_value(Gui.key_combo_target_trace_data)
    if filename == '':
        sg.popup_error('Click "Trace data list" before checking')
        return

    cmd = f'babeltrace {filename} | wc -l'
    ret = run_command(cmd, Value.timeout_check)

    if 'Cannot open any trace for reading' in ret:
        sg.popup_error('Invalid filename')
    elif 'Tracer discarded' in ret:
        sg.popup_error('Confirm you applied caret_topic_filter.bash and "Light mode" is checked.\nDecrease the nubmer of "record frequency".')
    elif ret != '':
        sg.popup('OK')
    print('Done')


def get_number_from_summary(str, key, separator='|'):
    if len(str) == 0:
        return None
    line = [line.replace(' ', '') for line in str.splitlines() if key in line]
    if len(line) == 0:
        return None
    line = line[0].split(separator)
    if len(line) < 2:
        return None
    num = line[1]
    try:
        num = int(num)
    except:
        return None
    return num



def check_ctf():
    filename = Gui.get_value(Gui.key_combo_target_trace_data)
    if filename == '':
        sg.popup_error('Click "Trace data list" before checking')
        return
    if sg.PopupYesNo('Do you really want to run check_ctf? (It may take time)') != 'Yes':
        print('canceled')
        return
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret check_ctf -d {filename}'
    Gui.output_text('')
    ret = run_command(cmd, Value.timeout_check)

    lines_failed_to_load_node = [line for line in ret.splitlines() if 'Failed to load node' in line]
    lines_failed_to_load_node = [line for line in lines_failed_to_load_node if '/caret_trace' not in line]

    if 'FileNotFoundError' in ret or 'expected one argument' in ret:
        sg.popup_error('Invalid filename')
    elif 'Failed to find trace point added by caret-rclcpp' in ret:
        sg.popup_error('Confirm you are using correct WS and the WS is built with CARET.')
    elif 'Failed to find trace point added by LD_PRELOAD' in ret:
        sg.popup_error('Confirm you applied "export LD_PRELOAD=...".')
    elif 'Tracer discarded' in ret:
        sg.popup_error('Confirm you applied caret_topic_filter.bash and "Light mode" is checked.\nDecrease the nubmer of "record frequency".')
    elif len(lines_failed_to_load_node) > 0:
        sg.popup_error('Please restart Autoware.')
    elif 'Duplicate parameter callback found' in ret:
        sg.popup('Duplicate parameter callback found. It\'s caused by the target application code.')
    elif 'Failed to identify subscription' in ret:
        sg.popup('Failed to identify subscription. It\'s caused by the target application code.')
    elif 'Duplicated node name' in ret:
        sg.popup('Duplicated node name. It\'s caused by the target application code.')
    elif 'AssertionError' in ret:
        sg.popup_error('Unknown error')
    elif ret != '':
        sg.popup('OK')
    print('Done')


def trace_point_summary():
    filename = Gui.get_value(Gui.key_combo_target_trace_data)
    if filename == '':
        sg.popup_error('Click "Trace data list" before checking')
        return
    if sg.PopupYesNo('Do you really want to run trace_point_summary? (It may take time)') != 'Yes':
        print('canceled')
        return
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret trace_point_summary -d {filename}'
    Gui.output_text('')
    ret = run_command(cmd, Value.timeout_check)
    num = get_number_from_summary(ret, 'ros2:rclcpp_intra_publish')
    if num is None or num < 10:
        sg.popup_error('Confirm you are using correct WS and the WS is built with CARET.')
    else:
        sg.popup('OK')
    print('Done')


def node_summary():
    filename = Gui.get_value(Gui.key_combo_target_trace_data)
    if filename == '':
        sg.popup_error('Click "Trace data list" before checking')
        return
    if sg.PopupYesNo('Do you really want to run node_summary? (It may take time)') != 'Yes':
        print('canceled')
        return
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret node_summary -d {filename}'
    Gui.output_text('')
    ret =run_command(cmd, Value.timeout_check)
    num = get_number_from_summary(ret, 'ekf_localizer')
    if num is None or num < 10:
        sg.popup_error('Confirm you are using correct WS and the WS is built with CARET.')
    else:
        sg.popup('OK')
    print('Done')


def topic_summary():
    filename = Gui.get_value(Gui.key_combo_target_trace_data)
    if filename == '':
        sg.popup_error('Click "Trace data list" before checking')
        return
    if sg.PopupYesNo('Do you really want to run topic_summary? (It may take time)') != 'Yes':
        print('canceled')
        return
    cmd = f'source /opt/ros/humble/setup.bash &&' + \
        f'source {Value.caret_dir}/install/local_setup.bash &&' + \
        f'ros2 caret topic_summary -d {Gui.get_value(Gui.key_combo_target_trace_data)}'
    Gui.output_text('')
    ret = run_command(cmd, Value.timeout_check)
    num_clock = get_number_from_summary(ret, '/clock')
    num_tf = get_number_from_summary(ret, '/tf')
    if (num_clock is not None and num_clock > 10) or (num_tf is not None and num_tf > 10):
        sg.popup_error('Confirm you applied caret_topic_filter.bash.')
    else:
        sg.popup('OK')
    print('Done')


def copy_to_local():
    if sg.PopupYesNo('Do you really want to copy trace data?') != 'Yes':
        print('canceled')
        return

    run_command_local(f'mkdir -p {Value.copy_dir}')

    option = ''
    if Gui.get_value(Gui.key_cb_copy_today):
        option = '-newermt `date "+%Y-%m-%d"` ! -newermt `date "+%Y-%m-%d"`" 23:59:59.9999"'
    cmd = f'cd {Value.trace_data_dir} &&' + \
        f'find -name caret_converted | xargs -I [] rm [] &&' + \
        f'find ./ -maxdepth 1 -mindepth 1 -type d {option} | xargs -I[] tar czvf [].tgz []'
    if run_command(cmd) == '':
        return
    file_list = run_command(f'find {Value.trace_data_dir} -maxdepth 1 -mindepth 1 {option} -name "*.tgz"')
    if file_list == '':
        return
    file_list = file_list.splitlines()

    if Value.is_local:
        file_list = ' '.join(file_list)
        run_command(f'mv {file_list} {Value.copy_dir}/.')
    else:
        file_list = ','.join(file_list)
        copy_dir = run_command_local(f'realpath {Value.copy_dir}').strip()
        Gui.update_executing_command(True)
        if ',' in file_list:
            scp = pexpect.spawn(f'scp {Value.user}@{Value.autoware_ecu_ip}:\{{{file_list}\}} {copy_dir}/.', timeout=10*60)
        else:
            scp = pexpect.spawn(f'scp {Value.user}@{Value.autoware_ecu_ip}:{file_list} {copy_dir}/.')
        scp.expect('.ssword:*')
        scp.sendline(Value.password)
        scp.interact()
        Gui.update_executing_command(False)

    print('Done')


def upload():
    sg.Popup(f'Not yet implemented.\nPlease manually upload files in {Value.copy_dir}.')


def remove_trace_data():
    if sg.PopupYesNo('Do you really want to remove all trace data?') != 'Yes':
        print('canceled')
        return
    cmd = f'rm -rf {Value.trace_data_dir}/*'
    run_command(cmd)
    print('Done')


def remove_copied_trace_data():
    if sg.PopupYesNo('Do you really want to remove all copied trace data?') != 'Yes':
        print('canceled')
        return
    cmd = f'rm -rf {Value.copy_dir}/*'
    run_command_local(cmd)
    print('Done')


def main():
    Gui.update_connection_components()
    Gui.update_record_components('not recording')

    while True:
        event, values = Gui.window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == Gui.key_cb_local:
            Gui.update_connection_components()
        elif event == Gui.key_btn_test:
            test_connection()
        elif event == Gui.key_btn_check_build:
            check_build()
        elif event == Gui.key_btn_record:
            record()
        elif event == Gui.key_btn_reset:
            reset()
        elif event == Gui.key_btn_list:
            trace_data_list()
        elif event == Gui.key_btn_check_ctf:
            check_ctf()
        elif event == Gui.key_btn_check_lost:
            check_lost()
        elif event == Gui.key_btn_trace_point_summary:
            trace_point_summary()
        elif event == Gui.key_btn_node_summary:
            node_summary()
        elif event == Gui.key_btn_topic_summary:
            topic_summary()
        elif event == Gui.key_btn_copy:
            copy_to_local()
        elif event == Gui.key_btn_upload:
            upload()
        elif event == Gui.key_btn_remove:
            remove_trace_data()
        elif event == Gui.key_btn_remove_copy:
            remove_copied_trace_data()

        Value.is_local = values[Gui.key_cb_local]
        Value.autoware_ecu_ip = values[Gui.key_input_ip]
        Value.user = values[Gui.key_input_user]
        Value.password = values[Gui.key_input_password]
        Value.timeout_check = values[Gui.key_input_timeout_check]
        if str(Value.timeout_check).isnumeric():
            Value.timeout_check = int(Value.timeout_check)
        else:
            Value.timeout_check = 30
        Value.caret_dir = values[Gui.key_input_caret_dir]
        Value.app_dir = values[Gui.key_input_app_dir]
        Value.record_frequency = values[Gui.key_input_freq]
        Value.record_light = values[Gui.key_cb_light]
        Value.copy_dir = values[Gui.key_input_copy_dir]

    Gui.window.close()
    exit(0)


if __name__ == '__main__':
    main()
