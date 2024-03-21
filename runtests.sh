#!/bin/bash
# vim: et ts=4 sw=4 sta ai


MAKEOUT2="n"

if [ "$1" = '-a' ]; then
    MAKEOUT2="y"
    shift
fi


PATTERN="$2"

WHICH=""
if [ -n "$1" ]
then
    WHICH="_$1"
fi

./getsource.sh "$WHICH"
(
cat << THEEND
<!DOCTYPE html>
<html>
<head>
<meta encoding="utf-8">
<style>
.passed {
    color:green;
}
.failed {
    color:red;
}
</style>
</head>
<body>
<h1>Testy</h1>
<h2>
THEEND
date
cat << THEEND
</h2>
<table border="1">
THEEND


TESTS=`echo test??`

echo '<tr>'
echo '<th>*</th>'
for TEST in $TESTS; do
    echo '<th>' `(echo $TEST '+' ; cat $TEST/test.name )| sed 's/+/<br>/g'` '</th>'
    rm -r $TEST/results 2>/dev/null
    mkdir $TEST/results
done
echo '</tr>'
./riesenia"$WHICH".sh 2>/dev/null | grep "$PATTERN" |
while IFS=: read RIESENIE NAME ; do
    if [ "$NAME" == "" ]
    then
        NAME="noname"
    fi
    ERR=results/test_${NAME}.err
    OUT=results/test_${NAME}.txt 
    OUT2=results/test_${NAME}.serverout.txt 
    printf '%-20s' "${NAME}" > /dev/stderr
    echo '<tr>'
    echo '<th> <a href="source/'${NAME}'.html">'${NAME}'</a></th>'
    for TEST in $TESTS; do
        cd $TEST
        bash test.sh ../$RIESENIE ${OUT2} 2>${ERR} >${OUT}
        EXIT_STATUS=$?
        echo '<td>'
        if [ "$EXIT_STATUS" == "0" ]
        then
            CLASS='passed'
            MARK='✓'
            COLOR="$(tput setaf 2)"
        else
            CLASS='failed'
            MARK='X'
            COLOR="$(tput setaf 1)"
        fi
        printf "${COLOR}%s$(tput sgr0)" ${MARK} >/dev/stderr
        echo '<span class="'$CLASS'">'$MARK'</span>'
        echo '<a href="'$TEST/${OUT}'">&gt;&gt;</a>'
        if [ "$MAKEOUT2" == "y" ]; then
            echo '<a href="'$TEST/${OUT2}'">stdout&gt;&gt;</a>'
        fi
        if [ ! -s ${ERR} ]; then
            printf '_' > /dev/stderr
	    	rm ${ERR}
        else
            printf '!' >/dev/stderr
            echo '<a href="'$TEST/${ERR}'">err&gt;&gt;</a>'
	    fi
        echo '</td>'
        cd ..
        #killall python 2>/dev/null
        #killall python3 2>/dev/null
    done
    printf '\n' > /dev/stderr
    echo '</tr>'
done
cat <<THEEND
</table>
</body>
</html>
THEEND
) > results.html

