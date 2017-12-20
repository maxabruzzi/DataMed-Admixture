#!/bin/bash

dataDir=/Users/maxabruzzi/Documents/Research/bioCADDIE/allGTarray/birdseed
metafile=/Users/maxabruzzi/Documents/Research/bioCADDIE/allGTarray/normalUniqueBdsdMeta.csv
plinkmapfile=/Users/maxabruzzi/Documents/Research/bioCADDIE/allGTarray/plink.map
scratchDir=/Users/maxabruzzi/Documents/Research/bioCADDIE/allGTarray/scratch
singlebirdseedcall=/Users/maxabruzzi/Documents/Research/bioCADDIE/allGTarray/scratch/singlebirdseedcall.txt
birdseedQueryOut=/Users/maxabruzzi/Documents/Research/bioCADDIE/allGTarray/scratch/birdseedQuery.out

[ -z $1 ] || dataDir=$1
birdseedfiles=$(find $dataDir -name "*.birdseed.data.txt")
for file in $birdseedfiles
do
	if [ -f $singlebirdseedcall ];
	then
		echo "Removing $singlebirdseedcall if it exists"
		rm $singlebirdseedcall
	fi
	
	dirname=$(dirname $file)
	
	fileID=$(echo $dirname | awk -F"/" '{print $NF}')

	echo "Copying $file to $singlebirdseedcall..."
	
	cp $file $singlebirdseedcall

	# Truncate the table so it is ready to be populated with new birdseed file
	
	mysql -h localhost -u mgr -pmgrpasswd diploid -e "truncate table singlebirdseedcall"	
	
	mysqlimport --fields-terminated-by='\t' --lines-terminated-by='\n' --verbose --local -u mgr -pmgrpasswd --ignore-lines=2 diploid $singlebirdseedcall

	if [ -f $birdseedQueryOut ];
	then
		echo "Removing $birdseedQueryOut if it exists"
		rm $birdseedQueryOut
	fi

	# Query to obtain the genotype call and output it to a file
	# This way involved permission issues as the file is written by mysql and not owned by the user
	#mysql -u mgr -pmgrpasswd diploid < $birdseedQuery

	# The following way creates file owned by user
	
	mysql -h localhost -u mgr -pmgrpasswd diploid -e "SELECT M.rsid, D.acgtCall, S.confidencescore FROM decodeintegercall AS D INNER JOIN map_probesetID_rsid AS M ON D.probesetID = M.probesetID INNER JOIN singlebirdseedcall AS S ON D.probesetID = S.probesetID AND D.intCall = S.intCall" > $birdseedQueryOut

	echo " The file to be converted is of file_id $fileID"

	# Run the python script to conver the output to ped file
	# Placeholder
	if [ -f $birdseedQueryOut ];
	then
		echo "The query output file is generated, now running python script to convert the query result to ped file."
		python sqlout2ped.py -i $birdseedQueryOut -f $fileID -o $scratchDir -m $metafile -p $plinkmapfile
		echo "Conversion completed, removing the query output file..." 
		rm $birdseedQueryOut
	fi
done
