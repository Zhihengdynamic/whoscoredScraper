# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 10:33:14 2016

@author: JK
"""
import os
import csv

def write_to_disk(data, name, rowwise = False):
    filename = name + ".txt"
    text_file = open(filename, "wb")
    for row in data:
        text_file.write("%s\r\n" % row)

    text_file.close()

def open_from_disk(name):
    filename = name + '.txt'
    output = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as openfile:
            reader = csv.reader(openfile, delimiter='\n')
            for row in reader:
                output.append(row[0])
        return output
    else:
        print 'File ' + filename + ' does not exist!'
        return []
        
    
def write_to_csv(path, data, append = False):
    # preparing data
    outputDic = []
    if type(data[0]) is dict:
        fieldnames = data[0].keys()
        outputDic = data
    else:
        fieldnames = data[0][0].keys()
        for day in data:
            for player in day:
                outputDic.append(player)
    # appending data to existing csv file
    if append:
        with open(path, "ab") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', 
                                    fieldnames=fieldnames, lineterminator='\n')
            for row in outputDic:
                writer.writerow(row)
    # make new csv file
    else:
        with open(path, "wb") as out_file:
            writer = csv.DictWriter(out_file, 
                                    delimiter=',', fieldnames=fieldnames)
            writer.writeheader()
            for row in outputDic:
                writer.writerow(row)
    out_file.close()
    
def open_from_csv(filename, firstrowHeader = True, path = './'):
    output= []
    headerRow = True
    with open(path + filename + '.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            if row == []:
                continue
            if firstrowHeader:
                if headerRow:
                    headers = row
                    headerRow = False
                else:                    
                    output.append(dict(zip(headers, row)))
            else:
                output.append(row)               
    return output
    
    
