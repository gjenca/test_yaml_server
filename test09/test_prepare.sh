if [ -d data ]
then 
	rm -r data
fi
mkdir data
cp data_copy_this/*.yaml data
chmod a-r data/*.yaml
