#!/bin/bash

exec() {
	runner="/bin/python3 /etc/desktops/src/detect-config.py"

	echo "$@"

	echo "detecting config..."
	$runner --detect
	
	current=$(head -1 /etc/desktops/current)
	current_path=$(tail -1 /etc/desktops/current)
	
	if [[ $current == "" ]];
	then
		echo "no config found! "
		exit 0
	fi
	
	echo "$current config found"
	script="${current_path}/root-launch.sh"
	
	if test -f $script;
	then
		echo "starting root script for config $current..."
		echo "$EUID"
		bash -c $script
	else 
		echo "no root launch script found for ${current}! "
	fi

	if [[ "$@" =~ "--apply" ]] && [[ "$@" =~ "--user=" ]];
	then
		user=0
		for ARG in "$@"; do
			if [[ $ARG =~ "--user=" ]];
			then
				user=${ARG:7:4}
				break
			fi
		done

		echo "applying user config for user $user"
		sudo --user=\#$user $runner --apply
	fi
}

if ! [ "$EUID" -eq 0 ];
then
	echo "please run this script as root! "
	
	if ! [[ "$@" =~ "--nosudo" ]];
	then
		echo "automatically attempting sudo..."
		sudo "$0" "$@" "--user=$EUID"
	fi
	exit 1
fi

exec "$@" 2>&1 | tee /etc/desktops/latest.log
