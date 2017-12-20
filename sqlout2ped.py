# Convert the sql query output file into .ped file that can be processed by plink

# 1. The caseMetafile which contains the metadata of the cases. The gender and file_id, case_id are the ones being used in the code
# This file is highly customized csv file (colon delimited), the field names dependent on how you retrieve them from the dgc portal or other means
# You will need to update the getCaseGenderDict() to tailor your application. eg. caseMetafile = "/Users/maxabruzzi/Documents/Research/bioCADDIE/allGTarray/..."

# 2. The rsid_snp_map.file, this file is the .map file for plink, simply obtained from birdsuite METADATADIR (removing the extra AFFY_SNP_...ones)

# 3. The birdseed fileID, this is going to be used to retrieve the caseID and the gender information

# 4. The plink map file. It contains all the rsids in an order that is going to be converted

# 5. The sql output file directory

# This directory contains the output file generated by the sql query that retrieves all the genotypes of a call
#An example run is:

#python sqlout2ped.py -i queryoutput -f $fileID -o outputdir -m metafile -p birdSeed.map

# Author: Xiaojun Max Xu
# Date: 06/26/2017

import os, sys, getopt, re, csv

def getrsidOrder(plinkmapfile):  # Read the rsids from the .map file into a list according to the order of them in the map file
    rsidOrder=[]
    with open(plinkmapfile,'r') as infile:
        for line in infile:
            rsid = line.split()[1]
            rsidOrder.append(rsid)
    return rsidOrder
            
def getfileCaseGenderDict(metafile):
    fileCaseGenderDict = {}
    with open(metafile) as csvfile:
        reader = csv.DictReader(csvfile, delimiter = ',')
        for row in reader:
            if row['file_id'] not in fileCaseGenderDict:
                fileCaseGenderDict[row['file_id']] = (row['case_id'], (1 if row['gender'] == 'male' else 2))
    return fileCaseGenderDict

def getRsid(line):
    return line.split("\t")[0]

def getGenotype(line):
    genotypeString = line.split("\t")[1]
    return genotypeString[0] + ' ' + genotypeString[1]

def getConfidenceScore(line):
    non_decimal = re.compile(r'[^\d.]+')
#     print(non_decimal.sub('', line.split("\t")[2]))
    return float(non_decimal.sub('', line.split("\t")[2]))

def getRsidGenoDict(inputfile):
    residGenoDict = {}
    with open(inputfile) as infile:
        header = infile.readline()
        for line in infile:
            resid = getRsid(line)
            confidence = getConfidenceScore(line)
            genotype = getGenotype(line)
            if (resid not in residGenoDict) and (confidence < 0.1):
                residGenoDict[resid] = genotype
    return residGenoDict

def main(argv):
    birdseedfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:f:o:m:p:",["inputfile=","fileID=","outputdir=","metafile=","plinkmapfile="])
    except getopt.GetoptError:
        print('sqlout2ped.py -i <inputfile> -f <fileID> -o <outputdir> -m <metafile> -p <plinkmapfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('sqlout2ped.py -i <inputfile> -f <fileID> -o <outputdir> -m <metafile> -p <plinkmapfile>')
            sys.exit()
        elif opt in ("-i", "--inputfile"):
            inputfile = arg
        elif opt in ("-f", "--fileID"):
            fileID = arg
        elif opt in ("-o", "--outputfiledir"):
            outputfileDirectory = arg
        elif opt in ("-m", "--metafile"):
            caseMetafile = arg
        elif opt in ("-p", "--plinkmapfile"):
            plinkMapfile = arg    
    
    rsidList = getrsidOrder(plinkMapfile)
    rsidGenoDict = getRsidGenoDict(inputfile)
    fileCaseGenderDict = getfileCaseGenderDict(caseMetafile)
#     print(fileCaseGenderDict[fileID])

    caseID = fileCaseGenderDict[fileID][0]
    genderCode = fileCaseGenderDict[fileID][1]
    
    
    outputfile = outputfileDirectory + '/' + caseID + '.ped'
    with open(outputfile, 'w') as outfile:
        print("Converting " + caseID + " query output to .ped file, outputs to directory " + outputfileDirectory)
        # write the first 6 columns: FAM_ID, IND_ID, FATHER_ID (0), MOTHER_ID(0), SEX, PHENO(0)
        #population study, no family relations; all cancer cases, therefore, the phenotype does not concern
        outfile.write(caseID + '\t' + caseID + '\t' + '0' + '\t' + '0' + '\t' + str(genderCode) + '\t' + '0' + '\t')
        
        for rsid in rsidList:
            try:
#                 print(rsidGenoDict[rsid] + '\t')
                outfile.write(rsidGenoDict[rsid] + '\t')
                #print on each line for debug or sanity check
#                 outfile.write(rsid + '\t' + rsidGenoDict[rsid] + '\n')
            except:
                outfile.write('0' + ' ' + '0' + '\t')
                #print on each line for debug or sanity check
#                 outfile.write(rsid + '\t' + '0' + ' ' + '0' + '\n')               
                
                
if __name__ == "__main__":
    main(sys.argv[1:])