#killall python3 2>/dev/null
if [ -e test_prepare.sh ]
then	
	echo '>>> Running test_prepare.sh'
	source test_prepare.sh
fi
echo '>>> Starting server'
python3 "$1"  >"$2" & 
PIDRIESENIE=$!
sleep 0.2
echo '>>> Running test.py'
python3 test.py
EXIT_STATUS=$?
echo '>>> Killing processes with rkill'
rkill $PIDRIESENIE 2>&1
echo '>>>' Killed server PID "$PIDRIESENIE"
wait $PIDRIESENIE 2>/dev/null
echo '>>> Checking with ps:' $(ps -p $PIDRIESENIE)
echo '>>> Test exit status:' "$EXIT_STATUS"
if [ -e test_cleanup.sh ]
then	
	echo '>>> Running test_cleanup.sh'
	source test_cleanup.sh
fi
echo '>>> Exitting test.sh'
exit $EXIT_STATUS
