#!/bin/bash -e

# Add user and group: start
USER_ID=$(id -u)
GROUP_ID=$(id -g)

if [ x"$GROUP_ID" != x"0" ]; then
    groupadd -g "$GROUP_ID" "$USER_NAME"
fi

if [ x"$USER_ID" != x"0" ]; then
    useradd -d /home/"$USER_NAME" -m -s /bin/bash -u "$USER_ID" -g "$GROUP_ID" "$USER_NAME"
fi
export HOME=/home/"$USER_NAME"

sudo chmod u-s /usr/sbin/useradd
sudo chmod u-s /usr/sbin/groupadd
sudo pwconv
sudo sh -c "echo $USER_NAME:$USER_NAME | chpasswd"
# Add user and group: end

# Add to .bashrc for VSCode
# {
#     echo "source /opt/ros/humble/setup.bash"
#     echo "source /ros2_caret_ws/install/local_setup.bash"
#     echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash"
# } >>"$HOME"/.bashrc

sudo ssh-keygen -A
sudo /usr/sbin/sshd

exec "$@"
